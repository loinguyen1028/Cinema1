# theme.py
import tkinter as tk
from tkinter import ttk


# ==================================================
# MOVIE MANAGER THEME (GLOBAL)
# ==================================================
COLORS = {
    "bg": "#0f172a",        # nền chính
    "panel": "#111827",     # sidebar / panel
    "card": "#1f2933",      # card / container
    "primary": "#facc15",   # màu nhấn (vàng)
    "text": "#e5e7eb",      # chữ chính
    "muted": "#9ca3af",     # chữ phụ
    "btn": "#2563eb",       # nút xanh
    "danger": "#dc2626",    # xóa / lỗi
    "success": "#22c55e",   # thành công
    "selected": "#334155"   # dòng được chọn
}


# ==================================================
# APPLY GLOBAL TTK STYLE
# ==================================================
def apply_ttk_theme():
    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Treeview",
        background=COLORS["panel"],
        fieldbackground=COLORS["panel"],
        foreground=COLORS["text"],
        rowheight=44,
        font=("Arial", 11),
        borderwidth=0
    )

    style.configure(
        "Treeview.Heading",
        background=COLORS["card"],
        foreground=COLORS["primary"],
        font=("Arial", 11, "bold"),
        relief="flat"
    )

    style.map(
        "Treeview",
        background=[("selected", COLORS["selected"])],
        foreground=[("selected", "#ffffff")]
    )

    return style


# ==================================================
# COMMON BUTTON STYLES
# ==================================================
BTN_PRIMARY = {
    "bg": COLORS["primary"],
    "fg": "#000",
    "relief": "flat",
    "cursor": "hand2"
}

BTN_BLUE = {
    "bg": COLORS["btn"],
    "fg": "white",
    "relief": "flat",
    "cursor": "hand2"
}

BTN_DANGER = {
    "bg": COLORS["danger"],
    "fg": "white",
    "relief": "flat",
    "cursor": "hand2"
}
