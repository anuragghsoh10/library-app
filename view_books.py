import tkinter as tk
from tkinter import ttk
from database import connect_db


def view_books_window(parent):

    global tree,search_entry

    tk.Label(
        parent,text="📚 Library Books",
        bg="#2c3e50",
        fg="white",
        font=("Segoe UI",18,"bold"),
        pady=10
    ).pack(fill="x")

    frame=tk.Frame(parent,bg="#ecf0f1")
    frame.pack(pady=10)

    search_entry=ttk.Entry(frame,width=25)
    search_entry.pack(side="left",padx=5)

    def search_books():

        keyword=search_entry.get()

        conn=connect_db()
        cur=conn.cursor()

        cur.execute("SELECT * FROM books WHERE title LIKE %s",("%"+keyword+"%",))
        rows=cur.fetchall()

        for r in tree.get_children():
            tree.delete(r)

        for row in rows:
            tree.insert("",tk.END,values=row)

        conn.close()

    tk.Button(frame,text="🔍 Search",command=search_books).pack(side="left")

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