# 🔐 Password Manager in Python

Desktop application developed with **Python + Tkinter** for secure password management, featuring **strong encryption**, **password generator**, **export tools**, **detailed logs**, and a clean, user-friendly interface.

---

## 📌 Overview

This system allows you to securely store credentials (website, username, and password) using **Fernet (AES) encryption**. All data is stored locally on the user's machine.

The project is ideal for personal use and learning purposes, offering advanced features such as:

* Automatic encryption
* Customizable password generator
* Duplicate account detection
* Account export
* Integrated log console

---

## 🛠️ Technologies Used

* **Python 3.9+**
* **Tkinter** (GUI)
* **cryptography (Fernet / AES)**
* JSON for data persistence
* Advanced logging system

---

## 📂 Project Structure

```
📁 project/
├── main.py            # Main application file
├── requirements.txt   # Project dependencies
├── start.bat          # Quick start for Windows
├── contas.json        # Stored accounts (encrypted)
├── chave.key          # Encryption key (DO NOT DELETE)
├── config.json        # Application settings
└── logs/              # Automatically generated logs
```

---

## ⚙️ Installation

### 1️⃣ Requirements

* Python installed (3.9 or higher)
* Tkinter (included by default on Windows)

Check your Python version:

```bash
python --version
```

---

### 2️⃣ Install dependencies

Inside the project directory, run:

```bash
pip install -r requirements.txt
```

---

## ▶️ How to Run

### Option 1 — Via terminal

```bash
python main.py
```

### Option 2 — Windows shortcut

Double-click:

```
start.bat
```

---

## 🔑 Master Password

When the application starts, you will be prompted to enter the **master password**.

> **Default master password:**

```
admin
```

⚠️ **IMPORTANT:**

* The master password is hardcoded in `main.py`
* It is strongly recommended to change it before real use

---

## 🧩 Features

### ➕ Add Account

* Enter website, username, and password
* Nickname is optional
* Duplicate accounts are automatically blocked

---

### 🎲 Password Generator

* Adjustable length
* Uppercase letters
* Numbers
* Custom special characters
* One-click copy

---

### 📋 View Accounts

* Alphabetically sorted by website
* View account details
* Show/hide password
* Copy password
* Delete account

---

### 📤 Export Accounts

* Exports **each account into an individual `.txt` file**
* Passwords are exported **decrypted**
* Ideal for offline backups

---

### 📊 Log Console

* Real-time logs
* Logs also saved to files
* Useful for debugging and auditing

---

## 🔐 Security

* **Fernet (AES) encryption**
* Local encryption key stored in `chave.key`
* Sensitive data is never stored in plain text

⚠️ **Never delete the `chave.key` file**

> Without it, stored passwords cannot be recovered.

---

## 🧠 Important Notes

* Designed for **local and personal use**
* Not recommended for corporate environments without modifications
* Regularly back up the following files:

  * `contas.json`
  * `chave.key`

---

## 🚀 Possible Future Improvements

* Master password change screen
* Hashed authentication
* Encrypted backup
* CSV export
* Packaging as a `.exe`

---

## 👨‍💻 Author

Developed in **Python** for learning and personal use.

---

## 📜 License

Free for educational and personal use.

---

✨ **Complete, secure, and fully functional project.**
