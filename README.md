# 🌞 Solar Customer Management System (PC App)

A lightweight **Windows Desktop Application** built using **Python, Tkinter, and SQLite** to manage:

- Vendors  
- Customers under each vendor  
- Solar project checklist tracking  
- Payment status  
- Direct access to customer document folders  

This app is designed for **solar installation businesses** to manage workflow digitally and avoid manual paperwork.

---

## 🚀 Features

### ✅ Vendor Management
- Add vendor name, phone, email, and address
- Select vendor to view all related customers

### ✅ Customer Management
- Add customers under each vendor
- Store customer phone & address
- Auto-link customer with vendor

### ✅ Project Checklist Tracking
Each customer has a checklist with the following stages:

- PM Suryaghar Application  
- PV Application  
- Loan  
- Meter Testing  
- WCR  
- Upload Documents to RTS Portal  
- Upload Documents to PM Suryaghar  
- Subsidy Request  
- ✅ Payment Done  

All checklist data is saved in the local database.

---

### ✅ Open Customer Folder (Auto)
With one click, the app opens this path automatically:

E:\Vendor Name\Customer Name

makefile
Copy code

Example:
E:\Nitin Electricals SATARA\Balaso Govid Mane

yaml
Copy code

If the folder does not exist, the app will **ask to create it automatically**.

---

## 💻 Technologies Used

- **Python 3**
- **Tkinter** – for GUI
- **SQLite** – for local database
- **PyInstaller** – for converting to `.exe`

---

## ▶️ How to Run the App (Python Mode)

1. Install Python 3  
2. Open Command Prompt in project folder  
3. Run:

```bash
python customer_manager.py
🏗️ How to Create EXE File
Install PyInstaller:

bash
Copy code
python -m pip install pyinstaller
Create EXE:

bash
Copy code
python -m PyInstaller --onefile --noconsole customer_manager.py
Your EXE will appear here:

bash
Copy code
dist/customer_manager.exe
📂 Important Files
File	Purpose
customer_manager.py	Main application
customer_manager.db	Local database
dist/	Auto-generated EXE
build/	Build files
.gitignore	Git ignore rules

🧠 Future Scope (Planned Upgrades)
Search customer by name / phone

Vendor-wise progress dashboard

Excel / PDF export

Auto backup to cloud

Role-based access (admin / staff)

👨‍💻 Developer
Paras
B.Tech Computer Engineering
GitHub Profile:
https://github.com/Paras045
