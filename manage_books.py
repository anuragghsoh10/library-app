import tkinter as tk
from tkinter import ttk
from database import connect_db


def manage_books_window(parent):

    global id_entry,qty_entry,status,tree

    tk.Label(
        parent,text="⚙ Manage Books",
        bg="#2c3e50",
        fg="white",
        font=("Segoe UI",18,"bold"),
        pady=10
    ).pack(fill="x")

    tree=ttk.Treeview(parent,columns=("ID","Title","Author","Qty"),show="headings")

    for col in ("ID","Title","Author","Qty"):
        tree.heading(col,text=col)

    tree.pack(fill="both",expand=True,padx=10,pady=10)

    def load_books():

        for r in tree.get_children():
            tree.delete(r)

        conn=connect_db()
        cur=conn.cursor()

        cur.execute("SELECT * FROM books")
        rows=cur.fetchall()

        for row in rows:
            tree.insert("",tk.END,values=row)

        conn.close()

    load_books()

    frame=tk.Frame(parent,bg="#ecf0f1")
    frame.pack()

    tk.Label(frame,text="Book ID").grid(row=0,column=0)
    id_entry=ttk.Entry(frame,width=10)
    id_entry.grid(row=0,column=1,padx=5)

    tk.Label(frame,text="Quantity").grid(row=0,column=2)
    qty_entry=ttk.Entry(frame,width=10)
    qty_entry.grid(row=0,column=3,padx=5)

    def delete_book():

        book_id=id_entry.get()

        conn=connect_db()
        cur=conn.cursor()

        cur.execute("DELETE FROM books WHERE book_id=%s",(book_id,))
        conn.commit()
        conn.close()

        status.config(text="🗑 Book Deleted",fg="green")
        load_books()

    def update_book():

        book_id=id_entry.get()
        qty=qty_entry.get()

        conn=connect_db()
        cur=conn.cursor()

        cur.execute(
            "UPDATE books SET quantity=%s WHERE book_id=%s",
            (qty,book_id)
        )

        conn.commit()
        conn.close()

        status.config(text="✅ Quantity Updated",fg="green")
        load_books()

    tk.Button(frame,text="✏ Update",bg="#3498db",fg="white",command=update_book).grid(row=0,column=4,padx=5)

    tk.Button(frame,text="🗑 Delete",bg="red",fg="white",command=delete_book).grid(row=0,column=5,padx=5)

    status=tk.Label(parent,bg="#ecf0f1")
    status.pack()