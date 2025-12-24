from tkinter import ttk

class AppTheme:
    BG = "#f4f6f9"
    CARD = "#ffffff"
    PRIMARY = "#3f51b5"
    SECONDARY = "#5c6bc0"
    TEXT = "#333"
    MUTED = "#777"
    BORDER = "#e0e0e0"

    @staticmethod
    def apply(root):
        style = ttk.Style(root)
        style.theme_use("default")

        # Treeview
        style.configure(
            "Treeview",
            background="white",
            foreground=AppTheme.TEXT,
            rowheight=36,
            fieldbackground="white",
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold"),
            background="#f0f0f0",
            foreground=AppTheme.TEXT
        )

        style.map(
            "Treeview",
            background=[("selected", "#c5cae9")],
            foreground=[("selected", "#000")]
        )
