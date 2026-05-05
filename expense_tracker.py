import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import datetime
import threading
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('TkAgg')

# ── Constants ────────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.expanduser("~"), "expenses_data.json")

CATEGORIES = [
    "🍔 Food & Dining", "🚗 Transportation", "🏠 Housing", "💡 Utilities",
    "🛒 Shopping", "🎮 Entertainment", "💊 Health", "📚 Education",
    "✈️ Travel", "💼 Business", "💰 Savings", "🎁 Gifts", "📦 Other"
]

COLORS = {
    "bg":        "#0F1117",
    "sidebar":   "#1A1D27",
    "card":      "#1E2130",
    "card2":     "#252840",
    "accent":    "#6C63FF",
    "accent2":   "#FF6584",
    "green":     "#00D4AA",
    "yellow":    "#FFD166",
    "text":      "#EAEAEA",
    "subtext":   "#8B8FA8",
    "border":    "#2E3250",
    "entry":     "#252840",
    "hover":     "#2D3055",
}

CAT_COLORS = [
    "#6C63FF","#FF6584","#00D4AA","#FFD166","#4ECDC4","#FF6B6B",
    "#A8E6CF","#FFAAA5","#85C1E9","#F1948A","#82E0AA","#F7DC6F","#BB8FCE"
]


# ── Data Layer ───────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"expenses": [], "budget": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Rounded Rectangle Helper ─────────────────────────────────────────────────
def round_rect(canvas, x1, y1, x2, y2, r=15, **kwargs):
    pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2,
           x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


# ── Main Application ─────────────────────────────────────────────────────────
class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💸 SmartSpend — AI Expense Tracker")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)

        self.data = load_data()
        self.current_page = tk.StringVar(value="dashboard")
        self.ai_messages = []

        self._build_ui()
        self.show_page("dashboard")

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()

        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.pages = {}
        for name, cls in [
            ("dashboard", DashboardPage),
            ("add",       AddExpensePage),
            ("history",   HistoryPage),
            ("charts",    ChartsPage),
            ("ai",        AIPage),
            ("budget",    BudgetPage),
        ]:
            page = cls(self.content, self)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = page

    def _build_sidebar(self):
        sb = tk.Frame(self, bg=COLORS["sidebar"], width=220)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        # Logo
        logo_frame = tk.Frame(sb, bg=COLORS["sidebar"])
        logo_frame.pack(fill="x", pady=(25, 10), padx=20)
        tk.Label(logo_frame, text="💸", font=("Segoe UI Emoji", 28),
                 bg=COLORS["sidebar"], fg=COLORS["accent"]).pack(side="left")
        tk.Label(logo_frame, text="SmartSpend", font=("Segoe UI", 16, "bold"),
                 bg=COLORS["sidebar"], fg=COLORS["text"]).pack(side="left", padx=(8,0))

        tk.Frame(sb, bg=COLORS["border"], height=1).pack(fill="x", padx=20, pady=10)

        nav_items = [
            ("dashboard", "🏠", "Dashboard"),
            ("add",       "➕", "Add Expense"),
            ("history",   "📋", "History"),
            ("charts",    "📊", "Analytics"),
            ("budget",    "🎯", "Budget"),
            ("ai",        "🤖", "AI Assistant"),
        ]

        self.nav_buttons = {}
        for page_id, icon, label in nav_items:
            btn = self._nav_btn(sb, icon, label, page_id)
            self.nav_buttons[page_id] = btn

        # Bottom info
        tk.Frame(sb, bg=COLORS["sidebar"]).pack(fill="both", expand=True)
        tk.Frame(sb, bg=COLORS["border"], height=1).pack(fill="x", padx=20, pady=10)
        tk.Label(sb, text="v1.0  •  Powered by Claude AI",
                 font=("Segoe UI", 9), bg=COLORS["sidebar"],
                 fg=COLORS["subtext"]).pack(pady=(0,15))

    def _nav_btn(self, parent, icon, label, page_id):
        frame = tk.Frame(parent, bg=COLORS["sidebar"], cursor="hand2")
        frame.pack(fill="x", padx=12, pady=2)

        indicator = tk.Frame(frame, width=4, bg=COLORS["sidebar"])
        indicator.pack(side="left", fill="y", padx=(0,8))

        inner = tk.Frame(frame, bg=COLORS["sidebar"], padx=10, pady=10)
        inner.pack(fill="x", side="left", expand=True)

        ico = tk.Label(inner, text=icon, font=("Segoe UI Emoji", 14),
                       bg=COLORS["sidebar"], fg=COLORS["subtext"])
        ico.pack(side="left")
        lbl = tk.Label(inner, text=label, font=("Segoe UI", 12),
                       bg=COLORS["sidebar"], fg=COLORS["subtext"])
        lbl.pack(side="left", padx=(10,0))

        for w in [frame, inner, ico, lbl, indicator]:
            w.bind("<Button-1>", lambda e, p=page_id: self.show_page(p))
            w.bind("<Enter>",    lambda e, f=inner, i=ico, l=lbl: self._nav_hover(f, i, l, True))
            w.bind("<Leave>",    lambda e, p=page_id, f=inner, i=ico, l=lbl: self._nav_hover_leave(p, f, i, l))

        return {"frame": frame, "inner": inner, "ico": ico, "lbl": lbl, "indicator": indicator}

    def _nav_hover(self, inner, ico, lbl, on):
        if on:
            inner.configure(bg=COLORS["hover"])
            ico.configure(bg=COLORS["hover"])
            lbl.configure(bg=COLORS["hover"])

    def _nav_hover_leave(self, page_id, inner, ico, lbl):
        if self.current_page.get() != page_id:
            inner.configure(bg=COLORS["sidebar"])
            ico.configure(bg=COLORS["sidebar"])
            lbl.configure(bg=COLORS["sidebar"])

    def show_page(self, name):
        # Deactivate old
        old = self.current_page.get()
        if old in self.nav_buttons:
            nb = self.nav_buttons[old]
            nb["inner"].configure(bg=COLORS["sidebar"])
            nb["ico"].configure(bg=COLORS["sidebar"], fg=COLORS["subtext"])
            nb["lbl"].configure(bg=COLORS["sidebar"], fg=COLORS["subtext"])
            nb["indicator"].configure(bg=COLORS["sidebar"])

        self.current_page.set(name)

        # Activate new
        if name in self.nav_buttons:
            nb = self.nav_buttons[name]
            nb["inner"].configure(bg=COLORS["hover"])
            nb["ico"].configure(bg=COLORS["hover"], fg=COLORS["accent"])
            nb["lbl"].configure(bg=COLORS["hover"], fg=COLORS["text"], font=("Segoe UI", 12, "bold"))
            nb["indicator"].configure(bg=COLORS["accent"])

        self.pages[name].tkraise()
        self.pages[name].refresh()


# ── Base Page ────────────────────────────────────────────────────────────────
class BasePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self.build()

    def build(self): pass
    def refresh(self): pass

    def card(self, parent, **kwargs):
        f = tk.Frame(parent, bg=COLORS["card"],
                     highlightbackground=COLORS["border"],
                     highlightthickness=1, **kwargs)
        return f

    def heading(self, parent, text, size=20):
        tk.Label(parent, text=text, font=("Segoe UI", size, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")

    def subtext(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 11),
                 bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")

    def styled_entry(self, parent, placeholder="", width=30, **kwargs):
        e = tk.Entry(parent, font=("Segoe UI", 12), bg=COLORS["entry"],
                     fg=COLORS["text"], insertbackground=COLORS["text"],
                     relief="flat", bd=0, width=width, **kwargs)
        return e

    def styled_btn(self, parent, text, command, color=None, width=None):
        color = color or COLORS["accent"]
        btn = tk.Button(parent, text=text, command=command,
                        font=("Segoe UI", 12, "bold"),
                        bg=color, fg="white", activebackground=color,
                        activeforeground="white", relief="flat", bd=0,
                        padx=20, pady=10, cursor="hand2",
                        **({"width": width} if width else {}))
        return btn


# ── Dashboard ────────────────────────────────────────────────────────────────
class DashboardPage(BasePage):
    def build(self):
        self.main = tk.Frame(self, bg=COLORS["bg"])
        self.main.pack(fill="both", expand=True, padx=30, pady=25)

    def refresh(self):
        for w in self.main.winfo_children():
            w.destroy()

        expenses = self.app.data["expenses"]
        now = datetime.datetime.now()
        this_month = [e for e in expenses
                      if e["date"].startswith(f"{now.year}-{now.month:02d}")]
        total_month = sum(e["amount"] for e in this_month)
        total_all   = sum(e["amount"] for e in expenses)
        budget_total = sum(self.app.data.get("budget", {}).values())

        # Header
        hdr = tk.Frame(self.main, bg=COLORS["bg"])
        hdr.pack(fill="x", pady=(0, 20))
        tk.Label(hdr, text=f"👋  Welcome back!",
                 font=("Segoe UI", 22, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(hdr, text=now.strftime("%A, %B %d, %Y"),
                 font=("Segoe UI", 12),
                 bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")

        # Stat cards
        cards_row = tk.Frame(self.main, bg=COLORS["bg"])
        cards_row.pack(fill="x", pady=(0, 20))
        for col in range(4):
            cards_row.columnconfigure(col, weight=1)

        stats = [
            ("💸 This Month",   f"${total_month:,.2f}",   COLORS["accent"],  f"{len(this_month)} transactions"),
            ("📦 All Time",     f"${total_all:,.2f}",     COLORS["green"],   f"{len(expenses)} total"),
            ("🎯 Budget",       f"${budget_total:,.2f}",  COLORS["yellow"],  "Monthly limit"),
            ("💰 Remaining",    f"${max(0, budget_total - total_month):,.2f}", COLORS["accent2"],
             "Left this month" if budget_total else "No budget set"),
        ]

        for i, (title, value, color, sub) in enumerate(stats):
            c = tk.Frame(cards_row, bg=COLORS["card"],
                         highlightbackground=color, highlightthickness=2)
            c.grid(row=0, column=i, sticky="ew", padx=(0,12) if i<3 else 0, pady=4)
            tk.Frame(c, bg=color, height=4).pack(fill="x")
            inner = tk.Frame(c, bg=COLORS["card"])
            inner.pack(fill="both", padx=20, pady=15)
            tk.Label(inner, text=title, font=("Segoe UI", 11),
                     bg=COLORS["card"], fg=COLORS["subtext"]).pack(anchor="w")
            tk.Label(inner, text=value, font=("Segoe UI", 22, "bold"),
                     bg=COLORS["card"], fg=color).pack(anchor="w", pady=(4,0))
            tk.Label(inner, text=sub, font=("Segoe UI", 10),
                     bg=COLORS["card"], fg=COLORS["subtext"]).pack(anchor="w")

        # Bottom row
        bot = tk.Frame(self.main, bg=COLORS["bg"])
        bot.pack(fill="both", expand=True)
        bot.columnconfigure(0, weight=3)
        bot.columnconfigure(1, weight=2)

        # Recent transactions
        rec = tk.Frame(bot, bg=COLORS["card"],
                       highlightbackground=COLORS["border"], highlightthickness=1)
        rec.grid(row=0, column=0, sticky="nsew", padx=(0,12))
        tk.Label(rec, text="Recent Transactions", font=("Segoe UI", 14, "bold"),
                 bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w", padx=20, pady=(15,5))
        tk.Frame(rec, bg=COLORS["border"], height=1).pack(fill="x", padx=20)

        recent = sorted(expenses, key=lambda e: e["date"], reverse=True)[:8]
        if not recent:
            tk.Label(rec, text="No expenses yet.\nClick 'Add Expense' to start!",
                     font=("Segoe UI", 12), bg=COLORS["card"],
                     fg=COLORS["subtext"], justify="center").pack(pady=30)
        for exp in recent:
            row = tk.Frame(rec, bg=COLORS["card"])
            row.pack(fill="x", padx=20, pady=6)
            cat_icon = exp.get("category","📦 Other").split(" ")[0]
            tk.Label(row, text=cat_icon, font=("Segoe UI Emoji", 16),
                     bg=COLORS["card"], fg=COLORS["text"]).pack(side="left")
            info = tk.Frame(row, bg=COLORS["card"])
            info.pack(side="left", padx=(10,0), expand=True, fill="x")
            tk.Label(info, text=exp.get("description","Expense"),
                     font=("Segoe UI", 11, "bold"),
                     bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w")
            tk.Label(info, text=f"{exp['date']} • {exp.get('category','Other')}",
                     font=("Segoe UI", 10),
                     bg=COLORS["card"], fg=COLORS["subtext"]).pack(anchor="w")
            tk.Label(row, text=f"-${exp['amount']:,.2f}",
                     font=("Segoe UI", 12, "bold"),
                     bg=COLORS["card"], fg=COLORS["accent2"]).pack(side="right")

        # Category breakdown
        pie_frame = tk.Frame(bot, bg=COLORS["card"],
                             highlightbackground=COLORS["border"], highlightthickness=1)
        pie_frame.grid(row=0, column=1, sticky="nsew")
        tk.Label(pie_frame, text="By Category", font=("Segoe UI", 14, "bold"),
                 bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w", padx=20, pady=(15,5))
        tk.Frame(pie_frame, bg=COLORS["border"], height=1).pack(fill="x", padx=20)

        if this_month:
            cat_totals = {}
            for e in this_month:
                cat_totals[e.get("category","Other")] = cat_totals.get(e.get("category","Other"),0)+e["amount"]
            fig = Figure(figsize=(3.5, 3.5), facecolor=COLORS["card"])
            ax  = fig.add_subplot(111)
            labels = list(cat_totals.keys())
            sizes  = list(cat_totals.values())
            ax.pie(sizes, labels=None,
                   colors=CAT_COLORS[:len(sizes)],
                   startangle=140, wedgeprops={"width":0.6})
            ax.set_facecolor(COLORS["card"])
            canvas = FigureCanvasTkAgg(fig, pie_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            tk.Label(pie_frame, text="No data this month",
                     font=("Segoe UI", 11), bg=COLORS["card"],
                     fg=COLORS["subtext"]).pack(pady=40)


# ── Add Expense ───────────────────────────────────────────────────────────────
class AddExpensePage(BasePage):
    def build(self):
        outer = tk.Frame(self, bg=COLORS["bg"])
        outer.pack(fill="both", expand=True, padx=30, pady=25)

        tk.Label(outer, text="➕  Add New Expense",
                 font=("Segoe UI", 22, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(outer, text="Fill in the details below to track your spending",
                 font=("Segoe UI", 12),
                 bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0,20))

        form_card = tk.Frame(outer, bg=COLORS["card"],
                             highlightbackground=COLORS["border"], highlightthickness=1)
        form_card.pack(fill="both", expand=True)

        form = tk.Frame(form_card, bg=COLORS["card"])
        form.pack(fill="both", expand=True, padx=40, pady=30)

        def field(label, widget_factory):
            lf = tk.Frame(form, bg=COLORS["card"])
            lf.pack(fill="x", pady=8)
            tk.Label(lf, text=label, font=("Segoe UI", 11, "bold"),
                     bg=COLORS["card"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0,4))
            w = widget_factory(lf)
            return w

        self.desc_var = tk.StringVar()
        self.desc_entry = field("📝  Description", lambda p: self._entry(p, self.desc_var))

        self.amount_var = tk.StringVar()
        self.amount_entry = field("💵  Amount ($)", lambda p: self._entry(p, self.amount_var))

        self.cat_var = tk.StringVar(value=CATEGORIES[0])
        def cat_widget(p):
            cb = ttk.Combobox(p, textvariable=self.cat_var,
                              values=CATEGORIES, font=("Segoe UI", 12),
                              state="readonly")
            cb.pack(fill="x", ipady=8)
            style = ttk.Style()
            style.theme_use('default')
            style.configure("TCombobox", fieldbackground=COLORS["entry"],
                            background=COLORS["entry"],
                            foreground=COLORS["text"],
                            arrowcolor=COLORS["text"])
            return cb
        field("🏷️  Category", cat_widget)

        self.date_var = tk.StringVar(value=datetime.date.today().isoformat())
        field("📅  Date (YYYY-MM-DD)", lambda p: self._entry(p, self.date_var))

        self.note_var = tk.StringVar()
        field("📓  Note (optional)", lambda p: self._entry(p, self.note_var))

        btn_row = tk.Frame(form, bg=COLORS["card"])
        btn_row.pack(fill="x", pady=(20,0))

        self.styled_btn(btn_row, "  💾  Save Expense", self.save_expense,
                        color=COLORS["accent"]).pack(side="left", padx=(0,10))
        self.styled_btn(btn_row, "  🗑️  Clear", self.clear_form,
                        color=COLORS["subtext"]).pack(side="left")

        self.status = tk.Label(form, text="", font=("Segoe UI", 11),
                               bg=COLORS["card"], fg=COLORS["green"])
        self.status.pack(anchor="w", pady=(10,0))

    def _entry(self, parent, var):
        e = tk.Entry(parent, textvariable=var, font=("Segoe UI", 13),
                     bg=COLORS["entry"], fg=COLORS["text"],
                     insertbackground=COLORS["text"],
                     relief="flat", bd=0)
        e.pack(fill="x", ipady=10, ipadx=10)
        tk.Frame(parent, bg=COLORS["accent"], height=2).pack(fill="x")
        return e

    def save_expense(self):
        desc   = self.desc_var.get().strip()
        amount = self.amount_var.get().strip()
        date   = self.date_var.get().strip()
        cat    = self.cat_var.get()
        note   = self.note_var.get().strip()

        if not desc or not amount or not date:
            self.status.config(text="⚠️  Please fill in description, amount, and date.",
                               fg=COLORS["accent2"])
            return
        try:
            amount = float(amount)
            datetime.date.fromisoformat(date)
        except ValueError:
            self.status.config(text="⚠️  Invalid amount or date format.",
                               fg=COLORS["accent2"])
            return

        self.app.data["expenses"].append({
            "id":          int(datetime.datetime.now().timestamp() * 1000),
            "description": desc,
            "amount":      amount,
            "category":    cat,
            "date":        date,
            "note":        note,
        })
        save_data(self.app.data)
        self.status.config(text=f"✅  Expense '${amount:.2f} for {desc}' saved!",
                           fg=COLORS["green"])
        self.clear_form()

    def clear_form(self):
        self.desc_var.set("")
        self.amount_var.set("")
        self.date_var.set(datetime.date.today().isoformat())
        self.note_var.set()
        self.cat_var.set(CATEGORIES[0])

    def refresh(self): pass


# ── History ───────────────────────────────────────────────────────────────────
class HistoryPage(BasePage):
    def build(self):
        self.outer = tk.Frame(self, bg=COLORS["bg"])
        self.outer.pack(fill="both", expand=True, padx=30, pady=25)

    def refresh(self):
        for w in self.outer.winfo_children():
            w.destroy()

        tk.Label(self.outer, text="📋  Expense History",
                 font=("Segoe UI", 22, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")

        # Search/filter bar
        bar = tk.Frame(self.outer, bg=COLORS["bg"])
        bar.pack(fill="x", pady=(10,15))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._filter())
        se = tk.Entry(bar, textvariable=self.search_var,
                      font=("Segoe UI", 12), bg=COLORS["entry"],
                      fg=COLORS["text"], insertbackground=COLORS["text"],
                      relief="flat", width=30)
        se.pack(side="left", ipady=8, ipadx=10)
        tk.Label(bar, text="🔍", font=("Segoe UI Emoji",14),
                 bg=COLORS["bg"], fg=COLORS["subtext"]).pack(side="left", padx=(5,20))

        self.cat_filter = tk.StringVar(value="All")
        cats = ["All"] + CATEGORIES
        cb = ttk.Combobox(bar, textvariable=self.cat_filter,
                          values=cats, font=("Segoe UI", 12),
                          state="readonly", width=22)
        cb.pack(side="left", ipady=5)
        cb.bind("<<ComboboxSelected>>", lambda e: self._filter())

        # Table frame
        tbl_frame = tk.Frame(self.outer, bg=COLORS["card"],
                             highlightbackground=COLORS["border"],
                             highlightthickness=1)
        tbl_frame.pack(fill="both", expand=True)

        headers = ["Date", "Description", "Category", "Amount", "Note", ""]
        for i, h in enumerate(headers):
            tk.Label(tbl_frame, text=h, font=("Segoe UI", 11, "bold"),
                     bg=COLORS["card2"], fg=COLORS["subtext"],
                     anchor="w", padx=12, pady=10).grid(row=0, column=i, sticky="ew", padx=1)
        tbl_frame.grid_columnconfigure(1, weight=1)
        tbl_frame.grid_columnconfigure(2, weight=1)

        self.tbl_frame = tbl_frame
        self._filter()

    def _filter(self):
        # Remove old rows
        for w in self.tbl_frame.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()

        q   = self.search_var.get().lower()
        cat = self.cat_filter.get() if hasattr(self, "cat_filter") else "All"
        exps = sorted(self.app.data["expenses"],
                      key=lambda e: e["date"], reverse=True)

        filtered = [e for e in exps
                    if (q in e.get("description","").lower() or
                        q in e.get("category","").lower() or
                        q in e.get("date",""))
                    and (cat == "All" or e.get("category","") == cat)]

        for r, e in enumerate(filtered, 1):
            bg = COLORS["card"] if r % 2 == 0 else COLORS["card2"]
            vals = [e["date"],
                    e.get("description",""),
                    e.get("category",""),
                    f"${e['amount']:,.2f}",
                    e.get("note","—")]
            for c, v in enumerate(vals):
                fg = COLORS["accent2"] if c == 3 else COLORS["text"]
                tk.Label(self.tbl_frame, text=v, font=("Segoe UI", 11),
                         bg=bg, fg=fg, anchor="w", padx=12, pady=8)\
                  .grid(row=r, column=c, sticky="ew", padx=1)

            del_btn = tk.Button(self.tbl_frame, text="🗑",
                                font=("Segoe UI Emoji",11),
                                bg=bg, fg=COLORS["accent2"],
                                relief="flat", bd=0, cursor="hand2",
                                command=lambda eid=e["id"]: self._delete(eid))
            del_btn.grid(row=r, column=5, sticky="ew", padx=4)

        if not filtered:
            tk.Label(self.tbl_frame, text="No expenses found.",
                     font=("Segoe UI", 12), bg=COLORS["card"],
                     fg=COLORS["subtext"]).grid(row=1, column=0,
                     columnspan=6, pady=30)

    def _delete(self, eid):
        if messagebox.askyesno("Delete", "Remove this expense?"):
            self.app.data["expenses"] = [
                e for e in self.app.data["expenses"] if e["id"] != eid]
            save_data(self.app.data)
            self._filter()


# ── Charts ────────────────────────────────────────────────────────────────────
class ChartsPage(BasePage):
    def build(self):
        self.outer = tk.Frame(self, bg=COLORS["bg"])
        self.outer.pack(fill="both", expand=True, padx=30, pady=25)

    def refresh(self):
        for w in self.outer.winfo_children():
            w.destroy()

        tk.Label(self.outer, text="📊  Analytics",
                 font=("Segoe UI", 22, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", pady=(0,20))

        expenses = self.app.data["expenses"]
        if not expenses:
            tk.Label(self.outer, text="No data to display yet. Add some expenses first!",
                     font=("Segoe UI", 14), bg=COLORS["bg"],
                     fg=COLORS["subtext"]).pack(pady=60)
            return

        row1 = tk.Frame(self.outer, bg=COLORS["bg"])
        row1.pack(fill="both", expand=True)
        row1.columnconfigure(0, weight=1)
        row1.columnconfigure(1, weight=1)

        # Monthly trend
        monthly = {}
        for e in expenses:
            key = e["date"][:7]
            monthly[key] = monthly.get(key, 0) + e["amount"]
        months = sorted(monthly.keys())[-12:]
        amounts = [monthly[m] for m in months]

        fig1 = Figure(figsize=(6, 3.5), facecolor=COLORS["card"])
        ax1  = fig1.add_subplot(111, facecolor=COLORS["card"])
        ax1.fill_between(range(len(months)), amounts, alpha=0.2, color=COLORS["accent"])
        ax1.plot(range(len(months)), amounts, color=COLORS["accent"], linewidth=2.5, marker="o", markersize=5)
        ax1.set_xticks(range(len(months)))
        ax1.set_xticklabels([m[5:] for m in months], color=COLORS["subtext"], fontsize=9, rotation=30)
        ax1.tick_params(axis="y", colors=COLORS["subtext"])
        ax1.spines[:].set_color(COLORS["border"])
        ax1.set_title("Monthly Spending Trend", color=COLORS["text"], fontsize=12, pad=10)
        fig1.tight_layout()

        c1 = tk.Frame(row1, bg=COLORS["card"], highlightbackground=COLORS["border"], highlightthickness=1)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        FigureCanvasTkAgg(fig1, c1).get_tk_widget().pack(fill="both", expand=True)

        # Category pie
        cat_totals = {}
        for e in expenses:
            cat_totals[e.get("category","Other")] = cat_totals.get(e.get("category","Other"),0)+e["amount"]
        labels = list(cat_totals.keys())
        sizes  = list(cat_totals.values())

        fig2 = Figure(figsize=(6, 3.5), facecolor=COLORS["card"])
        ax2  = fig2.add_subplot(111, facecolor=COLORS["card"])
        wedges, texts, autotexts = ax2.pie(
            sizes, labels=None, colors=CAT_COLORS[:len(sizes)],
            autopct="%1.0f%%", startangle=140,
            wedgeprops={"width": 0.55})
        for at in autotexts:
            at.set_color(COLORS["text"])
            at.set_fontsize(9)
        ax2.legend(wedges, [l.split(" ",1)[-1] for l in labels],
                   loc="upper left", fontsize=7,
                   labelcolor=COLORS["subtext"],
                   facecolor=COLORS["card"],
                   edgecolor=COLORS["border"])
        ax2.set_title("Spending by Category", color=COLORS["text"], fontsize=12, pad=10)
        fig2.tight_layout()

        c2 = tk.Frame(row1, bg=COLORS["card"], highlightbackground=COLORS["border"], highlightthickness=1)
        c2.grid(row=0, column=1, sticky="nsew")
        FigureCanvasTkAgg(fig2, c2).get_tk_widget().pack(fill="both", expand=True)


# ── Budget ────────────────────────────────────────────────────────────────────
class BudgetPage(BasePage):
    def build(self):
        self.outer = tk.Frame(self, bg=COLORS["bg"])
        self.outer.pack(fill="both", expand=True, padx=30, pady=25)

    def refresh(self):
        for w in self.outer.winfo_children():
            w.destroy()

        tk.Label(self.outer, text="🎯  Budget Manager",
                 font=("Segoe UI", 22, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(self.outer,
                 text="Set monthly spending limits per category",
                 font=("Segoe UI", 12),
                 bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0,20))

        grid = tk.Frame(self.outer, bg=COLORS["bg"])
        grid.pack(fill="both", expand=True)

        now = datetime.datetime.now()
        this_month = [e for e in self.app.data["expenses"]
                      if e["date"].startswith(f"{now.year}-{now.month:02d}")]

        budgets = self.app.data.get("budget", {})
        self.budget_vars = {}

        cols = 2
        for i, cat in enumerate(CATEGORIES):
            row = i // cols
            col = i % cols

            spent = sum(e["amount"] for e in this_month
                        if e.get("category") == cat)
            budget = budgets.get(cat, 0)
            pct = min((spent / budget * 100) if budget else 0, 100)
            bar_color = COLORS["green"] if pct < 80 else (COLORS["yellow"] if pct < 100 else COLORS["accent2"])

            c = tk.Frame(grid, bg=COLORS["card"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1)
            c.grid(row=row, column=col, sticky="ew", padx=(0,12) if col==0 else 0, pady=6)
            grid.columnconfigure(col, weight=1)

            inner = tk.Frame(c, bg=COLORS["card"])
            inner.pack(fill="x", padx=16, pady=12)

            top = tk.Frame(inner, bg=COLORS["card"])
            top.pack(fill="x")
            tk.Label(top, text=cat, font=("Segoe UI", 12, "bold"),
                     bg=COLORS["card"], fg=COLORS["text"]).pack(side="left")
            tk.Label(top, text=f"${spent:.0f} / ${budget:.0f}",
                     font=("Segoe UI", 11),
                     bg=COLORS["card"], fg=COLORS["subtext"]).pack(side="right")

            # Progress bar
            pb_bg = tk.Frame(inner, bg=COLORS["border"], height=8)
            pb_bg.pack(fill="x", pady=(6,8))
            if pct > 0:
                tk.Frame(pb_bg, bg=bar_color, height=8,
                         width=int(pct/100 * 400)).place(x=0, y=0)

            # Budget entry
            entry_row = tk.Frame(inner, bg=COLORS["card"])
            entry_row.pack(fill="x")
            var = tk.StringVar(value=str(budget) if budget else "")
            self.budget_vars[cat] = var
            e = tk.Entry(entry_row, textvariable=var,
                         font=("Segoe UI", 11), bg=COLORS["entry"],
                         fg=COLORS["text"], insertbackground=COLORS["text"],
                         relief="flat", width=10)
            e.pack(side="left", ipady=5, ipadx=8)
            tk.Button(entry_row, text="Set", font=("Segoe UI", 10, "bold"),
                      bg=COLORS["accent"], fg="white", relief="flat", bd=0,
                      padx=10, pady=5, cursor="hand2",
                      command=lambda c=cat: self._set_budget(c)).pack(side="left", padx=(8,0))

    def _set_budget(self, cat):
        val = self.budget_vars[cat].get().strip()
        try:
            self.app.data.setdefault("budget",{})[cat] = float(val)
            save_data(self.app.data)
            self.refresh()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")


# ── AI Page ───────────────────────────────────────────────────────────────────
class AIPage(BasePage):
    def build(self):
        outer = tk.Frame(self, bg=COLORS["bg"])
        outer.pack(fill="both", expand=True, padx=30, pady=25)
        outer.grid_rowconfigure(1, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        hdr = tk.Frame(outer, bg=COLORS["bg"])
        hdr.grid(row=0, column=0, sticky="ew", pady=(0,15))
        tk.Label(hdr, text="🤖  AI Financial Assistant",
                 font=("Segoe UI", 22, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(hdr, text="Ask me anything about your spending — I'll analyze your data!",
                 font=("Segoe UI", 12),
                 bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")

        # Chat window
        chat_card = tk.Frame(outer, bg=COLORS["card"],
                             highlightbackground=COLORS["border"],
                             highlightthickness=1)
        chat_card.grid(row=1, column=0, sticky="nsew")
        chat_card.grid_rowconfigure(0, weight=1)
        chat_card.grid_columnconfigure(0, weight=1)

        self.chat_scroll = tk.Frame(chat_card, bg=COLORS["card"])
        self.chat_scroll.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(self.chat_scroll, bg=COLORS["card"],
                                highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.chat_scroll, orient="vertical",
                                  command=self.canvas.yview)
        self.msg_frame = tk.Frame(self.canvas, bg=COLORS["card"])
        self.msg_frame.bind("<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0,0), window=self.msg_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Quick prompts
        quick = tk.Frame(chat_card, bg=COLORS["card2"])
        quick.grid(row=1, column=0, sticky="ew", padx=15, pady=8)
        tk.Label(quick, text="Quick:", font=("Segoe UI", 10),
                 bg=COLORS["card2"], fg=COLORS["subtext"]).pack(side="left", padx=(0,6))
        for q in ["📊 Summarize spending", "💡 Saving tips", "📈 Biggest expenses", "🎯 Budget advice"]:
            tk.Button(quick, text=q, font=("Segoe UI", 10),
                      bg=COLORS["border"], fg=COLORS["text"],
                      relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
                      command=lambda qtext=q: self._quick(qtext)).pack(side="left", padx=3)

        # Input row
        input_row = tk.Frame(chat_card, bg=COLORS["card2"])
        input_row.grid(row=2, column=0, sticky="ew", padx=15, pady=12)
        input_row.columnconfigure(0, weight=1)

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(input_row, textvariable=self.input_var,
                                   font=("Segoe UI", 13), bg=COLORS["entry"],
                                   fg=COLORS["text"],
                                   insertbackground=COLORS["text"],
                                   relief="flat", bd=0)
        self.input_entry.grid(row=0, column=0, sticky="ew", ipady=10, ipadx=12)
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = tk.Button(input_row, text="  Send  ➤",
                                  font=("Segoe UI", 12, "bold"),
                                  bg=COLORS["accent"], fg="white",
                                  relief="flat", bd=0, padx=16, pady=9,
                                  cursor="hand2", command=self.send_message)
        self.send_btn.grid(row=0, column=1, padx=(8,0))

        # Welcome message
        self._add_msg("assistant",
            "👋 Hi! I'm your AI financial assistant powered by Claude.\n\n"
            "I have full access to your expense data and can help you:\n"
            "• Analyze spending patterns\n"
            "• Identify where you're overspending\n"
            "• Give personalized saving tips\n"
            "• Answer any financial questions\n\n"
            "What would you like to know?")

    def _quick(self, text):
        prompts = {
            "📊 Summarize spending": "Give me a summary of my spending habits",
            "💡 Saving tips": "Based on my expenses, give me 5 actionable money saving tips",
            "📈 Biggest expenses": "What are my biggest expense categories and how can I reduce them?",
            "🎯 Budget advice": "Based on my spending, help me create a realistic monthly budget",
        }
        self.input_var.set(prompts.get(text, text))
        self.send_message()

    def _add_msg(self, role, text):
        is_user = role == "user"
        row = tk.Frame(self.msg_frame, bg=COLORS["card"])
        row.pack(fill="x", padx=16, pady=6, anchor="e" if is_user else "w")

        if is_user:
            bubble = tk.Frame(row, bg=COLORS["accent"])
            bubble.pack(side="right")
        else:
            icon = tk.Label(row, text="🤖", font=("Segoe UI Emoji", 16),
                           bg=COLORS["card"])
            icon.pack(side="left", anchor="n", padx=(0,8))
            bubble = tk.Frame(row, bg=COLORS["card2"])
            bubble.pack(side="left")

        lbl = tk.Label(bubble, text=text, font=("Segoe UI", 12),
                       bg=bubble.cget("bg"),
                       fg="white" if is_user else COLORS["text"],
                       wraplength=550, justify="left", padx=14, pady=10)
        lbl.pack()

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def send_message(self):
        msg = self.input_var.get().strip()
        if not msg: return
        self.input_var.set("")
        self._add_msg("user", msg)
        self.send_btn.config(state="disabled", text="  Thinking…")
        threading.Thread(target=self._call_ai, args=(msg,), daemon=True).start()

    def _call_ai(self, user_msg):
        expenses = self.app.data["expenses"]
        budget   = self.app.data.get("budget", {})

        # Build context
        now = datetime.datetime.now()
        this_month = [e for e in expenses
                      if e["date"].startswith(f"{now.year}-{now.month:02d}")]
        total_month = sum(e["amount"] for e in this_month)
        total_all   = sum(e["amount"] for e in expenses)
        cat_totals  = {}
        for e in expenses:
            cat_totals[e.get("category","Other")] = cat_totals.get(e.get("category","Other"),0)+e["amount"]
        recent_5 = sorted(expenses, key=lambda e: e["date"], reverse=True)[:5]

        context = f"""You are a friendly, expert financial advisor AI assistant embedded in a personal expense tracking app.

USER'S FINANCIAL DATA:
- Total expenses (all time): ${total_all:.2f}
- This month's total: ${total_month:.2f}
- Number of expenses this month: {len(this_month)}
- Total expenses recorded: {len(expenses)}

SPENDING BY CATEGORY (all time):
{json.dumps(cat_totals, indent=2)}

MONTHLY BUDGETS SET:
{json.dumps(budget, indent=2)}

RECENT 5 EXPENSES:
{json.dumps(recent_5, indent=2)}

Be concise, friendly, and give specific, actionable advice based on the actual data.
Use emojis occasionally to make responses engaging. Keep responses under 250 words."""

        self.app.ai_messages.append({"role": "user", "content": user_msg})

        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "system": context,
                    "messages": self.app.ai_messages[-10:],
                },
                timeout=30
            )
            data = resp.json()
            if "content" in data and data["content"]:
                reply = data["content"][0]["text"]
            else:
                reply = f"Hmm, I couldn't get a response. ({data.get('error',{}).get('message','Unknown error')})"
        except Exception as ex:
            reply = f"⚠️ Connection error: {str(ex)}\n\nMake sure you're connected to the internet."

        self.app.ai_messages.append({"role": "assistant", "content": reply})
        self.after(0, lambda: self._ai_done(reply))

    def _ai_done(self, reply):
        self._add_msg("assistant", reply)
        self.send_btn.config(state="normal", text="  Send  ➤")

    def refresh(self): pass


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ExpenseApp()
    app.mainloop()
