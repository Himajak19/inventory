import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class InventoryGUI:
    def __init__(self, master):
        self.master = master
        master.title("Inventory Management System")

        # Connect to the SQLite database
        self.conn = sqlite3.connect('inventory.db')
        self.cursor = self.conn.cursor()

        # Create the products table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, quantity INTEGER, price REAL)''')

        # Create the main frame
        self.main_frame = ttk.Frame(master, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create the product list
        self.product_list = ttk.Treeview(self.main_frame, columns=('name', 'description', 'quantity', 'price'), show='headings')
        self.product_list.heading('name', text='Name')
        self.product_list.heading('description', text='Description')
        self.product_list.heading('quantity', text='Quantity')
        self.product_list.heading('price', text='Price')
        self.product_list.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create the action frame
        self.action_frame = ttk.Frame(self.main_frame)
        self.action_frame.pack(pady=10)

        self.add_button = ttk.Button(self.action_frame, text="Add Product", command=self.add_product)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = ttk.Button(self.action_frame, text="Edit Product", command=self.edit_product)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(self.action_frame, text="Delete Product", command=self.delete_product)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.refresh_button = ttk.Button(self.action_frame, text="Refresh", command=self.refresh_product_list)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        # Populate the product list
        self.refresh_product_list()

    def add_product(self):
        # Create a new window for adding a product
        add_window = tk.Toplevel(self.master)
        add_window.title("Add Product")

        # Create the input fields
        name_label = ttk.Label(add_window, text="Name:")
        name_label.pack()
        name_entry = ttk.Entry(add_window)
        name_entry.pack()

        description_label = ttk.Label(add_window, text="Description:")
        description_label.pack()
        description_entry = ttk.Entry(add_window)
        description_entry.pack()

        quantity_label = ttk.Label(add_window, text="Quantity:")
        quantity_label.pack()
        quantity_entry = ttk.Entry(add_window)
        quantity_entry.pack()

        price_label = ttk.Label(add_window, text="Price:")
        price_label.pack()
        price_entry = ttk.Entry(add_window)
        price_entry.pack()

        # Add the save button
        save_button = ttk.Button(add_window, text="Save", command=lambda: self.save_product(name_entry.get(), description_entry.get(), quantity_entry.get(), price_entry.get(), add_window))
        save_button.pack(pady=10)

    def save_product(self, name, description, quantity, price, window):
        # Validate the input data
        if not name or not description or not quantity.isdigit() or not price.replace('.', '', 1).isdigit():
            messagebox.showerror("Error", "Please fill in all the fields correctly.")
            return

        # Insert the new product into the database
        self.cursor.execute("INSERT INTO products (name, description, quantity, price) VALUES (?, ?, ?, ?)", (name, description, int(quantity), float(price)))
        self.conn.commit()

        # Refresh the product list
        self.refresh_product_list()

        # Close the add product window
        window.destroy()

    def edit_product(self):
        # Get the selected product
        selected_product = self.product_list.focus()
        if not selected_product:
            messagebox.showerror("Error", "Please select a product to edit.")
            return

        # Get the product data
        product_id = self.product_list.item(selected_product)['text']
        name, description, quantity, price = self.product_list.item(selected_product)['values']

        # Create a new window for editing the product
        edit_window = tk.Toplevel(self.master)
        edit_window.title("Edit Product")

        # Create the input fields
        name_label = ttk.Label(edit_window, text="Name:")
        name_label.pack()
        name_entry = ttk.Entry(edit_window)
        name_entry.insert(0, name)
        name_entry.pack()

        description_label = ttk.Label(edit_window, text="Description:")
        description_label.pack()
        description_entry = ttk.Entry(edit_window)
        description_entry.insert(0, description)
        description_entry.pack()

        quantity_label = ttk.Label(edit_window, text="Quantity:")
        quantity_label.pack()
        quantity_entry = ttk.Entry(edit_window)
        quantity_entry.insert(0, str(quantity))
        quantity_entry.pack()

        price_label = ttk.Label(edit_window, text="Price:")
        price_label.pack()
        price_entry = ttk.Entry(edit_window)
        price_entry.insert(0, str(price))
        price_entry.pack()

        # Add the save button
        save_button = ttk.Button(edit_window, text="Save", command=lambda: self.update_product(product_id, name_entry.get(), description_entry.get(), quantity_entry.get(), price_entry.get(), edit_window))
        save_button.pack(pady=10)

    def update_product(self, product_id, name, description, quantity, price, window):
        # Validate the input data
        if not name or not description or not quantity.isdigit() or not price.replace('.', '', 1).isdigit():
            messagebox.showerror("Error", "Please fill in all the fields correctly.")
            return

        # Update the product in the database
        self.cursor.execute("UPDATE products SET name = ?, description = ?, quantity = ?, price = ? WHERE id = ?", (name, description, int(quantity), float(price), product_id))
        self.conn.commit()

        # Refresh the product list
        self.refresh_product_list()

        # Close the edit product window
        window.destroy()

    def delete_product(self):
        # Get the selected product
        selected_product = self.product_list.focus()
        if not selected_product:
            messagebox.showerror("Error", "Please select a product to delete.")
            return

        # Get the product ID
        product_id = self.product_list.item(selected_product)['text']

        # Ask for confirmation before deleting
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            # Delete the product from the database
            self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.conn.commit()

            # Refresh the product list
            self.refresh_product_list()

    def refresh_product_list(self):
        # Clear the existing product list
        self.product_list.delete(*self.product_list.get_children())

        # Fetch the products from the database
        self.cursor.execute("SELECT * FROM products")
        products = self.cursor.fetchall()

        # Populate the product list
        for product in products:
            self.product_list.insert('', 'end', text=product[0], values=(product[1], product[2], product[3], product[4]))

root = tk.Tk()
inventory_gui = InventoryGUI(root)
root.mainloop()