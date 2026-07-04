# Library Management System

# Library catalog - list of dictionaries
books = [
    {"id": 1, "title": "Python Basics", "author": "John Smith", "available": True, "copies": 3},
    {"id": 2, "title": "Data Science Guide", "author": "Jane Doe", "available": True, "copies": 2},
    {"id": 3, "title": "Web Development", "author": "Bob Johnson", "available": False, "copies": 0},
    {"id": 4, "title": "Machine Learning", "author": "Alice Brown", "available": True, "copies": 1},
]

# Members dictionary
members = {
    "M001": {"name": "Tom Wilson", "email": "tom@email.com", "borrowed_books": [1]},
    "M002": {"name": "Sarah Lee", "email": "sarah@email.com", "borrowed_books": [3]},
    "M003": {"name": "Mike Davis", "email": "mike@email.com", "borrowed_books": []},
}

# Borrow a book
def borrow_book(member_id, book_id):
    if member_id in members and any(b["id"] == book_id for b in books):
        book = next(b for b in books if b["id"] == book_id)
        if book["available"] and book["copies"] > 0:
            members[member_id]["borrowed_books"].append(book_id)
            book["copies"] -= 1
            if book["copies"] == 0:
                book["available"] = False
            return f"Book borrowed successfully!"
    return "Book not available or member not found."

# Return a book
def return_book(member_id, book_id):
    if member_id in members and book_id in members[member_id]["borrowed_books"]:
        book = next(b for b in books if b["id"] == book_id)
        members[member_id]["borrowed_books"].remove(book_id)
        book["copies"] += 1
        book["available"] = True
        return "Book returned successfully!"
    return "Invalid return request."

# Display available books
def show_available_books():
    print("\nAvailable Books:")
    for book in books:
        if book["available"]:
            print(f"  {book['id']}. {book['title']} by {book['author']} ({book['copies']} copies)")

# Test operations
print(borrow_book("M001", 2))
show_available_books()
print(return_book("M001", 1))
