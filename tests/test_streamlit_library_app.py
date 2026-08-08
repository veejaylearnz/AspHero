import sys
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit_library_app as module


class DummyLibrary:
    def list_books(self):
        return [SimpleNamespace(id=1, title="Dune", author="Frank Herbert", year=1965, copies=2)]

    def add_book(self, title, author, year, copies):
        return SimpleNamespace(id=2, title=title, author=author, year=year, copies=copies)

    def register_member(self, name, email):
        return SimpleNamespace(id=1, name=name, email=email, borrowed_books=[])

    def borrow_book(self, member_id, book_id):
        return f"Member {member_id} borrowed book {book_id}."

    def return_book(self, member_id, book_id):
        return f"Member {member_id} returned book {book_id}."


def test_health_and_book_listing(monkeypatch):
    monkeypatch.setattr(module, "get_library", lambda: DummyLibrary())

    client = TestClient(module.app)

    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}

    books_response = client.get("/books")
    assert books_response.status_code == 200
    assert books_response.json()[0]["title"] == "Dune"
