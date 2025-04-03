"""
Expense Entry Section Module

Defines the ExpenseEntryFrame for entering, updating, deleting, viewing, and searching expenses.
Also provides enhanced receipt upload functionality that automatically extracts data from a receipt.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkcalendar import DateEntry
from typing import Any

from ml import categorize_expense
from receipt_capture import process_receipt

# UI Constants
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#3498DB"


class ExpenseEntryFrame(ttk.Frame):
    def __init__(self, parent: tk.Widget, db: Any, *args, **kwargs) -> None:
        """
        Initialize the ExpenseEntryFrame with database reference and create UI widgets.
        """
        super().__init__(parent, padding="20", *args, **kwargs)
        self.db = db
        self.create_widgets()

    def create_widgets(self) -> None:
        """
        Create and layout all UI widgets for expense entry and management.
        """
        # Header Title
        title = ttk.Label(self, text="Add Expense", font=("Segoe UI", 16, "bold"), foreground=PRIMARY_COLOR)
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Create labels for input fields
        labels = ["Date:", "Expense Type:", "Amount (₹):", "Description:"]
        for idx, text in enumerate(labels, start=1):
            ttk.Label(self, text=text, foreground=TEXT_COLOR).grid(
                row=idx, column=0, sticky="e", padx=5, pady=5
            )

        # Date Entry
        self.date_var = tk.StringVar()
        self.date_entry = DateEntry(
            self, textvariable=self.date_var, width=25,
            background="white", foreground=TEXT_COLOR, date_pattern="yyyy-mm-dd"
        )
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        # Expense Category Combobox
        self.category_combo = ttk.Combobox(self, width=23)
        self.category_combo["values"] = [
            "Food", "Transport", "Housing", "Utilities",
            "Entertainment", "Healthcare", "Education", "Shopping", "Insurance", "Other"
        ]
        self.category_combo.grid(row=2, column=1, padx=5, pady=5)

        # Amount Entry
        self.amount_entry = ttk.Entry(self, width=25)
        self.amount_entry.grid(row=3, column=1, padx=5, pady=5)

        # Description Entry
        self.description_entry = ttk.Entry(self, width=25)
        self.description_entry.grid(row=4, column=1, padx=5, pady=5)

        # Buttons for operations
        ttk.Button(self, text="Add Expense", command=self.add_expense).grid(
            row=5, column=0, columnspan=2, pady=10
        )
        ttk.Button(self, text="Upload Receipt", command=self.upload_receipt).grid(
            row=6, column=0, columnspan=2, pady=5
        )
        ttk.Button(self, text="View Expenses", command=self.view_expenses).grid(
            row=7, column=0, columnspan=2, pady=10
        )
        ttk.Button(self, text="Search Expense", command=self.search_expense).grid(
            row=8, column=0, columnspan=2, pady=5
        )

        # Delete Expense Section
        ttk.Label(self, text="Expense ID to Delete:", foreground=TEXT_COLOR).grid(
            row=9, column=0, sticky="e", padx=5, pady=5
        )
        self.delete_id_entry = ttk.Entry(self, width=25)
        self.delete_id_entry.grid(row=9, column=1, padx=5, pady=5)
        ttk.Button(self, text="Delete Expense", command=self.delete_expense).grid(
            row=10, column=0, columnspan=2, pady=10
        )

        # Update Expense Section
        ttk.Label(self, text="Expense ID to Update:", foreground=TEXT_COLOR).grid(
            row=11, column=0, sticky="e", padx=5, pady=5
        )
        self.update_id_entry = ttk.Entry(self, width=25)
        self.update_id_entry.grid(row=11, column=1, padx=5, pady=5)
        ttk.Button(self, text="Update Expense", command=self.update_expense).grid(
            row=12, column=0, columnspan=2, pady=10
        )

        # Exit Application Button
        ttk.Button(self, text="Exit", command=self.exit_app).grid(
            row=13, column=0, columnspan=2, pady=(20, 5)
        )

    def add_expense(self) -> None:
        """
        Add a new expense to the database using input from the UI.
        """
        date_val = self.date_var.get()
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")
            return

        description = self.description_entry.get()
        # Determine category: use selected value or auto-categorize based on description.
        category = self.category_combo.get().strip() or categorize_expense(description)
        self.category_combo.set(category)

        # Convert amount to INR (if conversion logic is needed)
        amount_in_inr = self.convert_to_inr(amount)

        if self.db.insert_expense(date_val, amount_in_inr, category, description):
            messagebox.showinfo("Success", "Expense added successfully!")
            self.clear_fields()
        else:
            messagebox.showerror("Error", "Failed to add expense.")

    def clear_fields(self) -> None:
        """
        Clear all input fields after a successful operation.
        """
        self.date_var.set("")
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.description_entry.delete(0, tk.END)

    def upload_receipt(self) -> None:
        """
        Open a file dialog to select a receipt image, extract data using OCR, and optionally add the expense automatically.
        """
        file_path = filedialog.askopenfilename(
            title="Select Receipt Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if not file_path:
            return

        receipt_data = process_receipt(file_path)
        if receipt_data:
            # Populate fields with extracted data if available
            if "amount" in receipt_data:
                self.amount_entry.delete(0, tk.END)
                # Optionally, remove currency symbol if needed
                self.amount_entry.insert(0, str(receipt_data["amount"]))
            if "date" in receipt_data:
                self.date_var.set(receipt_data["date"])
            if "description" in receipt_data:
                self.description_entry.delete(0, tk.END)
                self.description_entry.insert(0, receipt_data["description"])
            if "category" in receipt_data:
                self.category_combo.set(receipt_data["category"])

            # Ask user if they want to automatically add the expense
            auto_add = messagebox.askyesno(
                "Add Expense", "Receipt data extracted. Do you want to automatically add this expense?"
            )
            if auto_add:
                try:
                    amount = float(self.amount_entry.get())
                except ValueError:
                    messagebox.showerror("Error", "Extracted amount is invalid.")
                    return
                amount_in_inr = self.convert_to_inr(amount)
                success = self.db.insert_expense(
                    self.date_var.get(),
                    amount_in_inr,
                    self.category_combo.get(),
                    self.description_entry.get()
                )
                if success:
                    messagebox.showinfo("Success", "Expense added from receipt!")
                    self.clear_fields()
                else:
                    messagebox.showerror("Error", "Failed to add expense from receipt.")
        else:
            messagebox.showwarning("OCR Failed", "Could not extract data from the receipt.")

    def view_expenses(self) -> None:
        """
        Open a new window displaying all stored expenses in a sortable table.
        """
        data = self.db.get_expenses()
        if not data:
            messagebox.showinfo("View Expenses", "No expense data available.")
            return

        view_win = tk.Toplevel(self)
        view_win.title("View Expenses")
        columns = ("ID", "Date", "Amount (₹)", "Category", "Description")
        tree = ttk.Treeview(view_win, columns=columns, show="headings")

        for col, width in [("ID", 50), ("Date", 100), ("Amount (₹)", 100), ("Category", 100), ("Description", 250)]:
            tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(tree, c, False))
            tree.column(col, width=width)

        for row in data:
            tree.insert("", tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(view_win, orient="vertical", command=tree.yview)
        tree.configure(yscroll=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    def sort_treeview(self, tv: ttk.Treeview, col: str, reverse: bool) -> None:
        """Sort the contents of a treeview by a given column."""
        items = [(tv.set(k, col), k) for k in tv.get_children('')]
        try:
            items.sort(key=lambda t: float(t[0].replace("₹", "").replace(",", "")), reverse=reverse)
        except ValueError:
            items.sort(reverse=reverse)
        for idx, (val, k) in enumerate(items):
            tv.move(k, '', idx)
        tv.heading(col, command=lambda: self.sort_treeview(tv, col, not reverse))

    def search_expense(self) -> None:
        """Search for expenses containing a user-specified keyword in the description and display the results in a new window."""
        keyword = simpledialog.askstring("Search Expense", "Enter keyword:")
        if not keyword:
            return

        data = self.db.get_expenses()
        filtered = [r for r in data if keyword.lower() in r[4].lower()]
        if not filtered:
            messagebox.showinfo("Search", f"No expenses found containing '{keyword}'.")
            return

        result_win = tk.Toplevel(self)
        result_win.title(f"Search Results for '{keyword}'")
        columns = ("ID", "Date", "Amount (₹)", "Category", "Description")
        tree = ttk.Treeview(result_win, columns=columns, show="headings")

        for col, width in [("ID", 50), ("Date", 100), ("Amount (₹)", 100), ("Category", 100), ("Description", 250)]:
            tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(tree, c, False))
            tree.column(col, width=width)

        for row in filtered:
            tree.insert("", tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(result_win, orient="vertical", command=tree.yview)
        tree.configure(yscroll=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    def delete_expense(self) -> None:
        """Delete an expense record based on the provided Expense ID."""
        exp_id_str = self.delete_id_entry.get().strip()
        if not exp_id_str:
            messagebox.showerror("Error", "Please enter a valid Expense ID.")
            return

        try:
            exp_id = int(exp_id_str)
        except ValueError:
            messagebox.showerror("Error", "Expense ID must be an integer.")
            return

        if self.db.delete_expense(exp_id):
            messagebox.showinfo("Success", f"Expense {exp_id} deleted successfully!")
            self.delete_id_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"Failed to delete expense {exp_id}.")

    def update_expense(self) -> None:
        """Update an existing expense record using new data from the input fields."""
        exp_id_str = self.update_id_entry.get().strip()
        if not exp_id_str:
            messagebox.showerror("Error", "Please enter a valid Expense ID to update.")
            return

        try:
            exp_id = int(exp_id_str)
        except ValueError:
            messagebox.showerror("Error", "Expense ID must be an integer.")
            return

        date_val = self.date_var.get()
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")
            return

        description = self.description_entry.get()
        category = self.category_combo.get().strip() or categorize_expense(description)
        self.category_combo.set(category)

        amount_in_inr = self.convert_to_inr(amount)
        if self.db.update_expense(exp_id, date_val, amount_in_inr, category, description):
            messagebox.showinfo("Success", f"Expense {exp_id} updated successfully!")
            self.update_id_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"Failed to update expense {exp_id}.")

    def exit_app(self) -> None:
        """Exit the application by destroying the top-level window."""
        self.winfo_toplevel().destroy()

    def convert_to_inr(self, amount: float) -> float:
        """Convert a given amount to Indian Rupees (₹)."""
        return round(amount, 2)
