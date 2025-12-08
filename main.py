import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

EXPENSES_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Expense Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.expenses = self.load_expenses()
        
        self.create_widgets()
        self.refresh_expense_list()
        self.update_summary()
    
    def load_expenses(self):
        """Load expenses from file"""
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_expenses(self):
        """Save expenses to file"""
        with open(EXPENSES_FILE, 'w') as f:
            json.dump(self.expenses, f, indent=2)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Title
        title = tk.Label(self.root, text="💰 Expense Tracker", 
                        font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#333")
        title.pack(pady=10)
        
        # Input Frame
        input_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.RAISED, borderwidth=2)
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(input_frame, text="Date:", font=("Arial", 10), 
                bg="#ffffff").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.date_entry = tk.Entry(input_frame, font=("Arial", 10), width=15)
        self.date_entry.grid(row=0, column=1, padx=10, pady=10)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(input_frame, text="Amount ($):", font=("Arial", 10), 
                bg="#ffffff").grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.amount_entry = tk.Entry(input_frame, font=("Arial", 10), width=15)
        self.amount_entry.grid(row=0, column=3, padx=10, pady=10)
        
        tk.Label(input_frame, text="Category:", font=("Arial", 10), 
                bg="#ffffff").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.category_entry = ttk.Combobox(input_frame, font=("Arial", 10), width=15,
                                          values=["Food", "Transport", "Entertainment", 
                                                 "Shopping", "Bills", "Healthcare", "Other"])
        self.category_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(input_frame, text="Description:", font=("Arial", 10), 
                bg="#ffffff").grid(row=1, column=2, padx=10, pady=10, sticky="e")
        self.description_entry = tk.Entry(input_frame, font=("Arial", 10), width=35)
        self.description_entry.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        add_btn = tk.Button(input_frame, text="Add Expense", font=("Arial", 11, "bold"),
                           bg="#4CAF50", fg="white", command=self.add_expense, 
                           cursor="hand2", padx=20, pady=5)
        add_btn.grid(row=2, column=0, columnspan=4, pady=10)
        
        # Expense List Frame
        list_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.RAISED, borderwidth=2)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(list_frame, text="Expense List", font=("Arial", 12, "bold"),
                bg="#ffffff").pack(pady=5)
        
        # Treeview for expenses
        columns = ("Date", "Amount", "Category", "Description")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("Date", text="Date")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Description", text="Description")
        
        self.tree.column("Date", width=150)
        self.tree.column("Amount", width=100)
        self.tree.column("Category", width=120)
        self.tree.column("Description", width=300)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Delete button
        delete_btn = tk.Button(list_frame, text="Delete Selected", font=("Arial", 10),
                              bg="#f44336", fg="white", command=self.delete_expense,
                              cursor="hand2", padx=10, pady=5)
        delete_btn.pack(pady=5)
        
        # Summary Frame
        summary_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.RAISED, borderwidth=2)
        summary_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(summary_frame, text="Summary", font=("Arial", 12, "bold"),
                bg="#ffffff").pack(pady=5)
        
        self.summary_label = tk.Label(summary_frame, text="", font=("Arial", 10),
                                     bg="#ffffff", justify=tk.LEFT)
        self.summary_label.pack(pady=5, padx=10)
    
    def add_expense(self):
        """Add a new expense"""
        try:
            amount = float(self.amount_entry.get())
            category = self.category_entry.get()
            description = self.description_entry.get()
            date_str = self.date_entry.get()
            
            if not category:
                messagebox.showwarning("Missing Info", "Please select a category.")
                return
            
            if not description:
                messagebox.showwarning("Missing Info", "Please enter a description.")
                return
            
            # Validate and format date
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format.")
                return
            
            expense = {
                "amount": amount,
                "category": category.lower(),
                "description": description,
                "date": date
            }
            
            self.expenses.append(expense)
            self.save_expenses()
            
            # Clear entries
            self.amount_entry.delete(0, tk.END)
            self.category_entry.set("")
            self.description_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            
            self.refresh_expense_list()
            self.update_summary()
            
            messagebox.showinfo("Success", f"Expense of ${amount:.2f} added!")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount.")
    
    def refresh_expense_list(self):
        """Refresh the expense list display"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for expense in reversed(self.expenses):
            self.tree.insert("", 0, values=(
                expense["date"],
                f"${expense['amount']:.2f}",
                expense["category"].capitalize(),
                expense["description"]
            ))
    
    def delete_expense(self):
        """Delete selected expense"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an expense to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            item = self.tree.item(selected[0])
            date = item["values"][0]
            
            # Find and remove expense
            for i, exp in enumerate(self.expenses):
                if exp["date"] == date:
                    self.expenses.pop(i)
                    break
            
            self.save_expenses()
            self.refresh_expense_list()
            self.update_summary()
            messagebox.showinfo("Deleted", "Expense deleted successfully!")
    
    def update_summary(self):
        """Update summary statistics"""
        if not self.expenses:
            self.summary_label.config(text="No expenses recorded yet.")
            return
        
        total = sum(exp['amount'] for exp in self.expenses)
        
        categories = {}
        for exp in self.expenses:
            cat = exp['category']
            categories[cat] = categories.get(cat, 0) + exp['amount']
        
        summary_text = f"Total Expenses: ${total:.2f}\n\nBy Category:\n"
        for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total) * 100
            summary_text += f"  • {cat.capitalize()}: ${amount:.2f} ({percentage:.1f}%)\n"
        
        self.summary_label.config(text=summary_text)

def main():
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()