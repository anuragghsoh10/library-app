import tkinter as tk
from tkinter import ttk
from database import connect_db


def view_requests_window(parent):

    global tree

    tree=ttk.Treeview(parent,columns=("ID","Book","User","Status"),show="headings")

    for col in ("ID","Book","User","Status"):
        tree.heading(col,text=col)

    tree.pack(fill="both",expand=True)

    def load_requests():

        for r in tree.get_children():
            tree.delete(r)

        conn=connect_db()
        cur=conn.cursor()

        cur.execute("SELECT * FROM book_requests")
        rows=cur.fetchall()

        for row in rows:
            tree.insert("",tk.END,values=row)

        conn.close()

    load_requests()

    def approve_request(request_id, book_id, username):

        conn = connect_db()
        cur = conn.cursor()

        # Check quantity
        cur.execute("SELECT quantity FROM books WHERE book_id=%s",(book_id,))
        result = cur.fetchone()

        if result[0] <= 0:
            print("Book Out of Stock")
            conn.close()
            return

        # Issue book
        cur.execute(
            "INSERT INTO issued_books(book_id,student_name) VALUES(%s,%s)",
            (book_id,username)
        )

        # Reduce quantity
        cur.execute(
            "UPDATE books SET quantity=quantity-1 WHERE book_id=%s",
            (book_id,)
        )

        # Update request status
        cur.execute(
            "UPDATE book_requests SET status='approved' WHERE request_id=%s",
            (request_id,)
        )

        conn.commit()
        conn.close()

        load_requests()

    def reject_request(request_id):

        conn=connect_db()
        cur=conn.cursor()

        cur.execute(
            "UPDATE book_requests SET status='rejected' WHERE request_id=%s",
            (request_id,)
        )

        conn.commit()
        conn.close()

        load_requests()

    def approve():

        selected=tree.focus()
        data=tree.item(selected,"values")

        approve_request(data[0],data[1],data[2])

    def reject():

        selected=tree.focus()
        data=tree.item(selected,"values")

        reject_request(data[0])

    frame=tk.Frame(parent)
    frame.pack(pady=10)

    tk.Button(frame,text="✅ Approve",bg="green",fg="white",command=approve).pack(side="left",padx=10)
    tk.Button(frame,text="❌ Reject",bg="red",fg="white",command=reject).pack(side="left",padx=10)