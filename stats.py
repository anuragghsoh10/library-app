import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from database import connect_db


def show_stats(parent):

    conn = connect_db()
    cur = conn.cursor()

    # --- Gather all data ---

    cur.execute("SELECT COUNT(*) FROM books")
    total_books = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(quantity),0) FROM books")
    total_copies = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM issued_books")
    total_issued = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM book_requests WHERE status='pending'")
    pending_req = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM book_requests WHERE status='approved'")
    approved_req = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM book_requests WHERE status='rejected'")
    rejected_req = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    # Book quantities for bar chart
    cur.execute("SELECT title, quantity FROM books ORDER BY quantity DESC LIMIT 10")
    book_data = cur.fetchall()

    # Top borrowers
    cur.execute(
        "SELECT student_name, COUNT(*) as cnt FROM issued_books "
        "GROUP BY student_name ORDER BY cnt DESC LIMIT 5"
    )
    borrower_data = cur.fetchall()

    # Most requested books
    cur.execute(
        "SELECT b.title, COUNT(*) as cnt FROM book_requests br "
        "JOIN books b ON br.book_id = b.book_id "
        "GROUP BY b.title ORDER BY cnt DESC LIMIT 5"
    )
    requested_data = cur.fetchall()

    conn.close()

    # --- Header ---
    tk.Label(
        parent, text="📊 Library Statistics",
        bg="#2c3e50", fg="white",
        font=("Segoe UI", 18, "bold"),
        pady=10
    ).pack(fill="x")

    # --- Scrollable area ---
    canvas_scroll = tk.Canvas(parent, bg="#ecf0f1", highlightthickness=0)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas_scroll.yview)
    scroll_frame = tk.Frame(canvas_scroll, bg="#ecf0f1")

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
    )

    canvas_scroll.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas_scroll.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas_scroll.pack(side="left", fill="both", expand=True)

    # Bind mousewheel
    def _on_mousewheel(event):
        canvas_scroll.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas_scroll.bind_all("<MouseWheel>", _on_mousewheel)

    # --- Summary Cards Row ---
    cards_frame = tk.Frame(scroll_frame, bg="#ecf0f1")
    cards_frame.pack(pady=15, padx=20, fill="x")

    summary_data = [
        ("📚", "Total Titles", str(total_books), "#3498db"),
        ("📦", "Total Copies", str(total_copies), "#2ecc71"),
        ("📖", "Books Issued", str(total_issued), "#e67e22"),
        ("📩", "Pending Requests", str(pending_req), "#e74c3c"),
        ("✅", "Approved", str(approved_req), "#27ae60"),
        ("👤", "Total Users", str(total_users), "#9b59b6"),
    ]

    for i, (icon, label, value, color) in enumerate(summary_data):

        card = tk.Frame(cards_frame, bg="white", bd=0, relief="flat",
                        highlightbackground="#dcdde1", highlightthickness=1)
        card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
        cards_frame.grid_columnconfigure(i, weight=1)

        # Color accent bar at top
        accent = tk.Frame(card, bg=color, height=4)
        accent.pack(fill="x")

        inner = tk.Frame(card, bg="white")
        inner.pack(padx=12, pady=10)

        tk.Label(inner, text=icon, font=("Segoe UI", 20), bg="white").pack()

        tk.Label(
            inner, text=value,
            font=("Segoe UI", 24, "bold"),
            bg="white", fg=color
        ).pack()

        tk.Label(
            inner, text=label,
            font=("Segoe UI", 9),
            bg="white", fg="#7f8c8d"
        ).pack()

    # --- Charts Row 1: Book Availability + Request Status ---
    charts_row1 = tk.Frame(scroll_frame, bg="#ecf0f1")
    charts_row1.pack(pady=10, padx=20, fill="x")

    # -- Bar Chart: Book Availability --
    bar_card = tk.Frame(charts_row1, bg="white", bd=0,
                        highlightbackground="#dcdde1", highlightthickness=1)
    bar_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

    tk.Label(bar_card, text="Book Availability (Top 10)",
             font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50"
             ).pack(pady=(10, 0))

    if book_data:
        titles = [row[0][:12] + ".." if len(row[0]) > 12 else row[0] for row in book_data]
        quantities = [row[1] for row in book_data]

        fig1 = Figure(figsize=(5, 3), dpi=90)
        fig1.patch.set_facecolor("white")
        ax1 = fig1.add_subplot(111)

        colors_bar = ["#3498db", "#2ecc71", "#e67e22", "#e74c3c", "#9b59b6",
                       "#1abc9c", "#f39c12", "#d35400", "#c0392b", "#8e44ad"]

        bars = ax1.barh(titles[::-1], quantities[::-1],
                        color=colors_bar[:len(titles)], edgecolor="white", height=0.6)

        ax1.set_xlabel("Quantity", fontsize=9, color="#7f8c8d")
        ax1.tick_params(axis="both", labelsize=8, colors="#7f8c8d")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.spines["left"].set_color("#dcdde1")
        ax1.spines["bottom"].set_color("#dcdde1")

        # Value labels on bars
        for bar in bars:
            width = bar.get_width()
            ax1.text(width + 0.1, bar.get_y() + bar.get_height() / 2,
                     f'{int(width)}', va='center', fontsize=8, color="#2c3e50")

        fig1.tight_layout(pad=1.5)

        canvas1 = FigureCanvasTkAgg(fig1, bar_card)
        canvas1.draw()
        canvas1.get_tk_widget().pack(padx=10, pady=(0, 10))
    else:
        tk.Label(bar_card, text="No books data available",
                 bg="white", fg="#95a5a6", font=("Segoe UI", 10)).pack(pady=30)

    # -- Pie Chart: Request Status --
    pie_card = tk.Frame(charts_row1, bg="white", bd=0,
                        highlightbackground="#dcdde1", highlightthickness=1)
    pie_card.pack(side="right", fill="both", expand=True, padx=(8, 0))

    tk.Label(pie_card, text="Request Status Breakdown",
             font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50"
             ).pack(pady=(10, 0))

    req_total = pending_req + approved_req + rejected_req

    if req_total > 0:
        fig2 = Figure(figsize=(4, 3), dpi=90)
        fig2.patch.set_facecolor("white")
        ax2 = fig2.add_subplot(111)

        sizes = [pending_req, approved_req, rejected_req]
        labels = [f"Pending ({pending_req})", f"Approved ({approved_req})", f"Rejected ({rejected_req})"]
        pie_colors = ["#f39c12", "#27ae60", "#e74c3c"]
        explode = (0.05, 0.05, 0.05)

        wedges, texts, autotexts = ax2.pie(
            sizes, labels=labels, colors=pie_colors,
            autopct="%1.0f%%", startangle=90, explode=explode,
            textprops={"fontsize": 9, "color": "#2c3e50"},
            pctdistance=0.75
        )

        for t in autotexts:
            t.set_fontsize(9)
            t.set_color("white")
            t.set_fontweight("bold")

        # Draw center circle for donut effect
        centre_circle = plt.Circle((0, 0), 0.50, fc="white")
        ax2.add_artist(centre_circle)
        ax2.set_aspect("equal")

        fig2.tight_layout(pad=1.5)

        canvas2 = FigureCanvasTkAgg(fig2, pie_card)
        canvas2.draw()
        canvas2.get_tk_widget().pack(padx=10, pady=(0, 10))
    else:
        tk.Label(pie_card, text="No requests data available",
                 bg="white", fg="#95a5a6", font=("Segoe UI", 10)).pack(pady=30)

    # --- Charts Row 2: Top Borrowers + Most Requested ---
    charts_row2 = tk.Frame(scroll_frame, bg="#ecf0f1")
    charts_row2.pack(pady=10, padx=20, fill="x")

    # -- Top Borrowers --
    borrow_card = tk.Frame(charts_row2, bg="white", bd=0,
                           highlightbackground="#dcdde1", highlightthickness=1)
    borrow_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

    tk.Label(borrow_card, text="Top Borrowers",
             font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50"
             ).pack(pady=(10, 0))

    if borrower_data:
        fig3 = Figure(figsize=(4.5, 2.5), dpi=90)
        fig3.patch.set_facecolor("white")
        ax3 = fig3.add_subplot(111)

        names = [row[0][:15] for row in borrower_data]
        counts = [row[1] for row in borrower_data]

        bars3 = ax3.bar(names, counts, color="#9b59b6", edgecolor="white", width=0.5)
        ax3.set_ylabel("Books Borrowed", fontsize=9, color="#7f8c8d")
        ax3.tick_params(axis="both", labelsize=8, colors="#7f8c8d")
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        ax3.spines["left"].set_color("#dcdde1")
        ax3.spines["bottom"].set_color("#dcdde1")

        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width() / 2, height + 0.1,
                     f'{int(height)}', ha='center', fontsize=9, color="#2c3e50", fontweight="bold")

        fig3.tight_layout(pad=1.5)

        canvas3 = FigureCanvasTkAgg(fig3, borrow_card)
        canvas3.draw()
        canvas3.get_tk_widget().pack(padx=10, pady=(0, 10))
    else:
        tk.Label(borrow_card, text="No borrowing data yet",
                 bg="white", fg="#95a5a6", font=("Segoe UI", 10)).pack(pady=30)

    # -- Most Requested Books --
    req_card = tk.Frame(charts_row2, bg="white", bd=0,
                        highlightbackground="#dcdde1", highlightthickness=1)
    req_card.pack(side="right", fill="both", expand=True, padx=(8, 0))

    tk.Label(req_card, text="Most Requested Books",
             font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50"
             ).pack(pady=(10, 0))

    if requested_data:
        fig4 = Figure(figsize=(4.5, 2.5), dpi=90)
        fig4.patch.set_facecolor("white")
        ax4 = fig4.add_subplot(111)

        req_titles = [row[0][:12] + ".." if len(row[0]) > 12 else row[0] for row in requested_data]
        req_counts = [row[1] for row in requested_data]

        bars4 = ax4.bar(req_titles, req_counts, color="#e67e22", edgecolor="white", width=0.5)
        ax4.set_ylabel("Requests", fontsize=9, color="#7f8c8d")
        ax4.tick_params(axis="both", labelsize=8, colors="#7f8c8d")
        ax4.spines["top"].set_visible(False)
        ax4.spines["right"].set_visible(False)
        ax4.spines["left"].set_color("#dcdde1")
        ax4.spines["bottom"].set_color("#dcdde1")

        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width() / 2, height + 0.1,
                     f'{int(height)}', ha='center', fontsize=9, color="#2c3e50", fontweight="bold")

        fig4.tight_layout(pad=1.5)

        canvas4 = FigureCanvasTkAgg(fig4, req_card)
        canvas4.draw()
        canvas4.get_tk_widget().pack(padx=10, pady=(0, 10))
    else:
        tk.Label(req_card, text="No request data yet",
                 bg="white", fg="#95a5a6", font=("Segoe UI", 10)).pack(pady=30)

    # Footer spacer
    tk.Frame(scroll_frame, bg="#ecf0f1", height=20).pack()