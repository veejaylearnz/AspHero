##Asphero Project: Library Management System with PostgreSQL Backend and Streamlit UI
import os

import streamlit as st

from library_management_system import Library, PostgresPool


def get_db_config() -> dict:
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": os.getenv("PGPORT", "5432"),
        "dbname": os.getenv("PGDATABASE", "library_db"),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "admin"),
    }


@st.cache_resource
def get_library(host: str, port: str, dbname: str, user: str, password: str) -> Library:
    connection_config = {
        "host": host,
        "port": port,
        "dbname": dbname,
        "user": user,
        "password": password,
    }
    db = PostgresPool(minconn=1, maxconn=10, **connection_config)
    return Library(db)


def render_books_tab(library: Library) -> None:
    st.header("Books")
    search_term = st.text_input("Search books by title or author")

    with st.expander("Search / Filter"):
        if search_term:
            books = library.search_books(search_term)
            if books:
                st.success(f"Found {len(books)} books matching '{search_term}'.")
            else:
                st.warning("No matching books found.")
        else:
            books = library.list_books()

        st.dataframe([
            {
                "ID": book.id,
                "Title": book.title,
                "Author": book.author,
                "Year": book.year,
                "Copies": book.copies,
            }
            for book in books
        ] or [])

    with st.form("add_book_form"):
        st.subheader("Add a new book")
        title = st.text_input("Title")
        author = st.text_input("Author")
        year = st.number_input("Publication year", min_value=0, value=2024, step=1)
        copies = st.number_input("Number of copies", min_value=1, value=1, step=1)
        add_submitted = st.form_submit_button("Add Book")
        if add_submitted:
            if title and author:
                book = library.add_book(title, author, int(year), int(copies))
                st.success(f"Added book [{book.id}] {book.title} by {book.author}.")
            else:
                st.error("Please provide both title and author.")

    with st.form("remove_book_form"):
        st.subheader("Remove a book")
        remove_book_id = st.number_input("Book ID", min_value=1, value=1, step=1)
        remove_submitted = st.form_submit_button("Remove Book")
        if remove_submitted:
            removed = library.remove_book(int(remove_book_id))
            if removed:
                st.success(f"Book {remove_book_id} removed.")
            else:
                st.error("Book not found.")


def render_members_tab(library: Library) -> None:
    st.header("Members")

    with st.expander("Member list"):
        members = library.list_members()
        st.dataframe([
            {
                "ID": member.id,
                "Name": member.name,
                "Email": member.email,
                "Borrowed Books": ", ".join(str(book_id) for book_id in member.borrowed_books) or "None",
            }
            for member in members
        ] or [])

    with st.form("register_member_form"):
        st.subheader("Register a new member")
        member_name = st.text_input("Name")
        member_email = st.text_input("Email")
        register_submitted = st.form_submit_button("Register Member")
        if register_submitted:
            if member_name and member_email:
                member = library.register_member(member_name, member_email)
                st.success(f"Registered member [{member.id}] {member.name}.")
            else:
                st.error("Please enter both name and email.")

    with st.form("member_details_form"):
        st.subheader("Member details")
        member_id = st.number_input("Member ID", min_value=1, value=1, step=1)
        details_submitted = st.form_submit_button("Show Member")
        if details_submitted:
            member = library.member_info(int(member_id))
            if member:
                st.write("**Name:**", member.name)
                st.write("**Email:**", member.email)
                st.write("**Borrowed Books:**", ", ".join(str(book_id) for book_id in member.borrowed_books) or "None")
            else:
                st.error("Member not found.")


def render_borrowing_tab(library: Library) -> None:
    st.header("Borrowing")

    with st.form("borrow_form"):
        st.subheader("Borrow a book")
        borrow_member_id = st.number_input("Member ID", min_value=1, value=1, step=1, key="borrow_member")
        borrow_book_id = st.number_input("Book ID", min_value=1, value=1, step=1, key="borrow_book")
        borrow_submitted = st.form_submit_button("Borrow Book")
        if borrow_submitted:
            message = library.borrow_book(int(borrow_member_id), int(borrow_book_id))
            if message.startswith("Member"):
                st.success(message)
            else:
                st.error(message)

    with st.form("return_form"):
        st.subheader("Return a book")
        return_member_id = st.number_input("Member ID", min_value=1, value=1, step=1, key="return_member")
        return_book_id = st.number_input("Book ID", min_value=1, value=1, step=1, key="return_book")
        return_submitted = st.form_submit_button("Return Book")
        if return_submitted:
            message = library.return_book(int(return_member_id), int(return_book_id))
            if message.startswith("Member"):
                st.success(message)
            else:
                st.error(message)

    with st.form("concurrent_borrow_form"):
        st.subheader("Simulate concurrent borrowing")
        concurrent_member_id = st.number_input("Member ID", min_value=1, value=1, step=1, key="concurrent_member")
        concurrent_book_id = st.number_input("Book ID", min_value=1, value=1, step=1, key="concurrent_book")
        threads = st.number_input("Number of concurrent attempts", min_value=1, value=3, step=1)
        simulate_submitted = st.form_submit_button("Simulate")
        if simulate_submitted:
            st.info("Running concurrent borrow simulation in background logs...")
            library.simulate_concurrent_borrow(int(concurrent_member_id), int(concurrent_book_id), threads=int(threads))
            st.success("Concurrent borrow simulation completed. Check terminal output for details.")


def render_details_tab(library: Library) -> None:
    st.header("Quick lookups")

    with st.form("book_details_form"):
        st.subheader("Book details")
        detail_book_id = st.number_input("Book ID", min_value=1, value=1, step=1, key="detail_book")
        details_submitted = st.form_submit_button("Show Book")
        if details_submitted:
            book = library.book_info(int(detail_book_id))
            if book:
                st.write("**Title:**", book.title)
                st.write("**Author:**", book.author)
                st.write("**Year:**", book.year)
                st.write("**Available Copies:**", book.copies)
            else:
                st.error("Book not found.")

    st.write("---")
    st.subheader("Last books and members")
    columns = st.columns(2)
    with columns[0]:
        st.write("**Books**")
        st.write(len(library.list_books()))
    with columns[1]:
        st.write("**Members**")
        st.write(len(library.list_members()))


def main() -> None:
    st.set_page_config(page_title="Library Management", layout="wide")
    st.title("Library Management System")
    st.write("Use this UI to manage books, members, borrowing, and returns with a PostgreSQL backend.")

    with st.sidebar:
        st.header("Database connection")
        config = get_db_config()
        host = st.text_input("Host", value=config["host"])
        port = st.text_input("Port", value=config["port"])
        dbname = st.text_input("Database", value=config["dbname"])
        user = st.text_input("User", value=config["user"])
        password = st.text_input("Password", value=config["password"], type="password")
        st.markdown("---")
        st.write("The app uses a cached connection and the library service is initialized automatically.")

    try:
        library = get_library(host, port, dbname, user, password)
    except Exception as exc:
        st.error(f"Unable to connect to PostgreSQL backend: {exc}")
        return

    tabs = st.tabs(["Books", "Members", "Borrowing", "Quick lookups"])
    with tabs[0]:
        render_books_tab(library)
    with tabs[1]:
        render_members_tab(library)
    with tabs[2]:
        render_borrowing_tab(library)
    with tabs[3]:
        render_details_tab(library)


if __name__ == "__main__":
    main()
