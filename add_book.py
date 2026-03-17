import tkinter as tk
from tkinter import ttk
from database import connect_db


def add_book_window(parent):

    global title_entry,author_entry,qty_entry,status

    tk.Label(
        parent,text="📚 Add New Book",
        bg="#2c3e50",
        fg="white",
        font=("Segoe UI",18,"bold"),
        pady=10
    ).pack(fill="x")

    frame=tk.Frame(parent,bg="white",bd=2,relief="ridge")
    frame.place(relx=0.5,rely=0.55,anchor="center",width=300,height=200)

    tk.Label(frame,text="Title",bg="white").pack(pady=5)
    title_entry=ttk.Entry(frame,width=25)
    title_entry.pack()

    tk.Label(frame,text="Author",bg="white").pack(pady=5)
    author_entry=ttk.Entry(frame,width=25)
    author_entry.pack()

    tk.Label(frame,text="Quantity",bg="white").pack(pady=5)
    qty_entry=ttk.Entry(frame,width=25)
    qty_entry.pack()

    def add_book():

        title = title_entry.get()
        author = author_entry.get()
        qty = qty_entry.get()

        if not title or not author or not qty:
            status.config(text="Fill all fields", fg="red")
            return

        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO books(title,author,quantity) VALUES(%s,%s,%s)",
            (title,author,qty)
        )

        conn.commit()
        conn.close()

        status.config(text="✅ Book Added Successfully", fg="green")

        title_entry.delete(0,tk.END)
        author_entry.delete(0,tk.END)
        qty_entry.delete(0,tk.END)

    tk.Button(
        frame,text="➕ Add Book",
        bg="#3498db",
        fg="white",
        width=15,
        command=add_book
    ).pack(pady=10)


    status=tk.Label(frame,bg="white")
    status.pack()