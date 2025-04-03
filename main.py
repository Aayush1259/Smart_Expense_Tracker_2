"""
Main Module

The main entry point of the Expense Tracker application.
Integrates expense entry, analytics, reporting, data import/export, backup/restore,
expense comparison, and other core features.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

from database import Database
from entry_section import ExpenseEntryFrame
from analytics_section import AnalyticsFrame
from report import generate_pdf_report, generate_html_report
from ml import compare_expenses


class ToolTip:
    """
    A simple tooltip class for additional help on UI elements.
    """
    def __init__(self, widget: tk.Widget, text: str = 'Info') -> None:
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None) -> None:
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += cy + self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID,
                        borderwidth=1, font=("Segoe UI", 10))
        label.pack(ipadx=1)

    def hide_tip(self, event=None) -> None:
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def toggle_theme(style: ttk.Style, current_theme: tk.StringVar) -> None:
    """
    Toggle between Light and Dark themes for the application.
    """
    if current_theme.get() == "Light":
        style.configure("TFrame", background="#1F1F1F")
        style.configure("TLabel", background="#1F1F1F", foreground="#E0E0E0", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=7,
                        background="#3A3A3A", foreground="#E0E0E0")
        style.configure("TEntry", font=("Segoe UI", 11), fieldbackground="#3A3A3A", foreground="#E0E0E0")
        style.configure("TCombobox", font=("Segoe UI", 11), fieldbackground="#3A3A3A", foreground="#E0E0E0")
        current_theme.set("Dark")
    else:
        style.configure("TFrame", background="#FFFFFF")
        style.configure("TLabel", background="#FFFFFF", foreground="#2C3E50", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=7,
                        background="#F0F0F0", foreground="#2C3E50")
        style.configure("TEntry", font=("Segoe UI", 11), fieldbackground="#FFFFFF", foreground="#2C3E50")
        style.configure("TCombobox", font=("Segoe UI", 11), fieldbackground="#FFFFFF", foreground="#2C3E50")
        current_theme.set("Light")


def show_about() -> None:
    """
    Display an 'About' dialog with application details.
    """
    messagebox.showinfo(
        "About",
        ("Expense Tracker\nVersion 2.0\nA modern, optimized expense tracker with enhanced reporting, "
        "advanced ML forecasting, and bank integration features.\n\n"
        "Note: Ensure Tesseract OCR is installed and added to your system PATH for receipt processing.")
    )


def import_data(db: Database) -> None:
    """
    Open a file dialog to import expense data from a CSV or Excel file.
    """
    file_path = filedialog.askopenfilename(
        title="Import Data",
        filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")]
    )
    if not file_path:
        return
    try:
        # Import functions are expected to return a boolean
        from import_export import Import
        importer = Import(db)
        success = importer.from_csv(file_path) if file_path.endswith(".csv") else importer.from_excel(file_path)
    except Exception as e:
        messagebox.showerror("Import Error", f"Failed to import data: {e}")
        return
    messagebox.showinfo("Import Data", "Data imported successfully!" if success else "Data import failed.")


def backup_data() -> None:
    """
    Open a file dialog to backup the database.
    """
    backup_file = filedialog.asksaveasfilename(
        title="Backup Database", defaultextension=".db", filetypes=[("DB Files", "*.db")]
    )
    if not backup_file:
        return
    try:
        from import_export import BackupRestore
        success = BackupRestore.backup_database("expense_tracker.db", backup_file)
    except Exception as e:
        messagebox.showerror("Backup Error", f"Failed to backup database: {e}")
        return
    messagebox.showinfo("Backup", "Database backup successful!" if success else "Database backup failed.")


def restore_data() -> None:
    """
    Open a file dialog to restore the database from a backup.
    """
    backup_file = filedialog.askopenfilename(
        title="Restore Database", filetypes=[("DB Files", "*.db")]
    )
    if not backup_file:
        return
    try:
        from import_export import BackupRestore
        success = BackupRestore.restore_database(backup_file, "expense_tracker.db")
    except Exception as e:
        messagebox.showerror("Restore Error", f"Failed to restore database: {e}")
        return
    messagebox.showinfo("Restore", "Database restore successful! Please restart the application." if success else "Database restore failed.")


def export_data_menu() -> None:
    """
    Export expense data to a CSV or Excel file through a file dialog.
    """
    db = Database()
    from export import Export
    data = pd.DataFrame(
        db.get_expenses(), columns=["id", "date", "amount", "category", "description"]
    )
    if data.empty:
        messagebox.showinfo("Export Data", "No data available to export.")
        return
    file_path = filedialog.asksaveasfilename(
        title="Export Data", defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")]
    )
    if not file_path:
        return
    exporter = Export(db)
    success = exporter.to_excel(file_path) if file_path.endswith(".xlsx") else exporter.to_csv(file_path)
    messagebox.showinfo("Export Data", "Data exported successfully!" if success else "Export failed.")


def generate_pdf_report_cmd() -> None:
    """
    Generate a PDF report of expense data through a file dialog.
    """
    db = Database()
    from report import generate_pdf_report
    data = pd.DataFrame(
        db.get_expenses(), columns=["id", "date", "amount", "category", "description"]
    )
    if data.empty:
        messagebox.showinfo("Report", "No data available.")
        return
    file_path = filedialog.asksaveasfilename(
        title="Save PDF Report", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path:
        return
    success = generate_pdf_report(data, file_path)
    messagebox.showinfo("Report", "PDF report generated successfully!" if success else "PDF report generation failed.")


def generate_html_report_cmd() -> None:
    """
    Generate an HTML report of expense data through a file dialog.
    """
    db = Database()
    from report import generate_html_report
    data = pd.DataFrame(
        db.get_expenses(), columns=["id", "date", "amount", "category", "description"]
    )
    if data.empty:
        messagebox.showinfo("Report", "No data available.")
        return
    html_content = generate_html_report(data)
    file_path = filedialog.asksaveasfilename(
        title="Save HTML Report", defaultextension=".html", filetypes=[("HTML Files", "*.html")]
    )
    if not file_path:
        return
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    messagebox.showinfo("Report", "HTML report generated successfully!")


def compare_expense() -> None:
    """
    Compare expenses between the last two months and display a summary.
    """
    db = Database()
    from ml import compare_expenses
    data = pd.DataFrame(
        db.get_expenses(), columns=["id", "date", "amount", "category", "description"]
    )
    result = compare_expenses(data)
    messagebox.showinfo("Expense Comparison", result)


def main() -> None:
    """
    Main function to initialize and run the Expense Tracker application.
    """
    root = tk.Tk()
    root.title("Expense Tracker")
    root.geometry("1200x700")

    # Configure UI theme
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#FFFFFF")
    style.configure("TLabel", background="#FFFFFF", foreground="#2C3E50", font=("Segoe UI", 11))
    style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=7)
    style.configure("TEntry", font=("Segoe UI", 11))
    style.configure("TCombobox", font=("Segoe UI", 11))
    current_theme = tk.StringVar(value="Light")

    # Build Menu Bar
    menubar = tk.Menu(root)
    
    # File Menu
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    
    # Data Menu: Import, Export, Backup, Restore
    data_menu = tk.Menu(menubar, tearoff=0)
    data_menu.add_command(label="Import Data", command=lambda: import_data(Database()))
    data_menu.add_command(label="Export Data", command=export_data_menu)
    data_menu.add_command(label="Backup DB", command=backup_data)
    data_menu.add_command(label="Restore DB", command=restore_data)
    menubar.add_cascade(label="Data", menu=data_menu)
    
    # Reports Menu
    report_menu = tk.Menu(menubar, tearoff=0)
    report_menu.add_command(label="Generate PDF Report", command=generate_pdf_report_cmd)
    report_menu.add_command(label="Generate HTML Report", command=generate_html_report_cmd)
    menubar.add_cascade(label="Reports", menu=report_menu)
    
    # View Menu
    view_menu = tk.Menu(menubar, tearoff=0)
    view_menu.add_command(label="Toggle Theme", command=lambda: toggle_theme(style, current_theme))
    menubar.add_cascade(label="View", menu=view_menu)
    
    # Help Menu
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="About", command=show_about)
    menubar.add_cascade(label="Help", menu=help_menu)
    
    root.config(menu=menubar)
    
    # Main content frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    db = Database()
    # Import Expense Entry and Analytics Frames
    entry_frame = ExpenseEntryFrame(main_frame, db)
    entry_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
    
    analytics_frame = AnalyticsFrame(main_frame, db)
    analytics_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    main()
