import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional

DATA_FILE = Path(__file__).parent / "library_data.json"

@dataclass
class Book:
    id: int
    title: str
    author: str
    year: int
    copies: int = 1

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Book":
        return cls(**data)

@dataclass
class Member:
    id: int
    name: str
    email: str
    borrowed_books: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Member":
        return cls(**data)

class Library:
    def __init__(self) -> None:
        self.books: Dict[int, Book] = {}
        self.members: Dict[int, Member] = {}
        self.next_book_id = 1
        self.next_member_id = 1
        self.load()

    def load(self) -> None:
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.books = {int(k): Book.from_dict(v) for k, v in data.get("books", {}).items()}
                self.members = {int(k): Member.from_dict(v) for k, v in data.get("members", {}).items()}
                self.next_book_id = data.get("next_book_id", self.next_book_id)
                self.next_member_id = data.get("next_member_id", self.next_member_id)

    def save(self) -> None:
        data = {
            "books": {book_id: book.to_dict() for book_id, book in self.books.items()},
            "members": {member_id: member.to_dict() for member_id, member in self.members.items()},
            "next_book_id": self.next_book_id,
            "next_member_id": self.next_member_id,
        }
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def add_book(self, title: str, author: str, year: int, copies: int = 1) -> Book:
        book = Book(id=self.next_book_id, title=title, author=author, year=year, copies=copies)
        self.books[self.next_book_id] = book
        self.next_book_id += 1
        self.save()
        return book

    def remove_book(self, book_id: int) -> bool:
        if book_id in self.books:
            del self.books[book_id]
            self.save()
            return True
        return False

    def search_books(self, term: str) -> List[Book]:
        lower_term = term.lower()
        return [book for book in self.books.values() if lower_term in book.title.lower() or lower_term in book.author.lower()]

    def list_books(self) -> List[Book]:
        return sorted(self.books.values(), key=lambda book: book.id)

    def register_member(self, name: str, email: str) -> Member:
        member = Member(id=self.next_member_id, name=name, email=email)
        self.members[self.next_member_id] = member
        self.next_member_id += 1
        self.save()
        return member

    def list_members(self) -> List[Member]:
        return sorted(self.members.values(), key=lambda member: member.id)

    def borrow_book(self, member_id: int, book_id: int) -> str:
        if member_id not in self.members:
            return "Member not found."
        if book_id not in self.books:
            return "Book not found."

        member = self.members[member_id]
        book = self.books[book_id]

        if book.copies < 1:
            return "No copies available to borrow."

        if book_id in member.borrowed_books:
            return "Member already borrowed this book."

        book.copies -= 1
        member.borrowed_books.append(book_id)
        self.save()
        return f"{member.name} borrowed '{book.title}'."

    def return_book(self, member_id: int, book_id: int) -> str:
        if member_id not in self.members:
            return "Member not found."
        if book_id not in self.books:
            return "Book not found."

        member = self.members[member_id]
        book = self.books[book_id]

        if book_id not in member.borrowed_books:
            return "This book is not borrowed by the member."

        member.borrowed_books.remove(book_id)
        book.copies += 1
        self.save()
        return f"{member.name} returned '{book.title}'."

    def member_info(self, member_id: int) -> Optional[Member]:
        return self.members.get(member_id)

    def book_info(self, book_id: int) -> Optional[Book]:
        return self.books.get(book_id)

def prompt_int(message: str) -> int:
    while True:
        user_input = input(message).strip()
        if user_input.isdigit():
            return int(user_input)
        print("Please enter a valid integer.")

def prompt_nonempty(message: str) -> str:
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Value cannot be empty.")

def show_menu() -> None:
    print("\nLibrary Management System")
    print("1. Add book")
    print("2. Remove book")
    print("3. Search books")
    print("4. List books")
    print("5. Register member")
    print("6. List members")
    print("7. Borrow book")
    print("8. Return book")
    print("9. Member details")
    print("0. Exit")

def run() -> None:
    library = Library()
    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            title = prompt_nonempty("Book title: ")
            author = prompt_nonempty("Author: ")
            year = prompt_int("Publication year: ")
            copies = prompt_int("Number of copies: ")
            book = library.add_book(title, author, year, copies)
            print(f"Added book [{book.id}] '{book.title}' by {book.author}.")

        elif choice == "2":
            book_id = prompt_int("Book ID to remove: ")
            if library.remove_book(book_id):
                print("Book removed.")
            else:
                print("Book not found.")

        elif choice == "3":
            term = prompt_nonempty("Search by title or author: ")
            found = library.search_books(term)
            if not found:
                print("No books found.")
            else:
                for book in found:
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

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    run()
