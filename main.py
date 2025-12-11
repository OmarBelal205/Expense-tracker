import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import uuid
from collections import defaultdict

# --- Configuration ---
EXPENSES_FILE = "expenses.json"
CATEGORIES_FILE = "categories.json"
DEFAULT_CATEGORIES = ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Healthcare", "Other"]
# ---------------------

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Comprehensive Financial Tracker")
        self.root.geometry("1000x750")
        self.root.configure(bg="#e8e8e8")
        
        self.expenses = self.load_expenses()
        self.categories = self.load_categories()
        
        # Unique ID for tracking expenses during deletion/editing
        self.next_id = len(self.expenses) + 1 if self.expenses else 1
        
        self.create_widgets()
        self.refresh_expense_list()
        self.update_summary()
    
    # --- Data Persistence Methods ---
    
    def load_expenses(self):
        """
        Load expenses from file, ensuring each has a unique ID and a 'type' key.
        This handles migration for old files that lack the 'id' or 'type' key.
        """
        data = []
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    # Handle case where file is empty or corrupted
                    return []
        
        needs_save = False
        
        for exp in data:
            # 1. Ensure unique ID (from previous update)
            if 'id' not in exp:
                exp['id'] = str(uuid.uuid4())
                needs_save = True
                
            # 2. Add 'type' key for old entries (THE FIX FOR KeyError: 'type')
            if 'type' not in exp:
                exp['type'] = 'Expense' # Old entries were always Expenses
                needs_save = True
                
        # If any data was updated (migrated), save it back immediately
        if needs_save:
            self.expenses = data # Temporarily set to save
            self.save_expenses()
            
        return data

    def load_categories(self):
        """Load custom categories from file or use defaults."""
        if os.path.exists(CATEGORIES_FILE):
            with open(CATEGORIES_FILE, 'r') as f:
                return json.load(f)
        return DEFAULT_CATEGORIES
    
    def save_expenses(self):
        """Save expenses to file"""
        with open(EXPENSES_FILE, 'w') as f:
            json.dump(self.expenses, f, indent=2)

    def save_categories(self):
        """Save custom categories to file"""
        with open(CATEGORIES_FILE, 'w') as f:
            json.dump(self.categories, f, indent=2)

    # --- UI Creation ---

    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Style Configuration
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", font=("Arial", 9))
        style.map("Treeview", background=[('selected', '#347083')])

        # Main Title
        title = tk.Label(self.root, text="💰 Comprehensive Financial Tracker", 
                         font=("Arial", 22, "bold"), bg="#e8e8e8", fg="#1a1a1a")
        title.pack(pady=10)
        
        # --- Input Frame (Transaction Entry) ---
        input_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.RIDGE, borderwidth=1)
        input_frame.pack(pady=5, padx=20, fill=tk.X)
        
        tk.Label(input_frame, text="Date:", font=("Arial", 10), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = tk.Entry(input_frame, font=("Arial", 10), width=12)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(input_frame, text="Amount ($):", font=("Arial", 10), bg="#ffffff").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.amount_entry = tk.Entry(input_frame, font=("Arial", 10), width=12)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(input_frame, text="Category:", font=("Arial", 10), bg="#ffffff").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.category_entry = ttk.Combobox(input_frame, font=("Arial", 10), width=15, values=self.categories)
        self.category_entry.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Label(input_frame, text="Description:", font=("Arial", 10), bg="#ffffff").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.description_entry = tk.Entry(input_frame, font=("Arial", 10), width=30)
        self.description_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        
        # Transaction Type (Income/Expense)
        self.type_var = tk.StringVar(value="Expense")
        tk.Radiobutton(input_frame, text="Expense", variable=self.type_var, value="Expense", bg="#ffffff", fg="#f44336").grid(row=1, column=4, padx=5, pady=5)
        tk.Radiobutton(input_frame, text="Income", variable=self.type_var, value="Income", bg="#ffffff", fg="#4CAF50").grid(row=1, column=5, padx=5, pady=5)
        
        # Action Buttons
        button_frame = tk.Frame(input_frame, bg="#ffffff")
        button_frame.grid(row=2, column=0, columnspan=6, pady=10)
        
        add_btn = tk.Button(button_frame, text="Add Transaction", font=("Arial", 11, "bold"),
                            bg="#2196F3", fg="white", command=self.add_transaction, 
                            cursor="hand2", padx=15, pady=5)
        add_btn.pack(side=tk.LEFT, padx=10)

        self.edit_btn = tk.Button(button_frame, text="Edit Selected", font=("Arial", 11, "bold"),
                                  bg="#FF9800", fg="white", command=self.open_edit_window,
                                  cursor="hand2", padx=15, pady=5, state=tk.DISABLED) # Start disabled
        self.edit_btn.pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Manage Categories", font=("Arial", 11),
                  bg="#607D8B", fg="white", command=self.open_category_manager,
                  cursor="hand2", padx=15, pady=5).pack(side=tk.LEFT, padx=10)

        # --- Filter Frame ---
        filter_frame = tk.Frame(self.root, bg="#f5f5f5", relief=tk.FLAT)
        filter_frame.pack(pady=5, padx=20, fill=tk.X)
        
        tk.Label(filter_frame, text="Filter By:", font=("Arial", 10, "bold"), bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
        
        self.filter_category_var = tk.StringVar(value="All Categories")
        filter_categories = ["All Categories"] + [c.capitalize() for c in self.categories]
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, 
                                                  values=filter_categories, font=("Arial", 10), width=15)
        self.filter_category_combo.pack(side=tk.LEFT, padx=10)
        self.filter_category_combo.bind("<<ComboboxSelected>>", self.filter_expenses)

        tk.Label(filter_frame, text="Type:", font=("Arial", 10), bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
        self.filter_type_var = tk.StringVar(value="All Types")
        filter_types = ["All Types", "Expense", "Income"]
        self.filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var,
                                              values=filter_types, font=("Arial", 10), width=10)
        self.filter_type_combo.pack(side=tk.LEFT, padx=10)
        self.filter_type_combo.bind("<<ComboboxSelected>>", self.filter_expenses)
        
        # --- Expense List Frame ---
        list_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.RIDGE, borderwidth=1)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Treeview for transactions
        columns = ("ID", "Type", "Date", "Amount", "Category", "Description")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Amount", text="Amount ($)")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Description", text="Description")
        
        self.tree.column("ID", width=0, stretch=tk.NO) # Hidden ID column
        self.tree.column("Type", width=70, anchor=tk.CENTER)
        self.tree.column("Date", width=120, anchor=tk.CENTER)
        self.tree.column("Amount", width=100, anchor=tk.E)
        self.tree.column("Category", width=120, anchor=tk.CENTER)
        self.tree.column("Description", width=350, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.open_edit_window) # Double click to edit
        
        # Delete button
        delete_btn = tk.Button(list_frame, text="Delete Selected", font=("Arial", 10),
                              bg="#f44336", fg="white", command=self.delete_expense,
                              cursor="hand2", padx=10, pady=5)
        delete_btn.pack(pady=5)
        
        # --- Summary Frame ---
        summary_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.RIDGE, borderwidth=1)
        summary_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(summary_frame, text="Financial Summary", font=("Arial", 14, "bold"),
                 bg="#ffffff", fg="#333").pack(pady=5)
        
        self.summary_label = tk.Label(summary_frame, text="", font=("Arial", 10),
                                      bg="#ffffff", justify=tk.LEFT, height=8)
        self.summary_label.pack(pady=5, padx=10, fill=tk.X)
    
    # --- Transaction Management Methods ---

    def add_transaction(self):
        """Add a new expense or income transaction."""
        try:
            amount = float(self.amount_entry.get())
            category = self.category_entry.get()
            description = self.description_entry.get()
            date_str = self.date_entry.get()
            trans_type = self.type_var.get()

            if amount <= 0:
                messagebox.showwarning("Invalid Amount", "Amount must be positive.")
                return

            if not category or not description:
                messagebox.showwarning("Missing Info", "Please select a category and enter a description.")
                return
            
            try:
                # Simple date validation (only accept YYYY-MM-DD)
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format.")
                return
            
            # Use UUID for a unique, collision-proof ID
            unique_id = str(uuid.uuid4())
            
            transaction = {
                "id": unique_id,
                "type": trans_type,
                "amount": amount,
                "category": category.lower(),
                "description": description,
                "date": date_str
            }
            
            self.expenses.append(transaction)
            self.save_expenses()
            
            # Clear entries
            self.amount_entry.delete(0, tk.END)
            self.category_entry.set("")
            self.description_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            
            self.refresh_expense_list()
            self.update_summary()
            
            messagebox.showinfo("Success", f"{trans_type} of ${amount:.2f} added!")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid numeric amount.")
    
    def on_tree_select(self, event):
        """Enable or disable the Edit button based on selection."""
        if self.tree.selection():
            self.edit_btn.config(state=tk.NORMAL)
        else:
            self.edit_btn.config(state=tk.DISABLED)

    def open_edit_window(self, event=None):
        """Open a new window to edit the selected expense."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a transaction to edit.")
            return

        item = self.tree.item(selected[0])
        trans_id = item['values'][0] # Get the unique ID from the hidden column

        # Find the original transaction object
        original_trans = next((exp for exp in self.expenses if exp['id'] == trans_id), None)
        
        if not original_trans:
            messagebox.showerror("Error", "Transaction not found.")
            return

        # --- Create Edit Window ---
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Edit {original_trans['type']} (ID: {trans_id[:8]})")
        edit_win.transient(self.root) # Keep on top of main window
        edit_win.grab_set()          # Modal window
        
        tk.Label(edit_win, text=f"Editing {original_trans['type']}").grid(row=0, column=0, columnspan=2, pady=10)

        # Fields for editing
        fields = ["Date", "Amount", "Category", "Description", "Type"]
        entries = {}
        for i, field in enumerate(fields):
            tk.Label(edit_win, text=f"{field}:").grid(row=i+1, column=0, padx=10, pady=5, sticky="e")
            
            if field == "Category":
                entry = ttk.Combobox(edit_win, values=self.categories, width=30)
                entry.set(original_trans['category'].capitalize())
            elif field == "Type":
                type_var = tk.StringVar(value=original_trans['type'])
                tk.Radiobutton(edit_win, text="Expense", variable=type_var, value="Expense").grid(row=i+1, column=1, sticky="w", padx=(0, 50))
                tk.Radiobutton(edit_win, text="Income", variable=type_var, value="Income").grid(row=i+1, column=1, sticky="w", padx=(50, 0))
                entries[field] = type_var
                continue
            else:
                entry = tk.Entry(edit_win, width=30)
                if field.lower() == 'amount':
                    entry.insert(0, f"{original_trans[field.lower()]:.2f}")
                elif field.lower() == 'date':
                    entry.insert(0, original_trans[field.lower()].split(" ")[0]) # Only date part
                else:
                    entry.insert(0, original_trans[field.lower()].capitalize())
            
            entry.grid(row=i+1, column=1, padx=10, pady=5, sticky="w")
            entries[field] = entry

        def save_edit():
            try:
                new_amount = float(entries['Amount'].get())
                new_date = entries['Date'].get()
                new_category = entries['Category'].get()
                new_description = entries['Description'].get()
                new_type = entries['Type'].get()

                if new_amount <= 0:
                    messagebox.showwarning("Invalid Amount", "Amount must be positive.")
                    return

                try:
                    # Date validation
                    datetime.strptime(new_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format.")
                    return

                # Update the original transaction object
                original_trans['amount'] = new_amount
                original_trans['date'] = new_date # Use only date for consistency
                original_trans['category'] = new_category.lower()
                original_trans['description'] = new_description
                original_trans['type'] = new_type

                self.save_expenses()
                self.refresh_expense_list()
                self.update_summary()
                edit_win.destroy()
                messagebox.showinfo("Success", "Transaction updated successfully!")

            except ValueError:
                messagebox.showerror("Invalid Input", "Please ensure Amount is a number.")

        tk.Button(edit_win, text="Save Changes", command=save_edit, bg="#4CAF50", fg="white").grid(row=len(fields)+1, column=0, columnspan=2, pady=15)
        edit_win.wait_window() # Wait until the edit window is closed


    def delete_expense(self):
        """Delete selected expense."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a transaction to delete.")
            return
        
        item = self.tree.item(selected[0])
        trans_id = item["values"][0] # Unique ID
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?"):
            
            # Find and remove expense using the unique ID
            self.expenses[:] = [exp for exp in self.expenses if exp['id'] != trans_id]
            
            self.save_expenses()
            self.refresh_expense_list()
            self.update_summary()
            self.edit_btn.config(state=tk.DISABLED)
            messagebox.showinfo("Deleted", "Transaction deleted successfully!")

    # --- Display & Filtering Methods ---

    def filter_expenses(self, event=None):
        """Filters the expenses list based on selected criteria."""
        category_filter = self.filter_category_var.get().lower()
        type_filter = self.filter_type_var.get()
        
        filtered_list = self.expenses
        
        if category_filter != "all categories":
            filtered_list = [exp for exp in filtered_list if exp['category'] == category_filter]
        
        if type_filter != "All Types":
            filtered_list = [exp for exp in filtered_list if exp['type'] == type_filter]
            
        self.refresh_expense_list(filtered_list)

    def refresh_expense_list(self, expense_list=None):
        """Refresh the expense list display with the provided list (or all expenses)."""
        
        data_to_display = expense_list if expense_list is not None else self.expenses
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Sort by date (newest first)
        data_to_display.sort(key=lambda x: x['date'], reverse=True)
        
        for expense in data_to_display:
            trans_type = expense["type"]
            amount_display = f"${expense['amount']:.2f}"
            
            # Set tag for color coding
            tag = 'income' if trans_type == 'Income' else 'expense'
            self.tree.tag_configure('income', background='#e6ffe6') # Light green for income
            self.tree.tag_configure('expense', background='#ffe6e6') # Light red for expense

            self.tree.insert("", tk.END, tags=(tag,), values=(
                expense["id"],
                trans_type,
                expense["date"],
                amount_display,
                expense["category"].capitalize(),
                expense["description"]
            ))
            
    def update_summary(self):
        """Update summary statistics including income and net balance."""
        if not self.expenses:
            self.summary_label.config(text="No transactions recorded yet.")
            return
        
        total_income = sum(exp['amount'] for exp in self.expenses if exp['type'] == 'Income')
        total_expense = sum(exp['amount'] for exp in self.expenses if exp['type'] == 'Expense')
        net_balance = total_income - total_expense
        
        expense_categories = defaultdict(float)
        for exp in self.expenses:
            if exp['type'] == 'Expense':
                expense_categories[exp['category']] += exp['amount']
        
        # Determine the color for Net Balance
        net_balance_color = "#4CAF50" if net_balance >= 0 else "#f44336"
        
        summary_text = f"Total Income: **${total_income:.2f}**\n"
        summary_text += f"Total Expenses: **${total_expense:.2f}**\n"
        summary_text += f"Net Balance: **${net_balance:.2f}**\n\n"
        
        summary_text += "Expense Breakdown by Category:\n"
        if total_expense > 0:
            for cat, amount in sorted(expense_categories.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_expense) * 100
                summary_text += f" • {cat.capitalize()}: ${amount:.2f} ({percentage:.1f}%)\n"
        else:
            summary_text += " (No expenses recorded)\n"

        # Apply formatting to the Summary Label
        self.summary_label.config(text=summary_text)

        # To color the net balance, we'd typically use a Text widget or multiple Labels.
        # For simplicity with a single Label:
        colored_summary = f"Total Income: ${total_income:.2f}\n"
        colored_summary += f"Total Expenses: ${total_expense:.2f}\n"
        colored_summary += f"Net Balance: ${net_balance:.2f}\n\n"
        colored_summary += "Expense Breakdown by Category:\n"
        if total_expense > 0:
            for cat, amount in sorted(expense_categories.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_expense) * 100
                colored_summary += f" • {cat.capitalize()}: ${amount:.2f} ({percentage:.1f}%)\n"
        else:
            colored_summary += " (No expenses recorded)\n"
        
        self.summary_label.config(text=colored_summary)

    # --- Category Management ---

    def open_category_manager(self):
        """Open a window to add/remove custom categories."""
        cat_win = tk.Toplevel(self.root)
        cat_win.title("Manage Categories")
        cat_win.transient(self.root)
        cat_win.grab_set()

        # Frame for adding new category
        add_frame = tk.Frame(cat_win)
        add_frame.pack(padx=10, pady=10)
        
        tk.Label(add_frame, text="New Category Name:").pack(side=tk.LEFT)
        new_cat_entry = tk.Entry(add_frame, width=20)
        new_cat_entry.pack(side=tk.LEFT, padx=5)

        def add_category():
            new_cat = new_cat_entry.get().strip().lower()
            if new_cat and new_cat not in [c.lower() for c in self.categories]:
                self.categories.append(new_cat.capitalize())
                self.save_categories()
                category_listbox.insert(tk.END, new_cat.capitalize())
                self.update_category_comboboxes()
                new_cat_entry.delete(0, tk.END)
                messagebox.showinfo("Success", f"Category '{new_cat.capitalize()}' added.")
            elif new_cat:
                messagebox.showwarning("Exists", "Category already exists.")

        tk.Button(add_frame, text="Add", command=add_category).pack(side=tk.LEFT)

        # Listbox for existing categories
        tk.Label(cat_win, text="Existing Categories (Select to Remove):").pack(pady=(10, 5))
        category_listbox = tk.Listbox(cat_win, width=40, height=10)
        category_listbox.pack(padx=10)

        for cat in self.categories:
            category_listbox.insert(tk.END, cat.capitalize())

        def remove_category():
            selected = category_listbox.curselection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a category to remove.")
                return

            cat_to_remove = category_listbox.get(selected[0]).lower()

            if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove '{cat_to_remove.capitalize()}'?"):
                self.categories.remove(cat_to_remove.capitalize())
                self.save_categories()
                category_listbox.delete(selected[0])
                self.update_category_comboboxes()
                messagebox.showinfo("Removed", "Category removed.")

        tk.Button(cat_win, text="Remove Selected Category", command=remove_category, bg="#f44336", fg="white").pack(pady=10)
        cat_win.wait_window()

    def update_category_comboboxes(self):
        """Updates the values in all category comboboxes."""
        display_categories = [c.capitalize() for c in self.categories]
        self.category_entry['values'] = display_categories
        
        filter_categories = ["All Categories"] + display_categories
        self.filter_category_combo['values'] = filter_categories


def main():
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()