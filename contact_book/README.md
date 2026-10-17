# 📇 Python Contact Book Application

A clean, modern, and efficient Python-based Contact Book application to store, organize, search, update, delete, and display contacts. Each contact includes complete contact details: **name, mobile number, email address, physical address, organization, notes, and favorite status**.

---

## 🌟 Key Features

- **Core Contact Management**:
  - **Add New Contacts**: Store Name, Mobile Number, Email Address, Physical Address, Organization / Company, Notes, and Favorite flag.
  - **Search Contacts**: Real-time multi-field search across Name, Mobile, Email, Organization, and Address.
  - **Update Contact Details**: Modify any field while preserving the remaining information.
  - **Delete Unwanted Contacts**: Fast deletion with safety confirmation dialog.
  - **Display All Contacts**: Alphabetical sorting (A-Z, Z-A), sorting by company/organization, and sorting by recently added.
- **Enhanced Utilities**:
  - **vCard (.vcf) Export**: Export standard vCards compatible with Apple Contacts, Google Contacts, and Outlook.
  - **CSV (.csv) Export**: Download full contact database for spreadsheets or data backup.
  - **Quick Communications**: One-click direct calling (`tel:`), emailing (`mailto:`), Google Maps directions (`maps.google.com`), and clipboard copy.
- **Dual Interface**:
  - **Modern Web Application**: Responsive split-view layout, initials avatars with colorful gradients, dark/light theme toggle, alphabetical jump bar, and toast alerts.
  - **Interactive CLI (Command-Line Interface)**: Clean terminal interface for quick terminal-based contact management.
- **Persistence**: Built-in SQLite database with auto-initialization and diverse realistic sample contacts.

---

## 🚀 Quick Start

### 1. Prerequisites & Environment
From the repository root:
```bash
# Using the workspace virtual environment
source ../.venv/bin/activate   # or .venv/bin/activate
```

### 2. Run the Web Application
```bash
python3 app.py
# or using the virtualenv:
../.venv/bin/python app.py
```
Open your browser at: **`http://127.0.0.1:5002`**

#### Web Features:
- Click **"➕ Add Contact"** to create a new record.
- Click any contact in the left directory to open their detailed profile card.
- Use the **Search bar** (or press `/` on your keyboard) to search instantly.
- Click the **★ Star icon** on any contact to mark them as a Favorite.
- Filter by **"⭐ Favorites"** tab or select a specific organization from the dropdown.
- Click **"📤 Export ▾"** to download as vCard (.vcf) or CSV (.csv).

---

### 3. Run the Command-Line Interface (CLI)
```bash
python3 cli.py
# or using the virtualenv:
../.venv/bin/python cli.py
```

#### CLI Menu Options:
1. `➕ Add New Contact`: Guided prompts to enter name, mobile, email, address, organization, notes.
2. `📇 Display All Contacts`: Sort A-Z, Z-A, by company, or show favorites only.
3. `🔍 Search Contacts`: Instant query by name, mobile, email, or company.
4. `✏️ Update Contact Details`: Edit individual fields.
5. `🗑️ Delete Unwanted Contact`: Remove contact with confirmation.
6. `📤 Export Contacts`: Export to `.vcf` or `.csv`.

---

## 🧪 Running Tests
```bash
python3 test_contact_book.py
# or
../.venv/bin/python test_contact_book.py
```
