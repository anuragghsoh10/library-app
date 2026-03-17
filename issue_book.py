import tkinter as tk
from tkinter import ttk
from database import connect_db
from datetime import date


def issue_book_window(parent):

    global book_entry,student_entry,status

    tk.Label(
        parent,text="📖 Issue Book",
        bg="#2c3e50",
        fg="white",
        font=("Segoe UI",18,"bold"),
        pady=10
    ).pack(fill="x")

    frame=tk.Frame(parent,bg="white",bd=2,relief="ridge")
    frame.place(relx=0.5,rely=0.6,anchor="center",width=300,height=180)

    tk.Label(frame,text="Book ID",bg="white").pack(pady=5)
    book_entry=ttk.Entry(frame,width=25)
    book_entry.pack()

    tk.Label(frame,text="Student Name",bg="white").pack(pady=5)
    student_entry=ttk.Entry(frame,width=25)
    student_entry.pack()

    def issue_book():

        book_id = book_entry.get()
        student = student_entry.get()

        if not book_id or not student:
            status.config(text="Enter all fields", fg="red")
            return

        conn = connect_db()
        cur = conn.cursor()

        # Check quantity
        cur.execute("SELECT quantity FROM books WHERE book_id=%s",(book_id,))
        result = cur.fetchone()

        if not result:
            status.config(text="❌ Book not found",fg="red")
            conn.close()
            return

        qty = result[0]

        if qty <= 0:
            status.config(text="❌ Book Out of Stock",fg="red")
            conn.close()
            return

        # Issue book
        cur.execute(
            "INSERT INTO issued_books(book_id,student_name,issue_date) VALUES(%s,%s,CURDATE())",
            (book_id,student)
        )

        # Reduce quantity
        cur.execute(
            "UPDATE books SET quantity = quantity - 1 WHERE book_id=%s",
            (book_id,)
        )

        conn.commit()
        conn.close()

        status.config(text="✅ Book Issued",fg="green")

    tk.Button(
        frame,text="📖 Issue",
        bg="#3498db",
        fg="white",
        command=issue_book
    ).pack(pady=10)


    status=tk.Label(frame,bg="white")
    status.pack()