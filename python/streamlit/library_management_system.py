import os
import threading
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor


@dataclass
class Book:
    id: int
    title: str
    author: str
    year: int
    copies: int


@dataclass
class Member:
    id: int
    name: str
    email: str
    borrowed_books: List[int] = field(default_factory=list)


class PostgresPool:
    def __init__(self, minconn: int, maxconn: int, **connection_kwargs):
        self.pool = pool.ThreadedConnectionPool(minconn, maxconn, **connection_kwargs)
        self.lock = threading.Lock()

    def close_all(self) -> None:
        self.pool.closeall()

    @contextmanager
    def connection(self):
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    def execute(self, query: str, params: tuple = (), commit: bool = False, fetchone: bool = False, fetchall: bool = False):
        with self.connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if commit:
                    conn.commit()
                if fetchone:
                    return cursor.fetchone()
                if fetchall:
                    return cursor.fetchall()


class Library:
    def __init__(self, db: PostgresPool):
        self.db = db
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        create_books = """
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER NOT NULL,
                copies INTEGER NOT NULL CHECK (copies >= 0)
            )
        """

        create_members = """
            CREATE TABLE IF NOT EXISTS members (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """

        create_borrowed = """
            CREATE TABLE IF NOT EXISTS borrowed_books (
                member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
                book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                borrowed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (member_id, book_id)
            )
        """

        self.db.execute(create_books, commit=True)
        self.db.execute(create_members, commit=True)
        self.db.execute(create_borrowed, commit=True)

    def add_book(self, title: str, author: str, year: int, copies: int = 1) -> Book:
        row = self.db.execute(
            "INSERT INTO books (title, author, year, copies) VALUES (%s, %s, %s, %s) RETURNING id, title, author, year, copies",
            (title, author, year, copies),
            commit=True,
            fetchone=True,
        )
        return Book(**row)

    def remove_book(self, book_id: int) -> bool:
        deleted = self.db.execute("DELETE FROM books WHERE id = %s RETURNING id", (book_id,), commit=True, fetchone=True)
        return deleted is not None

    def search_books(self, term: str) -> List[Book]:
        rows = self.db.execute(
            "SELECT id, title, author, year, copies FROM books WHERE title ILIKE %s OR author ILIKE %s ORDER BY id",
            (f"%{term}%", f"%{term}%"),
            fetchall=True,
        )
        return [Book(**row) for row in rows] if rows else []

    def list_books(self) -> List[Book]:
        rows = self.db.execute(
            "SELECT id, title, author, year, copies FROM books ORDER BY id",
            fetchall=True,
        )
        return [Book(**row) for row in rows] if rows else []

    def register_member(self, name: str, email: str) -> Member:
        row = self.db.execute(
            "INSERT INTO members (name, email) VALUES (%s, %s) RETURNING id, name, email",
            (name, email),
            commit=True,
            fetchone=True,
        )
        return Member(id=row["id"], name=row["name"], email=row["email"])

    def list_members(self) -> List[Member]:
        rows = self.db.execute("SELECT id, name, email FROM members ORDER BY id", fetchall=True)
        members = [Member(id=row["id"], name=row["name"], email=row["email"]) for row in rows] if rows else []
        for member in members:
            member.borrowed_books = self._borrowed_book_ids(member.id)
        return members

    def _borrowed_book_ids(self, member_id: int) -> List[int]:
        rows = self.db.execute(
            "SELECT book_id FROM borrowed_books WHERE member_id = %s ORDER BY book_id",
            (member_id,),
            fetchall=True,
        )
        return [row["book_id"] for row in rows] if rows else []

    def borrow_book(self, member_id: int, book_id: int) -> str:
        with self.db.connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                try:
                    cursor.execute("BEGIN")
                    cursor.execute("SELECT id, copies FROM books WHERE id = %s FOR UPDATE", (book_id,))
                    book = cursor.fetchone()
                    if not book:
                        conn.rollback()
                        return "Book not found."

                    cursor.execute("SELECT id FROM members WHERE id = %s", (member_id,))
                    member = cursor.fetchone()
                    if not member:
                        conn.rollback()
                        return "Member not found."

                    cursor.execute(
                        "SELECT 1 FROM borrowed_books WHERE member_id = %s AND book_id = %s",
                        (member_id, book_id),
                    )
                    if cursor.fetchone():
                        conn.rollback()
                        return "Member already borrowed this book."

                    if book["copies"] < 1:
                        conn.rollback()
                        return "No copies available to borrow."

                    cursor.execute(
                        "UPDATE books SET copies = copies - 1 WHERE id = %s",
                        (book_id,),
                    )
                    cursor.execute(
                        "INSERT INTO borrowed_books (member_id, book_id) VALUES (%s, %s)",
                        (member_id, book_id),
                    )
                    conn.commit()
                    return f"Member {member_id} borrowed book {book_id}."
                except Exception as exc:
                    conn.rollback()
                    return f"Failed to borrow book: {exc}"

    def return_book(self, member_id: int, book_id: int) -> str:
        with self.db.connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                try:
                    cursor.execute("BEGIN")
                    cursor.execute(
                        "SELECT 1 FROM borrowed_books WHERE member_id = %s AND book_id = %s",
                        (member_id, book_id),
                    )
                    if not cursor.fetchone():
                        conn.rollback()
                        return "This book is not borrowed by the member."

                    cursor.execute(
                        "UPDATE books SET copies = copies + 1 WHERE id = %s",
                        (book_id,),
                    )
                    cursor.execute(
                        "DELETE FROM borrowed_books WHERE member_id = %s AND book_id = %s",
                        (member_id, book_id),
                    )
                    conn.commit()
                    return f"Member {member_id} returned book {book_id}."
                except Exception as exc:
                    conn.rollback()
                    return f"Failed to return book: {exc}"

    def member_info(self, member_id: int) -> Optional[Member]:
        row = self.db.execute(
            "SELECT id, name, email FROM members WHERE id = %s",
            (member_id,),
            fetchone=True,
        )
        if not row:
            return None
        borrowed_books = self._borrowed_book_ids(member_id)
        return Member(id=row["id"], name=row["name"], email=row["email"], borrowed_books=borrowed_books)

    def book_info(self, book_id: int) -> Optional[Book]:
        row = self.db.execute(
            "SELECT id, title, author, year, copies FROM books WHERE id = %s",
            (book_id,),
            fetchone=True,
        )
        return Book(**row) if row else None

    def simulate_concurrent_borrow(self, member_id: int, book_id: int, threads: int = 5) -> None:
        def worker(task_id: int) -> None:
            result = self.borrow_book(member_id, book_id)
            print(f"[Thread {task_id}] {result}")

        with ThreadPoolExecutor(max_workers=threads) as executor:
            for task_id in range(1, threads + 1):
                executor.submit(worker, task_id)


def prompt_with_default(prompt_text: str, default: str) -> str:
    value = input(f"{prompt_text} [{default}]: ").strip()
    return value if value else default


def build_db_config() -> Dict[str, str]:
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    database = os.getenv("PGDATABASE", "library_db")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "admin")

    print("Postgres connection settings")
    host = prompt_with_default("Host", host)
    port = prompt_with_default("Port", port)
    database = prompt_with_default("Database", database)
    user = prompt_with_default("User", user)
    password = prompt_with_default("Password", password)

    return {
        "host": host,
        "port": port,
        "dbname": database,
        "user": user,
        "password": password,
    }


def show_menu() -> None:
    print("\n=== Library Management System ===")
    print("1. Add book")
    print("2. Remove book")
    print("3. Search books")
    print("4. List books")
    print("5. Register member")
    print("6. List members")
    print("7. Borrow book")
    print("8. Return book")
    print("9. Member details")
    print("10. Book details")
    print("11. Simulate concurrent borrow")
    print("0. Exit")


def prompt_int(message: str, default: Optional[int] = None) -> int:
    while True:
        raw = input(message).strip()
        if raw == "" and default is not None:
            return default
        if raw.isdigit():
            return int(raw)
        print("Please enter a valid integer.")


def prompt_nonempty(message: str) -> str:
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Value cannot be empty.")


def main() -> None:
    config = build_db_config()
    db = PostgresPool(minconn=1, maxconn=10, **config)
    library = Library(db)

    try:
        while True:
            show_menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                title = prompt_nonempty("Book title: ")
                author = prompt_nonempty("Author: ")
                year = prompt_int("Publication year: ")
                copies = prompt_int("Number of copies: ", default=1)
                book = library.add_book(title, author, year, copies)
                print(f"Added book [{book.id}] '{book.title}' by {book.author}.")

            elif choice == "2":
                book_id = prompt_int("Book ID to remove: ")
                print("Book removed." if library.remove_book(book_id) else "Book not found.")

            elif choice == "3":
                term = prompt_nonempty("Search by title or author: ")
                books = library.search_books(term)
                if not books:
                    print("No books found.")
                else:
                    for book in books:
                        print(f"[{book.id}] {book.title} by {book.author} ({book.year}) - copies: {book.copies}")

            elif choice == "4":
                books = library.list_books()
                if not books:
                    print("No books available.")
                else:
                    for book in books:
                        print(f"[{book.id}] {book.title} by {book.author} ({book.year}) - copies: {book.copies}")

            elif choice == "5":
                name = prompt_nonempty("Member name: ")
                email = prompt_nonempty("Member email: ")
                member = library.register_member(name, email)
                print(f"Registered member [{member.id}] {member.name}.")

            elif choice == "6":
                members = library.list_members()
                if not members:
                    print("No registered members.")
                else:
                    for member in members:
                        borrowed = ", ".join(str(book_id) for book_id in member.borrowed_books) or "none"
                        print(f"[{member.id}] {member.name} <{member.email}> - borrowed: {borrowed}")

            elif choice == "7":
                member_id = prompt_int("Member ID: ")
                book_id = prompt_int("Book ID: ")
                print(library.borrow_book(member_id, book_id))

            elif choice == "8":
                member_id = prompt_int("Member ID: ")
                book_id = prompt_int("Book ID: ")
                print(library.return_book(member_id, book_id))

            elif choice == "9":
                member_id = prompt_int("Member ID: ")
                member = library.member_info(member_id)
                if not member:
                    print("Member not found.")
                else:
                    borrowed = ", ".join(str(book_id) for book_id in member.borrowed_books) or "none"
                    print(f"[{member.id}] {member.name} <{member.email}> - borrowed: {borrowed}")

            elif choice == "10":
                book_id = prompt_int("Book ID: ")
                book = library.book_info(book_id)
                if not book:
                    print("Book not found.")
                else:
                    print(f"[{book.id}] {book.title} by {book.author} ({book.year}) - copies: {book.copies}")

            elif choice == "11":
                member_id = prompt_int("Member ID for concurrent borrow: ")
                book_id = prompt_int("Book ID to borrow concurrently: ")
                threads = prompt_int("Number of simultaneous borrow attempts: ", default=5)
                library.simulate_concurrent_borrow(member_id, book_id, threads=threads)

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid option, please try again.")
    finally:
        db.close_all()


if __name__ == "__main__":
    main()
