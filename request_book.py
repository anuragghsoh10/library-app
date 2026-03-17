import tkinter as tk
from tkinter import ttk
from database import connect_db


def request_book_window(parent, username):

    global tree,status

    tree=ttk.Treeview(parent,columns=("ID","Title","Author","Qty"),show="headings")

    for col in ("ID","Title","Author","Qty"):
        tree.heading(col,text=col)

    tree.pack(fill="both",expand=True)

    conn=connect_db()
    cur=conn.cursor()

    cur.execute("SELECT * FROM books")
    rows=cur.fetchall()

    for row in rows:
        tree.insert("",tk.END,values=row)

    conn.close()

    def send_request(book_id, uname):

        conn = connect_db()
        cur = conn.cursor()

        # Check if already issued
        cur.execute(
            "SELECT * FROM issued_books WHERE book_id=%s AND student_name=%s",
            (book_id,uname)
        )

        if cur.fetchone():
            status.config(text="⚠ You already borrowed this book", fg="red")
            conn.close()
            return

        # Check if request already exists
        cur.execute(
            "SELECT * FROM book_requests WHERE book_id=%s AND username=%s AND status='pending'",
            (book_id,uname)
        )

        if cur.fetchone():
            status.config(text="⚠ Request already pending", fg="red")
            conn.close()
            return

        # Check quantity
        cur.execute("SELECT quantity FROM books WHERE book_id=%s",(book_id,))
        result = cur.fetchone()

        if result[0] <= 0:
            status.config(text="❌ Book not available", fg="red")
            conn.close()
            return

        # Insert request
        cur.execute(
            "INSERT INTO book_requests(book_id,username,status) VALUES(%s,%s,'pending')",
            (book_id,uname)
        )

        conn.commit()
        conn.close()

        status.config(text="✅ Request Sent", fg="green")

    def request_selected():

        selected=tree.focus()
        data=tree.item(selected,"values")

        send_request(data[0],username)


    tk.Button(parent,text="📩 Request Book",command=request_selected).pack(pady=10)
    status=tk.Label(parent)
    status.pack()