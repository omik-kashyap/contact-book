# 🚀 Python Projects Suite

This workspace contains two distinct, fully-featured, Python-based applications:

---

## 📁 Projects Overview

### 1. [Digital Notice Board System](file:///media/loki/New%20Volume6/repos/other%27s%20project/digital_notice_board/README.md) (`digital_notice_board/`)
A centralized digital bulletin board for campus, office, or organizational announcements.
- **Admin Capabilities**: Post, update, delete notices, and pin critical bulletins to top.
- **Sorting & Viewing**:
  - Sort notices by date (newest/oldest), category, or priority (Urgent first).
  - Filter by category pills with live counters.
  - Live search matching titles, body text, and departments.
- **Display Modes**:
  - **Modern Web App** with breaking news live ticker, live clock, card grid, and full-screen **Kiosk / Digital Signage Mode** for wall display monitors (`http://127.0.0.1:5001`).
  - **Interactive Terminal CLI** (`cli.py`).
- **Database**: SQLite with persistent storage and sample seed announcements.

### 2. [Contact Book Application](file:///media/loki/New%20Volume6/repos/other%27s%20project/contact_book/README.md) (`contact_book/`)
An intuitive contact management directory to store, organize, and manage personal and professional contacts.
- **Full Contact Profiles**: Name, mobile number, email address, physical address, organization / company, notes, and favorite status.
- **Operations**:
  - Add new contacts with validation.
  - Real-time multi-field search (name, mobile, email, organization, address).
  - Update contact information with field preservation.
  - Delete unwanted contacts with confirmation.
  - Display all contacts with alphabetical sorting (A-Z, Z-A), company grouping, and favorites filtering.
- **Data Export & Quick Actions**:
  - Export contacts as **vCard (.vcf)** or **CSV (.csv)**.
  - One-click call (`tel:`), email (`mailto:`), Google Maps directions, and copy to clipboard.
- **Interfaces**:
  - **Modern Split-View Web App** (`http://127.0.0.1:5002`).
  - **Interactive Terminal CLI** (`cli.py`).
- **Database**: SQLite with persistent storage and sample seed contacts.

---

## ⚡ Quick Start Guide

### Setup Virtual Environment
```bash
# Activate virtual environment
source .venv/bin/activate
```

---

### Running Digital Notice Board

#### Web Application:
```bash
cd digital_notice_board
python3 app.py
```
Open **`http://127.0.0.1:5001`** in your browser.

#### Terminal CLI:
```bash
cd digital_notice_board
python3 cli.py
```

---

### Running Contact Book

#### Web Application:
```bash
cd contact_book
python3 app.py
```
Open **`http://127.0.0.1:5002`** in your browser.

#### Terminal CLI:
```bash
cd contact_book
python3 cli.py
```

---

## 🧪 Run Tests

```bash
# Run Digital Notice Board tests
.venv/bin/python digital_notice_board/test_notice_board.py

# Run Contact Book tests
.venv/bin/python contact_book/test_contact_book.py
```
