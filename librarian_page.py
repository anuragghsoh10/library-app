import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os


from add_book import add_book_window
from issue_book import issue_book_window
from view_books import view_books_window
from issued_books import issued_books_window
from view_requests import view_requests_window


def logout(win):

    confirm = messagebox.askyesno("Logout", "Do you want to logout?")

    if confirm:
        win.destroy()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        login_path = os.path.join(current_dir, "login.py")

        subprocess.Popen([sys.executable, login_path])


def create_card(parent, text, command):

    # shadow layer
    shadow = tk.Frame(parent, bg="#d0d3d4")
    shadow.grid_propagate(False)

    card = tk.Frame(
        shadow,
        bg="white",
        width=220,
        height=130,
        bd=0,
        relief="flat"
    )

    card.pack(padx=4, pady=4)
    card.pack_propagate(False)

    label = tk.Label(
        card,
        text=text,
        font=("Segoe UI", 14, "bold"),
        bg="white"
    )

    label.pack(expand=True)

    def on_enter(e):
        card.config(bg="#3498db")
        label.config(bg="#3498db", fg="white")
        shadow.config(bg="#bfc9ca")
        card.config(cursor="hand2")

    def on_leave(e):
        card.config(bg="white")
        label.config(bg="white", fg="black")
        shadow.config(bg="#d0d3d4")

    shadow.bind("<Enter>", on_enter)
    shadow.bind("<Leave>", on_leave)

    card.bind("<Enter>", on_enter)
    card.bind("<Leave>", on_leave)

    label.bind("<Enter>", on_enter)
    label.bind("<Leave>", on_leave)

    shadow.bind("<Button-1>", lambda e: command())
    card.bind("<Button-1>", lambda e: command())
    label.bind("<Button-1>", lambda e: command())

    return shadow

def librarian_page(username, role):

    win = tk.Tk()
    win.title("Librarian Dashboard")
    win.geometry("1000x600")

    sidebar = tk.Frame(win, bg="#2c3e50", width=220)
    sidebar.pack(side="left", fill="y")

    content = tk.Frame(win, bg="#ecf0f1")
    content.pack(side="right", expand=True, fill="both")

    def clear_content():
        for widget in content.winfo_children():
            widget.destroy()

    def show_page(page_func):
        clear_content()
        page_func(content)

    def show_dashboard():
        clear_content()

        tk.Label(
            content,
            text="Library Librarian Dashboard",
            font=("Segoe UI",22,"bold"),
            bg="#ecf0f1"
        ).pack(pady=20)

        card_frame = tk.Frame(content,bg="#ecf0f1")
        card_frame.pack()

        cards = [
            ("📚 Add Book", lambda: show_page(add_book_window)),
            ("📖 Issue Book", lambda: show_page(issue_book_window)),
            ("🔍 View Books", lambda: show_page(view_books_window)),
            ("📋 Issued Books", lambda: show_page(issued_books_window)),
            ("📩 Book Requests", lambda: show_page(view_requests_window))
        ]

        col=0
        row=0

        for text,cmd in cards:

            card=create_card(card_frame,text,cmd)
            card.grid(row=row,column=col,padx=20,pady=20)

            col+=1
            if col==3:
                col=0
                row+=1

    tk.Label(
        sidebar,
        text=f"Librarian\n{username}",
        bg="#2c3e50",
        fg="white",
        font=("Segoe UI",16,"bold")
    ).pack(pady=30)

    btn_style = {
    "width":20,
    "bg":"#34495e",
    "fg":"white",
    "font":("Segoe UI",11),
    "bd":0
}

    buttons = []

    def activate(btn):

        for b in buttons:
            b.config(bg="#34495e")

        btn.config(bg="#1abc9c")


    btn0 = tk.Button(sidebar,text="🏠 Dashboard",**btn_style,
                    command=lambda:[activate(btn0),show_dashboard()])
    btn0.pack(pady=5)

    btn1 = tk.Button(sidebar,text="📚 Add Book",**btn_style,
                    command=lambda:[activate(btn1),show_page(add_book_window)])
    btn1.pack(pady=5)

    btn2 = tk.Button(sidebar,text="📖 Issue Book",**btn_style,
                    command=lambda:[activate(btn2),show_page(issue_book_window)])
    btn2.pack(pady=5)

    btn3 = tk.Button(sidebar,text="🔍 View Books",**btn_style,
                    command=lambda:[activate(btn3),show_page(view_books_window)])
    btn3.pack(pady=5)

    btn4 = tk.Button(sidebar,text="📋 Issued Books",**btn_style,
                    command=lambda:[activate(btn4),show_page(issued_books_window)])
    btn4.pack(pady=5)

    btn5 = tk.Button(sidebar,text="📩 Book Requests",**btn_style,
                    command=lambda:[activate(btn5),show_page(view_requests_window)])
    btn5.pack(pady=5)

    buttons = [btn0,btn1,btn2,btn3,btn4,btn5]

    tk.Button(
        sidebar,
        text="🚪 Logout",
        bg="red",
        fg="white",
        command=lambda: logout(win)
    ).pack(side="bottom", pady=20)

    # Show dashboard by default
    show_dashboard()

    win.mainloop()