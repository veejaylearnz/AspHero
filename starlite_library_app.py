import os
from dataclasses import asdict
from typing import Dict, List, Optional

from pydantic import BaseModel
from starlite import MediaType, Response, Starlite, get, post

from library_management_system import Book, Library, Member, PostgresPool

library: Optional[Library] = None


def get_db_config() -> Dict[str, str]:
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": os.getenv("PGPORT", "5432"),
        "dbname": os.getenv("PGDATABASE", "library_db"),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "admin"),
    }


class BookCreate(BaseModel):
    title: str
    author: str
    year: int
    copies: int = 1


class MemberCreate(BaseModel):
    name: str
    email: str


class BorrowRequest(BaseModel):
    member_id: int
    book_id: int


def book_to_dict(book: Book) -> Dict[str, object]:
    return asdict(book)


def member_to_dict(member: Member) -> Dict[str, object]:
    return asdict(member)


@get("/", media_type=MediaType.HTML)
def index() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Library Management UI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 24px; }
        section { border: 1px solid #ddd; padding: 16px; margin-bottom: 20px; border-radius: 8px; }
        h1, h2 { margin-top: 0; }
        label { display: block; margin: 8px 0 4px; }
        input, button { padding: 8px; width: 100%; max-width: 420px; box-sizing: border-box; }
        button { width: auto; margin-top: 8px; }
        pre { background: #f4f4f4; padding: 12px; border-radius: 6px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>Library Management System</h1>
    <section>
        <h2>Books</h2>
        <button onclick="refreshBooks()">Refresh book list</button>
        <pre id="books">Loading books...</pre>
        <h3>Add Book</h3>
        <label>Title</label>
        <input id="book-title" type="text" placeholder="Book title" />
        <label>Author</label>
        <input id="book-author" type="text" placeholder="Author" />
        <label>Year</label>
        <input id="book-year" type="number" placeholder="Publication year" />
        <label>Copies</label>
        <input id="book-copies" type="number" value="1" min="1" />
        <button onclick="createBook()">Create book</button>
    </section>
    <section>
        <h2>Members</h2>
        <button onclick="refreshMembers()">Refresh member list</button>
        <pre id="members">Loading members...</pre>
        <h3>Register Member</h3>
        <label>Name</label>
        <input id="member-name" type="text" placeholder="Member name" />
        <label>Email</label>
        <input id="member-email" type="email" placeholder="Member email" />
        <button onclick="createMember()">Register member</button>
    </section>
    <section>
        <h2>Borrow / Return</h2>
        <label>Member ID</label>
        <input id="borrow-member-id" type="number" placeholder="Member ID" />
        <label>Book ID</label>
        <input id="borrow-book-id" type="number" placeholder="Book ID" />
        <button onclick="borrowBook()">Borrow book</button>
        <button onclick="returnBook()">Return book</button>
        <pre id="borrow-result"></pre>
    </section>
    <script>
        async function refreshBooks() {
            const response = await fetch('/api/books');
            const books = await response.json();
            document.getElementById('books').textContent = books.length ? JSON.stringify(books, null, 2) : 'No books available.';
        }

        async function refreshMembers() {
            const response = await fetch('/api/members');
            const members = await response.json();
            document.getElementById('members').textContent = members.length ? JSON.stringify(members, null, 2) : 'No members registered.';
        }

        async function createBook() {
            const title = document.getElementById('book-title').value.trim();
            const author = document.getElementById('book-author').value.trim();
            const year = parseInt(document.getElementById('book-year').value, 10);
            const copies = parseInt(document.getElementById('book-copies').value, 10);
            const response = await fetch('/api/books', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, author, year, copies })
            });
            const result = await response.json();
            document.getElementById('borrow-result').textContent = JSON.stringify(result, null, 2);
            refreshBooks();
        }

        async function createMember() {
            const name = document.getElementById('member-name').value.trim();
            const email = document.getElementById('member-email').value.trim();
            const response = await fetch('/api/members', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email })
            });
            const result = await response.json();
            document.getElementById('borrow-result').textContent = JSON.stringify(result, null, 2);
            refreshMembers();
        }

        async function borrowBook() {
            const member_id = parseInt(document.getElementById('borrow-member-id').value, 10);
            const book_id = parseInt(document.getElementById('borrow-book-id').value, 10);
            const response = await fetch('/api/borrow', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ member_id, book_id })
            });
            const result = await response.json();
            document.getElementById('borrow-result').textContent = JSON.stringify(result, null, 2);
            refreshBooks();
            refreshMembers();
        }

        async function returnBook() {
            const member_id = parseInt(document.getElementById('borrow-member-id').value, 10);
            const book_id = parseInt(document.getElementById('borrow-book-id').value, 10);
            const response = await fetch('/api/return', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ member_id, book_id })
            });
            const result = await response.json();
            document.getElementById('borrow-result').textContent = JSON.stringify(result, null, 2);
            refreshBooks();
            refreshMembers();
        }

        refreshBooks();
        refreshMembers();
    </script>
</body>
</html>
"""


@get("/api/books")
def api_list_books() -> List[Dict[str, object]]:
    if library is None:
        raise RuntimeError("Library is not initialized")
    return [book_to_dict(book) for book in library.list_books()]


@get("/api/books/{book_id:int}")
def api_book_detail(book_id: int) -> Optional[Dict[str, object]]:
    if library is None:
        raise RuntimeError("Library is not initialized")
    book = library.book_info(book_id)
    return book_to_dict(book) if book else None


@post("/api/books")
def api_create_book(data: BookCreate) -> Dict[str, object]:
    if library is None:
        raise RuntimeError("Library is not initialized")
    book = library.add_book(data.title, data.author, data.year, data.copies)
    return book_to_dict(book)


@get("/api/members")
def api_list_members() -> List[Dict[str, object]]:
    if library is None:
        raise RuntimeError("Library is not initialized")
    return [member_to_dict(member) for member in library.list_members()]


@get("/api/members/{member_id:int}")
def api_member_detail(member_id: int) -> Optional[Dict[str, object]]:
    if library is None:
        raise RuntimeError("Library is not initialized")
    member = library.member_info(member_id)
    return member_to_dict(member) if member else None


@post("/api/members")
def api_create_member(data: MemberCreate) -> Dict[str, object]:
    if library is None:
        raise RuntimeError("Library is not initialized")
    member = library.register_member(data.name, data.email)
    return member_to_dict(member)


@post("/api/borrow")
def api_borrow_book(data: BorrowRequest) -> Dict[str, str]:
    if library is None:
        raise RuntimeError("Library is not initialized")
    return {"message": library.borrow_book(data.member_id, data.book_id)}


@post("/api/return")
def api_return_book(data: BorrowRequest) -> Dict[str, str]:
    if library is None:
        raise RuntimeError("Library is not initialized")
    return {"message": library.return_book(data.member_id, data.book_id)}


async def on_startup() -> None:
    global library
    config = get_db_config()
    db = PostgresPool(minconn=1, maxconn=10, **config)
    library = Library(db)


async def on_shutdown() -> None:
    if library is not None:
        library.db.close_all()


app = Starlite(
    route_handlers=[
        index,
        api_list_books,
        api_book_detail,
        api_create_book,
        api_list_members,
        api_member_detail,
        api_create_member,
        api_borrow_book,
        api_return_book,
    ],
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("starlite_library_app:app", host="127.0.0.1", port=8000, reload=True)
