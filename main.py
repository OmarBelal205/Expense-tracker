import customtkinter as ctk
import tkinter as tk # Needed for standard widgets (Listbox)
from tkinter import messagebox, ttk # ttk needed for Treeview
import json
import os
from datetime import datetime
import uuid
from collections import defaultdict

# --- Configuration ---
EXPENSES_FILE = "expenses.json"
CATEGORIES_FILE = "categories.json"
DEFAULT_CATEGORIES = ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Healthcare", "Other"]

# CustomTkinter Appearance Settings
ctk.set_appearance_mode("Dark")  # Sleek dark theme
ctk.set_default_color_theme("blue") # Dark blue/purple primary color
# ---------------------

class FinancialTracker(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize main window
        self.title("💰 Comprehensive Financial Tracker - Dark Mode")
        self.geometry("1100x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # The List Frame gets expansion space
        
        self.expenses = self.load_expenses()
        self.categories = self.load_categories()
        
        # Modern fonts
        self.font_main = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        self.font_label = ctk.CTkFont(family="Segoe UI", size=12)
        self.font_stat = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        
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
                    return []
        
        needs_save = False
        
        for exp in data:
            # 1. Ensure unique ID
            if 'id' not in exp:
                exp['id'] = str(uuid.uuid4())
                needs_save = True
                
            # 2. Add 'type' key for old entries (Migration fix)
            if 'type' not in exp:
                exp['type'] = 'Expense' 
                needs_save = True
                
        if needs_save:
            self.expenses = data
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
        """Create all GUI widgets using CustomTkinter components."""
        
        # --- 1. Header Frame (Top Info) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        header_frame.grid_columnconfigure((0, 2), weight=1)

        ctk.CTkLabel(header_frame, text="💰 Financial Tracker Dashboard", font=self.font_main).grid(row=0, column=0, sticky="w")
        
        # Live Status Indicator
        self.status_dot = ctk.CTkLabel(header_frame, text=" • ", font=ctk.CTkFont(size=30), text_color="red")
        self.status_dot.grid(row=0, column=1, padx=5, sticky="e")
        ctk.CTkLabel(header_frame, text="Status: Connected", font=self.font_label).grid(row=0, column=2, padx=10, sticky="e")
        self.update_status_indicator(True) # Set initial status
        
        # --- 2. Input and Summary Card Frames (Card-based Layout) ---
        main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_content_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        main_content_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Input Card (Left)
        input_card = ctk.CTkFrame(main_content_frame, corner_radius=10, fg_color=("#EAEAEA", "#2B2B2B"))
        input_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(input_card, text="➕ Add New Transaction", font=self.font_main).pack(pady=10)
        
        self._create_input_fields(input_card)
        
        # Summary Card (Right)
        summary_card = ctk.CTkFrame(main_content_frame, corner_radius=10, fg_color=("#EAEAEA", "#2B2B2B"))
        summary_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(summary_card, text="📊 Financial Overview", font=self.font_main).pack(pady=10)
        
        self._create_summary_stats(summary_card)

        # --- 3. Filter/List/Action Frame ---
        list_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#EAEAEA", "#2B2B2B"))
        list_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        list_frame.grid_rowconfigure(2, weight=1)
        list_frame.grid_columnconfigure((0, 1), weight=1) # Need space for the treeview

        ctk.CTkLabel(list_frame, text="📜 Transaction History", font=self.font_main).grid(row=0, column=0, columnspan=3, pady=(10, 5))

        self._create_filter_section(list_frame)
        self._create_transaction_treeview(list_frame)
        self._create_action_buttons(list_frame)

    def _create_input_fields(self, master):
        """Creates input fields and buttons inside the Input Card."""
        
        grid_frame = ctk.CTkFrame(master, fg_color="transparent")
        grid_frame.pack(padx=20, pady=(0, 10), fill="x")
        grid_frame.columnconfigure(1, weight=1)

        # Date, Amount, Category, Description
        fields = [("🗓️ Date (YYYY-MM-DD):", "date"), ("💸 Amount ($):", "amount"), ("🏷️ Category:", "category"), ("📝 Description:", "description")]
        
        for i, (label_text, key) in enumerate(fields):
            ctk.CTkLabel(grid_frame, text=label_text, font=self.font_label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            
            if key == "category":
                self.category_entry = ctk.CTkComboBox(grid_frame, values=[c.capitalize() for c in self.categories], 
                                                      command=self.category_selected, width=200)
                self.category_entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
                # Set a default value if categories exist
                if self.categories:
                    self.category_entry.set(self.categories[0].capitalize()) 
            else:
                entry = ctk.CTkEntry(grid_frame, width=200)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
                setattr(self, f"{key}_entry", entry)

        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Transaction Type (Radio Buttons)
        self.type_var = ctk.StringVar(value="Expense")
        ctk.CTkLabel(grid_frame, text="✅ Type:", font=self.font_label).grid(row=len(fields), column=0, padx=10, pady=10, sticky="w")
        
        type_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
        type_frame.grid(row=len(fields), column=1, padx=10, pady=10, sticky="w")

        ctk.CTkRadioButton(type_frame, text="Expense", variable=self.type_var, value="Expense", border_color="#f44336").pack(side="left", padx=5)
        ctk.CTkRadioButton(type_frame, text="Income", variable=self.type_var, value="Income", border_color="#4CAF50").pack(side="left", padx=15)
        
        # Action Button (Custom button with hover effect)
        ctk.CTkButton(master, text="✨ ADD TRANSACTION", font=self.font_main, 
                      command=self.add_transaction, hover_color="#388E3C", 
                      fg_color="#4CAF50", height=40).pack(pady=10, padx=20, fill="x")

    def _create_summary_stats(self, master):
        """Creates the large stat boxes for the Summary Card."""
        
        stats_frame = ctk.CTkFrame(master, fg_color="transparent")
        stats_frame.pack(padx=10, pady=10, fill="both", expand=True)
        stats_frame.columnconfigure((0, 1), weight=1)
        
        # Net Balance Stat Box
        self.net_balance_box = self._create_stat_box(stats_frame, "Net Balance ⚖️", "$0.00", 0, 0, "#2196F3")
        
        # Total Income Stat Box
        self.income_box = self._create_stat_box(stats_frame, "Total Income 💰", "$0.00", 0, 1, "#4CAF50")
        
        # Total Expense Stat Box
        self.expense_box = self._create_stat_box(stats_frame, "Total Expenses 📉", "$0.00", 1, 0, "#f44336")
        
        # Summary text area (for breakdown)
        ctk.CTkLabel(stats_frame, text="Category Breakdown:", font=self.font_label).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 0))
        self.summary_text = ctk.CTkTextbox(stats_frame, height=100, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.summary_text.grid(row=3, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="ew")
        self.summary_text.configure(state="disabled") # Make it read-only


    def _create_stat_box(self, master, title, initial_value, row, col, color):
        """Helper to create a unified stat display box."""
        frame = ctk.CTkFrame(master, fg_color=color, corner_radius=10)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(frame, text=title, font=self.font_label, text_color="white").pack(padx=10, pady=(5, 0))
        value_label = ctk.CTkLabel(frame, text=initial_value, font=self.font_stat, text_color="white")
        value_label.pack(padx=10, pady=(0, 5))
        
        return value_label 

    def _create_filter_section(self, master):
        """Creates the filtering controls."""
        filter_frame = ctk.CTkFrame(master, fg_color="transparent")
        filter_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(filter_frame, text="🔎 Filter By:", font=self.font_label).pack(side="left", padx=(5, 10))
        
        # Category Filter
        self.filter_category_var = ctk.StringVar(value="All Categories")
        filter_categories = ["All Categories"] + [c.capitalize() for c in self.categories]
        self.filter_category_combo = ctk.CTkComboBox(filter_frame, variable=self.filter_category_var, 
                                                     values=filter_categories, font=self.font_label, 
                                                     command=self.filter_expenses, width=150)
        self.filter_category_combo.pack(side="left", padx=10)

        # Type Filter
        self.filter_type_var = ctk.StringVar(value="All Types")
        filter_types = ["All Types", "Expense", "Income"]
        self.filter_type_combo = ctk.CTkComboBox(filter_frame, variable=self.filter_type_var, 
                                                 values=filter_types, font=self.font_label, 
                                                 command=self.filter_expenses, width=120)
        self.filter_type_combo.pack(side="left", padx=10)

    def _create_transaction_treeview(self, master):
        """Creates the standard ttk Treeview and applies dark mode styling."""
        
        # --- 1. Apply TTK Theme Styling (Crucial for dark mode Treeview) ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b",  # CTk dark background
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        bordercolor="#3e3e3e")
        style.map('Treeview', background=[('selected', '#347083')]) 
        style.configure("Treeview.Heading", 
                        background="#3e3e3e", 
                        foreground="white",
                        font=self.font_label)

        # --- 2. Create the Treeview using standard ttk ---
        columns = ("ID", "Type", "Date", "Amount", "Category", "Description")
        self.tree = ttk.Treeview(master, columns=columns, show="headings", style="Treeview")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Amount", text="Amount ($)")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Description", text="Description")
        
        self.tree.column("ID", width=0, stretch=False)
        self.tree.column("Type", width=70, anchor=ctk.CENTER)
        self.tree.column("Date", width=120, anchor=ctk.CENTER)
        self.tree.column("Amount", width=100, anchor=ctk.E)
        self.tree.column("Category", width=120, anchor=ctk.CENTER)
        self.tree.column("Description", width=350, anchor=ctk.W)
        
        # Add scrollbar using CTkScrollbar
        scrollbar = ctk.CTkScrollbar(master, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid placement
        self.tree.grid(row=2, column=0, columnspan=2, padx=(10, 0), pady=10, sticky="nsew")
        scrollbar.grid(row=2, column=2, padx=(0, 10), pady=10, sticky="ns") 

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.open_edit_window) 
        
        # Bind for smooth scrolling
        self.tree.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _on_mouse_wheel(self, event):
        """Enables smooth mouse wheel scrolling for the Treeview."""
        if event.widget == self.tree:
            self.tree.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

    def _create_action_buttons(self, master):
        """Creates the action buttons (Edit, Delete, Manage Categories)."""
        
        action_frame = ctk.CTkFrame(master, fg_color="transparent")
        action_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")
        action_frame.columnconfigure((0, 1, 2), weight=1)
        
        self.edit_btn = ctk.CTkButton(action_frame, text="✏️ Edit Selected", font=self.font_label,
                                      command=self.open_edit_window, hover_color="#E07C00", 
                                      fg_color="#FF9800", state="disabled")
        self.edit_btn.grid(row=0, column=0, padx=10, sticky="ew")

        ctk.CTkButton(action_frame, text="❌ Delete Selected", font=self.font_label,
                      command=self.delete_expense, hover_color="#B71C1C", 
                      fg_color="#f44336").grid(row=0, column=1, padx=10, sticky="ew")
        
        ctk.CTkButton(action_frame, text="⚙️ Manage Categories", font=self.font_label,
                      command=self.open_category_manager, hover_color="#455A64", 
                      fg_color="#607D8B").grid(row=0, column=2, padx=10, sticky="ew")

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
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format.")
                return
            
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
            self.amount_entry.delete(0, ctk.END)
            # self.category_entry.set(self.category_entry.get()) # Keep selected category for quick entry
            self.description_entry.delete(0, ctk.END)
            self.date_entry.delete(0, ctk.END)
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            
            self.refresh_expense_list()
            self.update_summary()
            
            messagebox.showinfo("Success", f"'{trans_type}' of ${amount:.2f} added!")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid numeric amount.")

    def on_tree_select(self, event):
        """Enable or disable the Edit button based on selection."""
        if self.tree.selection():
            self.edit_btn.configure(state="normal")
        else:
            self.edit_btn.configure(state="disabled")

    def open_edit_window(self, event=None):
        """Open a new CustomTkinter Toplevel window to edit the selected expense."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a transaction to edit.")
            return

        item = self.tree.item(selected[0])
        trans_id = item['values'][0]

        original_trans = next((exp for exp in self.expenses if exp['id'] == trans_id), None)
        
        if not original_trans:
            messagebox.showerror("Error", "Transaction not found.")
            return

        # --- Create Edit Window ---
        edit_win = ctk.CTkToplevel(self)
        edit_win.title(f"Edit {original_trans['type']} (ID: {trans_id[:8]})")
        edit_win.transient(self)
        edit_win.grab_set()
        
        ctk.CTkLabel(edit_win, text=f"✏️ Editing {original_trans['type']}", font=self.font_main).grid(row=0, column=0, columnspan=2, pady=10, padx=20)

        # Fields for editing
        fields = ["Date", "Amount", "Category", "Description", "Type"]
        entries = {}
        for i, field in enumerate(fields):
            ctk.CTkLabel(edit_win, text=f"{field}:", font=self.font_label).grid(row=i+1, column=0, padx=10, pady=5, sticky="e")
            
            if field == "Category":
                entry = ctk.CTkComboBox(edit_win, values=[c.capitalize() for c in self.categories], width=200)
                entry.set(original_trans['category'].capitalize())
            elif field == "Type":
                type_var = ctk.StringVar(value=original_trans['type'])
                radio_frame = ctk.CTkFrame(edit_win, fg_color="transparent")
                radio_frame.grid(row=i+1, column=1, sticky="w", padx=10)
                ctk.CTkRadioButton(radio_frame, text="Expense", variable=type_var, value="Expense", border_color="#f44336").pack(side="left", padx=5)
                ctk.CTkRadioButton(radio_frame, text="Income", variable=type_var, value="Income", border_color="#4CAF50").pack(side="left", padx=15)
                entries[field] = type_var
                continue
            else:
                entry = ctk.CTkEntry(edit_win, width=200)
                if field.lower() == 'amount':
                    entry.insert(0, f"{original_trans[field.lower()]:.2f}")
                elif field.lower() == 'date':
                    entry.insert(0, original_trans[field.lower()]) 
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
                    datetime.strptime(new_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format.")
                    return

                # Update the original transaction object
                original_trans['amount'] = new_amount
                original_trans['date'] = new_date 
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

        ctk.CTkButton(edit_win, text="💾 Save Changes", command=save_edit, hover_color="#388E3C", fg_color="#4CAF50").grid(row=len(fields)+1, column=0, columnspan=2, pady=15)
        edit_win.wait_window()


    def delete_expense(self):
        """Delete selected expense."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a transaction to delete.")
            return
        
        item = self.tree.item(selected[0])
        trans_id = item["values"][0] 
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?"):
            
            self.expenses[:] = [exp for exp in self.expenses if exp['id'] != trans_id]
            
            self.save_expenses()
            self.refresh_expense_list()
            self.update_summary()
            self.edit_btn.configure(state="disabled")
            messagebox.showinfo("Deleted", "Transaction deleted successfully!")

    # --- Display & Filtering Methods ---

    def filter_expenses(self, choice):
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
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        data_to_display.sort(key=lambda x: x['date'], reverse=True)
        
        for expense in data_to_display:
            trans_type = expense["type"]
            amount_display = f"${expense['amount']:,.2f}"
            
            self.tree.insert("", ctk.END, values=(
                expense["id"],
                trans_type,
                expense["date"],
                amount_display,
                expense["category"].capitalize(),
                expense["description"]
            ))
            
    def update_summary(self):
        """Update summary statistics including income, expense, and net balance."""
        
        total_income = sum(exp['amount'] for exp in self.expenses if exp['type'] == 'Income')
        total_expense = sum(exp['amount'] for exp in self.expenses if exp['type'] == 'Expense')
        net_balance = total_income - total_expense
    
        expense_categories = defaultdict(float)
        for exp in self.expenses:
            if exp['type'] == 'Expense':
                expense_categories[exp['category']] += exp['amount']
        
        # Build category breakdown text
        category_text = ""
        if total_expense > 0:
            for cat, amount in sorted(expense_categories.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_expense) * 100
                category_text += f" • {cat.capitalize()}: ${amount:,.2f} ({percentage:.1f}%)\n"
        else:
            category_text = " (No expenses recorded.)"
        
        # Update Stat Boxes
        self.income_box.configure(text=f"${total_income:,.2f}")
        self.expense_box.configure(text=f"${total_expense:,.2f}")
        self.net_balance_box.configure(text=f"${net_balance:,.2f}")
        
        # Color-coded status for Net Balance
        net_color = "#4CAF50" if net_balance >= 0 else "#f44336"
        self.net_balance_box.master.configure(fg_color=net_color)

        # Update Text Box for Breakdown
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", category_text)
        self.summary_text.configure(state="disabled")
        
    def update_status_indicator(self, is_connected):
        """Toggles the color of the connection status dot."""
        if is_connected:
            self.status_dot.configure(text_color="#4CAF50") # Green = Good/Online
        else:
            self.status_dot.configure(text_color="#f44336") # Red = Bad/Offline

    # --- Category Management ---

    def open_category_manager(self):
        """Open a Toplevel window to add/remove custom categories."""
        cat_win = ctk.CTkToplevel(self)
        cat_win.title("⚙️ Manage Categories")
        cat_win.transient(self)
        cat_win.grab_set()

        # Frame for adding new category
        add_frame = ctk.CTkFrame(cat_win, fg_color="transparent")
        add_frame.pack(padx=20, pady=10)
        
        ctk.CTkLabel(add_frame, text="✨ New Category:", font=self.font_label).pack(side="left", padx=5)
        new_cat_entry = ctk.CTkEntry(add_frame, width=150)
        new_cat_entry.pack(side="left", padx=5)

        def add_category():
            new_cat = new_cat_entry.get().strip().lower()
            if new_cat and new_cat.capitalize() not in self.categories:
                self.categories.append(new_cat.capitalize())
                self.categories.sort()
                self.save_categories()
                tk_listbox.delete(0, tk.END)
                for cat in self.categories:
                    tk_listbox.insert(ctk.END, cat.capitalize())
                self.update_category_comboboxes()
                new_cat_entry.delete(0, ctk.END)
                messagebox.showinfo("Success", f"Category '{new_cat.capitalize()}' added.")
            elif new_cat:
                messagebox.showwarning("Exists", "Category already exists.")

        ctk.CTkButton(add_frame, text="➕ Add", command=add_category, hover_color="#388E3C", fg_color="#4CAF50").pack(side="left", padx=5)

        # Listbox for existing categories
        ctk.CTkLabel(cat_win, text="📜 Existing Categories (Select to Remove):", font=self.font_label).pack(pady=(10, 5))
        
        category_list_frame = ctk.CTkScrollableFrame(cat_win, width=250, height=150)
        category_list_frame.pack(padx=20)
        
        # Use standard Listbox inside CTkScrollableFrame
        tk_listbox = tk.Listbox(category_list_frame, width=40, height=10, bg="#2B2B2B", fg="white", selectbackground="#347083", highlightthickness=0)
        tk_listbox.pack(padx=5, pady=5)
        
        for cat in self.categories:
            tk_listbox.insert(ctk.END, cat.capitalize())

        def remove_category():
            selected_indices = tk_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select a category to remove.")
                return

            # Get the category name (capitalized)
            cat_to_remove_display = tk_listbox.get(selected_indices[0])
            cat_to_remove_lower = cat_to_remove_display.lower()

            # Check if category is in use
            if any(exp['category'] == cat_to_remove_lower for exp in self.expenses):
                 messagebox.showwarning("In Use", f"Cannot remove '{cat_to_remove_display}'. Update or delete related transactions first.")
                 return

            if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove '{cat_to_remove_display}'?"):
                self.categories.remove(cat_to_remove_display)
                self.save_categories()
                tk_listbox.delete(selected_indices[0])
                self.update_category_comboboxes()
                messagebox.showinfo("Removed", "Category removed.")

        ctk.CTkButton(cat_win, text="❌ Remove Selected Category", command=remove_category, hover_color="#B71C1C", fg_color="#f44336").pack(pady=10)
        cat_win.wait_window()

    def update_category_comboboxes(self):
        """Updates the values in all category comboboxes."""
        display_categories = [c.capitalize() for c in self.categories]
        self.category_entry.configure(values=display_categories)
        
        filter_categories = ["All Categories"] + display_categories
        self.filter_category_combo.configure(values=filter_categories)

    def category_selected(self, choice):
        """Required command function for CTkComboBox."""
        pass 

def main():
    app = FinancialTracker()
    app.mainloop()

if __name__ == "__main__":
    main()