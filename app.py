from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import connect_db
from functools import wraps

app = Flask(__name__)
app.secret_key = "library_secret_key_2026"


# --- Auth Decorator ---

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("role") not in roles:
                flash("Access denied", "error")
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated
    return decorator


# --- Auth Routes ---

@app.route("/")
def index():
    if "username" in session:
        role = session["role"]
        if role == "admin":
            return redirect(url_for("admin_dashboard"))
        elif role == "librarian":
            return redirect(url_for("librarian_dashboard"))
        else:
            return redirect(url_for("user_dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s AND role=%s",
            (username, password, role)
        )
        result = cur.fetchone()
        conn.close()

        if result:
            session["username"] = username
            session["role"] = role
            if role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif role == "librarian":
                return redirect(url_for("librarian_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid login credentials", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users(username,password,role) VALUES(%s,%s,%s)",
                (username, password, role)
            )
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except:
            flash("Registration failed. Username may already exist.", "error")
        finally:
            conn.close()

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))


# --- Admin Dashboard ---

@app.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM books")
    total_books = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM issued_books")
    issued_books = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM book_requests WHERE status='pending'")
    pending_requests = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    conn.close()

    return render_template("admin_dashboard.html",
                           total_books=total_books,
                           issued_books=issued_books,
                           pending_requests=pending_requests,
                           total_users=total_users)


# --- Librarian Dashboard ---

@app.route("/librarian")
@login_required
@role_required("librarian")
def librarian_dashboard():
    return render_template("librarian_dashboard.html")


# --- User Dashboard ---

@app.route("/user")
@login_required
@role_required("user")
def user_dashboard():
    return render_template("user_dashboard.html")


# --- Add Book ---

@app.route("/add-book", methods=["GET", "POST"])
@login_required
@role_required("admin", "librarian")
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        qty = request.form["quantity"]

        if not title or not author or not qty:
            flash("Please fill all fields", "error")
            return redirect(url_for("add_book"))

        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO books(title,author,quantity) VALUES(%s,%s,%s)",
            (title, author, qty)
        )
        conn.commit()
        conn.close()

        flash("Book added successfully!", "success")
        return redirect(url_for("add_book"))

    return render_template("add_book.html")


# --- Issue Book ---

@app.route("/issue-book", methods=["GET", "POST"])
@login_required
@role_required("admin", "librarian")
def issue_book():
    if request.method == "POST":
        book_id = request.form["book_id"]
        student = request.form["student_name"]

        if not book_id or not student:
            flash("Enter all fields", "error")
            return redirect(url_for("issue_book"))

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT quantity FROM books WHERE book_id=%s", (book_id,))
        result = cur.fetchone()

        if not result:
            flash("Book not found", "error")
            conn.close()
            return redirect(url_for("issue_book"))

        if result[0] <= 0:
            flash("Book out of stock", "error")
            conn.close()
            return redirect(url_for("issue_book"))

        cur.execute(
            "INSERT INTO issued_books(book_id,student_name,issue_date) VALUES(%s,%s,CURDATE())",
            (book_id, student)
        )
        cur.execute(
            "UPDATE books SET quantity = quantity - 1 WHERE book_id=%s",
            (book_id,)
        )
        conn.commit()
        conn.close()

        flash("Book issued successfully!", "success")
        return redirect(url_for("issue_book"))

    return render_template("issue_book.html")


# --- View Books ---

@app.route("/view-books")
@login_required
def view_books():
    search = request.args.get("search", "")

    conn = connect_db()
    cur = conn.cursor()

    if search:
        cur.execute("SELECT * FROM books WHERE title LIKE %s", ("%" + search + "%",))
    else:
        cur.execute("SELECT * FROM books")

    books = cur.fetchall()
    conn.close()

    return render_template("view_books.html", books=books, search=search)


# --- Issued Books ---

@app.route("/issued-books")
@login_required
@role_required("admin", "librarian")
def issued_books():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM issued_books")
    books = cur.fetchall()
    conn.close()

    return render_template("issued_books.html", books=books)


# --- Manage Books ---

@app.route("/manage-books")
@login_required
@role_required("admin")
def manage_books():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    conn.close()

    return render_template("manage_books.html", books=books)


@app.route("/update-book", methods=["POST"])
@login_required
@role_required("admin")
def update_book():
    book_id = request.form["book_id"]
    qty = request.form["quantity"]

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE books SET quantity=%s WHERE book_id=%s", (qty, book_id))
    conn.commit()
    conn.close()

    flash("Quantity updated!", "success")
    return redirect(url_for("manage_books"))


@app.route("/delete-book/<int:book_id>")
@login_required
@role_required("admin")
def delete_book(book_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
    conn.commit()
    conn.close()

    flash("Book deleted!", "success")
    return redirect(url_for("manage_books"))


# --- Request Book ---

@app.route("/request-book", methods=["GET", "POST"])
@login_required
@role_required("user")
def request_book():
    username = session["username"]

    if request.method == "POST":
        book_id = request.form["book_id"]

        conn = connect_db()
        cur = conn.cursor()

        # Check if already issued
        cur.execute(
            "SELECT * FROM issued_books WHERE book_id=%s AND student_name=%s",
            (book_id, username)
        )
        if cur.fetchone():
            flash("You already borrowed this book", "error")
            conn.close()
            return redirect(url_for("request_book"))

        # Check if request already pending
        cur.execute(
            "SELECT * FROM book_requests WHERE book_id=%s AND username=%s AND status='pending'",
            (book_id, username)
        )
        if cur.fetchone():
            flash("Request already pending", "error")
            conn.close()
            return redirect(url_for("request_book"))

        # Check quantity
        cur.execute("SELECT quantity FROM books WHERE book_id=%s", (book_id,))
        result = cur.fetchone()
        if not result or result[0] <= 0:
            flash("Book not available", "error")
            conn.close()
            return redirect(url_for("request_book"))

        cur.execute(
            "INSERT INTO book_requests(book_id,username,status) VALUES(%s,%s,'pending')",
            (book_id, username)
        )
        conn.commit()
        conn.close()

        flash("Request sent!", "success")
        return redirect(url_for("request_book"))

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    conn.close()

    return render_template("request_book.html", books=books)


# --- Return Book ---

@app.route("/return-book", methods=["GET", "POST"])
@login_required
@role_required("user")
def return_book():
    username = session["username"]

    if request.method == "POST":
        issue_id = request.form["issue_id"]
        book_id = request.form["book_id"]

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM issued_books WHERE issue_id=%s", (issue_id,))
        cur.execute(
            "UPDATE books SET quantity = quantity + 1 WHERE book_id=%s",
            (book_id,)
        )
        conn.commit()
        conn.close()

        flash("Book returned successfully!", "success")
        return redirect(url_for("return_book"))

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT issue_id, book_id, student_name, issue_date FROM issued_books WHERE student_name=%s",
        (username,)
    )
    books = cur.fetchall()
    conn.close()

    return render_template("return_book.html", books=books)


# --- View Requests ---

@app.route("/view-requests")
@login_required
@role_required("admin", "librarian")
def view_requests():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM book_requests")
    requests_list = cur.fetchall()
    conn.close()

    return render_template("view_requests.html", requests=requests_list)


@app.route("/approve-request/<int:request_id>/<int:book_id>/<username>")
@login_required
@role_required("admin", "librarian")
def approve_request(request_id, book_id, username):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT quantity FROM books WHERE book_id=%s", (book_id,))
    result = cur.fetchone()

    if not result or result[0] <= 0:
        flash("Book out of stock, cannot approve", "error")
        conn.close()
        return redirect(url_for("view_requests"))

    cur.execute(
        "INSERT INTO issued_books(book_id,student_name) VALUES(%s,%s)",
        (book_id, username)
    )
    cur.execute(
        "UPDATE books SET quantity=quantity-1 WHERE book_id=%s",
        (book_id,)
    )
    cur.execute(
        "UPDATE book_requests SET status='approved' WHERE request_id=%s",
        (request_id,)
    )
    conn.commit()
    conn.close()

    flash("Request approved!", "success")
    return redirect(url_for("view_requests"))


@app.route("/reject-request/<int:request_id>")
@login_required
@role_required("admin", "librarian")
def reject_request(request_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE book_requests SET status='rejected' WHERE request_id=%s",
        (request_id,)
    )
    conn.commit()
    conn.close()

    flash("Request rejected", "success")
    return redirect(url_for("view_requests"))


# --- Statistics API ---

@app.route("/statistics")
@login_required
@role_required("admin")
def statistics():
    return render_template("stats.html")


@app.route("/api/stats")
@login_required
@role_required("admin")
def api_stats():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM books")
    total_books = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(quantity),0) FROM books")
    total_copies = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM issued_books")
    total_issued = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM book_requests WHERE status='pending'")
    pending = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM book_requests WHERE status='approved'")
    approved = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM book_requests WHERE status='rejected'")
    rejected = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT title, quantity FROM books ORDER BY quantity DESC LIMIT 10")
    book_data = cur.fetchall()

    cur.execute(
        "SELECT student_name, COUNT(*) as cnt FROM issued_books "
        "GROUP BY student_name ORDER BY cnt DESC LIMIT 5"
    )
    borrower_data = cur.fetchall()

    cur.execute(
        "SELECT b.title, COUNT(*) as cnt FROM book_requests br "
        "JOIN books b ON br.book_id = b.book_id "
        "GROUP BY b.title ORDER BY cnt DESC LIMIT 5"
    )
    requested_data = cur.fetchall()

    conn.close()

    return jsonify({
        "total_books": total_books,
        "total_copies": int(total_copies),
        "total_issued": total_issued,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "total_users": total_users,
        "book_availability": [{"title": r[0], "quantity": r[1]} for r in book_data],
        "top_borrowers": [{"name": r[0], "count": r[1]} for r in borrower_data],
        "most_requested": [{"title": r[0], "count": r[1]} for r in requested_data]
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
