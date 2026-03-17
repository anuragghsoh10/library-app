import tkinter as tk
from tkinter import ttk
from database import connect_db


def issued_books_window(parent):

    global tree

    tk.Label(
        parent,text="📚 Issued Books",
        bg="#2c3e50",
        fg="white",
        font=("Segoe UI",18,"bold"),
        pady=10
    ).pack(fill="x")

    tree=ttk.Treeview(parent,columns=("IssueID","BookID","Student","Date"),show="headings")

    for col in ("IssueID","BookID","Student","Date"):
        tree.heading(col,text=col)

    tree.pack(fill="both",expand=True,padx=10,pady=10)

    def load_books():

        for r in tree.get_children():
            tree.delete(r)

        conn=connect_db()
        cur=conn.cursor()

        cur.execute("SELECT * FROM issued_books")
        rows=cur.fetchall()

        for row in rows:
            tree.insert("",tk.END,values=row)

        conn.close()

    tk.Button(parent,text="🔄 Refresh",command=load_books).pack(pady=5)

    load_books()