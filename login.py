import tkinter as tk
from database import connect_db
from admin_page import admin_page
from librarian_page import librarian_page
from user_page import user_page


def login():

    username = user_entry.get()
    password = pass_entry.get()
    role = role_var.get()

    conn = connect_db()
    cur = conn.cursor()

    query = "SELECT * FROM users WHERE username=%s AND password=%s AND role=%s"
    cur.execute(query,(username,password,role))

    result = cur.fetchone()
    conn.close()

    if result:

        root.destroy()

        if role == "admin":
            admin_page(username,role)

        elif role == "librarian":
            librarian_page(username,role)

        else:
            user_page(username,role)

    else:
        status_label.config(text="Invalid Login",fg="red")


# ----- REGISTER PART (unchanged) -----

def register():

    username = reg_user.get()
    password = reg_pass.get()
    role = reg_role.get()

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users(username,password,role) VALUES(%s,%s,%s)",
        (username,password,role)
    )

    conn.commit()
    conn.close()

    reg_status.config(text="Registration Successful",fg="green")


def register_window():

    global reg_user,reg_pass,reg_role,reg_status

    reg_win = tk.Toplevel()
    reg_win.title("Register")
    reg_win.geometry("350x300")
    reg_win.configure(bg="black")

    tk.Label(reg_win,text="Register User",
             font=("Arial",20,"bold"),
             bg="black",fg="white").pack(pady=15)

    tk.Label(reg_win,text="Username",bg="black",fg="white").pack()
    reg_user=tk.Entry(reg_win)
    reg_user.pack()

    tk.Label(reg_win,text="Password",bg="black",fg="white").pack()
    reg_pass=tk.Entry(reg_win,show="*")
    reg_pass.pack()

    tk.Label(reg_win,text="Role",bg="black",fg="white").pack()

    reg_role=tk.StringVar()
    reg_role.set("user")

    tk.OptionMenu(reg_win,reg_role,"admin","librarian","user").pack()

    tk.Button(reg_win,text="Register",
              bg="#99ccff",width=15,
              command=register).pack(pady=10)

    reg_status=tk.Label(reg_win,bg="black")
    reg_status.pack()


root=tk.Tk()
root.title("Library Login")
root.geometry("400x350")
root.configure(bg="black")

tk.Label(root,text="Library Login",
         font=("Arial",26,"bold"),
         bg="black",fg="white").pack(pady=20)

tk.Label(root,text="Username",bg="black",fg="white").pack()
user_entry=tk.Entry(root)
user_entry.pack()

tk.Label(root,text="Password",bg="black",fg="white").pack()
pass_entry=tk.Entry(root,show="*")
pass_entry.pack()

tk.Label(root,text="Role",bg="black",fg="white").pack()

role_var=tk.StringVar()
role_var.set("user")

tk.OptionMenu(root,role_var,"admin","librarian","user").pack()

tk.Button(root,text="Login",
          font=("Arial",12,"bold"),
          width=15,bg="#99ccff",
          command=login).pack(pady=10)

tk.Button(root,text="Register",
          font=("Arial",12,"bold"),
          width=15,bg="#b3ffb3",
          command=register_window).pack()

status_label=tk.Label(root,bg="black")
status_label.pack()


root.mainloop()

