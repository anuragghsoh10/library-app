import tkinter as tk
from tkinter import ttk
from database import connect_db


def return_book_window(parent, username):

    global tree, status, current_user

    current_user = username

    tk.Label(
        parent,
        text="🔄 Return Your Books",
        bg="#2c3e50",
        fg="white",
        font=("Segoe UI", 18, "bold"),
        pady=10
    ).pack(fill="x")

    columns = ("Issue ID", "Book ID", "User", "Date")

    tree = ttk.Treeview(parent, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_books(uname):

        for r in tree.get_children():
            tree.delete(r)

        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT issue_id, book_id, student_name, issue_date FROM issued_books WHERE student_name=%s",
            (uname,)
        )

        rows = cur.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        conn.close()

    def return_book():

        selected = tree.focus()

        if not selected:
            status.config(text="Select a book", fg="red")
            return

        data = tree.item(selected, "values")

        issue_id = data[0]
        book_id = data[1]

        conn = connect_db()
        cur = conn.cursor()

        # delete issued record
        cur.execute("DELETE FROM issued_books WHERE issue_id=%s", (issue_id,))

        # increase quantity
        cur.execute(
            "UPDATE books SET quantity = quantity + 1 WHERE book_id=%s",
            (book_id,)
        )

        conn.commit()
        conn.close()

        status.config(text="✅ Book Returned", fg="green")

        load_books(current_user)

    tk.Button(
        parent,
        text="🔄 Return Selected Book",
        bg="#3498db",
        fg="white",
        command=return_book
    ).pack(pady=10)

    status = tk.Label(parent)
    status.pack()


    load_books(username)