import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import subprocess

DB_NAME = "customer_manager.db"

# Change this if your main folder is different
DOCUMENT_ROOT = r"E:\\"  # e.g. E:\VendorName\CustomerName

CHECKLIST_FIELDS = [
    ("pm_suryaghar_app", "PM Suryaghar Application"),
    ("pv_application", "PV Application"),
    ("loan", "Loan"),
    ("meter_testing", "Meter Testing"),
    ("wcr", "WCR"),
    ("upload_rts_portal", "Upload document RTS Portal"),
    ("upload_pm_suryaghar", "Upload document PM Suryaghar"),
    ("subsidy_request", "Subsidy Request"),
    ("payment_done", "Payment Done"),
]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Vendors
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT
        )
    """)

    # Customers
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            FOREIGN KEY(vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
        )
    """)

    # Checklist basic table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS checklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER UNIQUE
        )
    """)

    # 🔧 Ensure all checklist columns exist (auto-upgrade old DB)
    for col, _ in CHECKLIST_FIELDS:
        try:
            cur.execute(f"ALTER TABLE checklist ADD COLUMN {col} INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            # Column already exists, ignore
            pass

    conn.commit()
    conn.close()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Solar Customer Management")
        self.conn = sqlite3.connect(DB_NAME)

        self.selected_vendor_id = None
        self.selected_vendor_name = None
        self.selected_customer_id = None
        self.selected_customer_name = None

        self.check_vars = {}
        self.build_ui()
        self.load_vendors()

    def build_ui(self):
        self.root.geometry("1050x520")
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Vendors frame
        vendor_frame = ttk.Frame(self.root, padding=10)
        vendor_frame.grid(row=0, column=0, sticky="nsew")
        ttk.Label(vendor_frame, text="Vendors", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.vendor_list = tk.Listbox(vendor_frame)
        self.vendor_list.pack(fill="both", expand=True, pady=5)
        self.vendor_list.bind("<<ListboxSelect>>", self.on_vendor_select)
        ttk.Button(vendor_frame, text="Add Vendor", command=self.add_vendor_dialog).pack(pady=5, fill="x")

        # Customers frame
        customer_frame = ttk.Frame(self.root, padding=10)
        customer_frame.grid(row=0, column=1, sticky="nsew")
        ttk.Label(customer_frame, text="Customers", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.customer_list = tk.Listbox(customer_frame)
        self.customer_list.pack(fill="both", expand=True, pady=5)
        self.customer_list.bind("<<ListboxSelect>>", self.on_customer_select)
        ttk.Button(customer_frame, text="Add Customer", command=self.add_customer_dialog).pack(pady=5, fill="x")

        # Checklist frame
        checklist_frame = ttk.Frame(self.root, padding=10)
        checklist_frame.grid(row=0, column=2, sticky="nsew")
        ttk.Label(checklist_frame, text="Customer Checklist", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.checklist_container = ttk.Frame(checklist_frame)
        self.checklist_container.pack(fill="both", expand=True, pady=5)

        for field, label in CHECKLIST_FIELDS:
            var = tk.IntVar(value=0)
            cb = ttk.Checkbutton(self.checklist_container, text=label, variable=var)
            cb.pack(anchor="w", pady=2)
            self.check_vars[field] = var

        ttk.Button(checklist_frame, text="Save Checklist", command=self.save_checklist).pack(pady=5, fill="x")
        ttk.Button(checklist_frame, text="Open Customer Folder", command=self.open_customer_folder).pack(pady=5, fill="x")

    # ---------- Vendors ----------

    def load_vendors(self):
        self.vendor_list.delete(0, tk.END)
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM vendors ORDER BY name")
        self.vendors = cur.fetchall()
        for idx, (vid, name) in enumerate(self.vendors):
            self.vendor_list.insert(idx, f"{name} (ID:{vid})")

    def on_vendor_select(self, event):
        selection = self.vendor_list.curselection()
        if not selection:
            return
        index = selection[0]
        self.selected_vendor_id = self.vendors[index][0]
        self.selected_vendor_name = self.vendors[index][1]
        self.load_customers()

    def add_vendor_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Vendor")
        dialog.grab_set()

        ttk.Label(dialog, text="Vendor Name *").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Phone").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        phone_entry = ttk.Entry(dialog, width=30)
        phone_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Email").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Address").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        address_text = tk.Text(dialog, width=30, height=4)
        address_text.grid(row=3, column=1, padx=5, pady=5)

        def save_vendor():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            address = address_text.get("1.0", tk.END).strip()

            if not name:
                messagebox.showerror("Error", "Vendor name is required.")
                return

            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO vendors (name, phone, email, address) VALUES (?, ?, ?, ?)",
                (name, phone, email, address),
            )
            self.conn.commit()
            self.load_vendors()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save_vendor).grid(row=4, column=0, columnspan=2, pady=10)

    # ---------- Customers ----------

    def load_customers(self):
        self.customer_list.delete(0, tk.END)
        self.selected_customer_id = None
        self.selected_customer_name = None
        self.clear_checklist()
        if self.selected_vendor_id is None:
            return
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM customers WHERE vendor_id = ? ORDER BY name", (self.selected_vendor_id,))
        self.customers = cur.fetchall()
        for idx, (cid, name) in enumerate(self.customers):
            self.customer_list.insert(idx, f"{name} (ID:{cid})")

    def add_customer_dialog(self):
        if self.selected_vendor_id is None:
            messagebox.showwarning("Select Vendor", "Please select a vendor first.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Customer")
        dialog.grab_set()

        ttk.Label(dialog, text="Customer Name *").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Phone").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        phone_entry = ttk.Entry(dialog, width=30)
        phone_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Address").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        address_text = tk.Text(dialog, width=30, height=4)
        address_text.grid(row=2, column=1, padx=5, pady=5)

        def save_customer():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            address = address_text.get("1.0", tk.END).strip()

            if not name:
                messagebox.showerror("Error", "Customer name is required.")
                return

            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO customers (vendor_id, name, phone, address) VALUES (?, ?, ?, ?)",
                (self.selected_vendor_id, name, phone, address),
            )
            self.conn.commit()
            self.load_customers()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save_customer).grid(row=3, column=0, columnspan=2, pady=10)

    def on_customer_select(self, event):
        selection = self.customer_list.curselection()
        if not selection:
            return
        index = selection[0]
        self.selected_customer_id = self.customers[index][0]
        self.selected_customer_name = self.customers[index][1]
        self.load_checklist()

    # ---------- Checklist ----------

    def clear_checklist(self):
        for var in self.check_vars.values():
            var.set(0)

    def load_checklist(self):
        self.clear_checklist()
        if self.selected_customer_id is None:
            return
        cur = self.conn.cursor()
        cur.execute(
            "SELECT " +
            ", ".join(col for col, _ in CHECKLIST_FIELDS) +
            " FROM checklist WHERE customer_id = ?",
            (self.selected_customer_id,),
        )
        row = cur.fetchone()
        if row:
            for (field, _), value in zip(CHECKLIST_FIELDS, row):
                self.check_vars[field].set(value)

    def save_checklist(self):
        if self.selected_customer_id is None:
            messagebox.showwarning("Select Customer", "Please select a customer first.")
            return

        values = [self.check_vars[field].get() for field, _ in CHECKLIST_FIELDS]
        cur = self.conn.cursor()

        try:
            cur.execute("SELECT id FROM checklist WHERE customer_id = ?", (self.selected_customer_id,))
            existing = cur.fetchone()
            if existing:
                set_clause = ", ".join(f"{col}=?" for col, _ in CHECKLIST_FIELDS)
                cur.execute(
                    f"UPDATE checklist SET {set_clause} WHERE customer_id=?",
                    (*values, self.selected_customer_id),
                )
            else:
                cols = ", ".join(col for col, _ in CHECKLIST_FIELDS)
                placeholders = ", ".join("?" for _ in CHECKLIST_FIELDS)
                cur.execute(
                    f"INSERT INTO checklist (customer_id, {cols}) VALUES (?, {placeholders})",
                    (self.selected_customer_id, *values),
                )
            self.conn.commit()
            messagebox.showinfo("Saved", "Checklist saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save checklist:\n{e}")

    # ---------- Open Customer Folder ----------

    def open_customer_folder(self):
        if not self.selected_vendor_name or not self.selected_customer_name:
            messagebox.showwarning("Select Customer", "Please select a vendor and customer first.")
            return

        folder_path = os.path.join(DOCUMENT_ROOT, self.selected_vendor_name, self.selected_customer_name)

        if not os.path.exists(folder_path):
            create = messagebox.askyesno(
                "Folder Not Found",
                f"Folder not found:\n{folder_path}\n\nDo you want to create it?"
            )
            if not create:
                return
            try:
                os.makedirs(folder_path, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder:\n{e}")
                return

        try:
            if sys.platform.startswith("win"):
                os.startfile(folder_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = App(root)

    def on_close():
        app.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
