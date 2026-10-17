"""
Database layer for Python Contact Book Application
Provides SQLite persistence for contacts with search, sorting, and export support.
"""

import sqlite3
import os
import csv
import io
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT,
            address TEXT,
            organization TEXT,
            is_favorite INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def seed_sample_contacts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM contacts")
    count = cursor.fetchone()[0]

    if count == 0:
        samples = [
            (
                "Alexander Wright",
                "+1 (555) 234-5678",
                "alex.wright@quantumlabs.tech",
                "742 Evergreen Terrace, San Francisco, CA 94107",
                "Quantum Labs",
                1,
                "Lead Systems Architect. Key contact for cloud infrastructure."
            ),
            (
                "Dr. Sophia Martinez",
                "+1 (555) 876-5432",
                "s.martinez@stanford.edu",
                "450 Serra Mall, Stanford, CA 94305",
                "Stanford University",
                1,
                "Professor of AI & Robotics. Collaborator on computer vision research."
            ),
            (
                "Benjamin Chen",
                "+1 (555) 345-6789",
                "ben.chen@apexfintech.io",
                "100 Wall Street, 14th Floor, New York, NY 10005",
                "Apex Fintech Solutions",
                0,
                "Senior Product Manager for automated trading platform."
            ),
            (
                "Elena Rostova",
                "+44 20 7946 0912",
                "elena.rostova@bioinnovate.co.uk",
                "221B Baker Street, Marylebone, London NW1 6XE",
                "BioInnovate Genomics",
                1,
                "Head of Computational Biology. Meeting scheduled every alternate Thursday."
            ),
            (
                "Marcus Vance",
                "+1 (555) 456-7890",
                "marcus.vance@vancemedia.com",
                "1200 Grand Avenue, Suite 400, Chicago, IL 60611",
                "Vance Media Group",
                0,
                "Creative Director. Manages brand guidelines and video assets."
            ),
            (
                "Priya Sharma",
                "+91 98765 43210",
                "priya.sharma@aerotechglobal.in",
                "Technology Park, Whitefield, Bangalore 560066",
                "AeroTech Dynamics",
                0,
                "Aerospace Propulsion Consultant."
            )
        ]

        cursor.executemany("""
            INSERT INTO contacts (name, mobile, email, address, organization, is_favorite, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, samples)
        conn.commit()
    conn.close()

def add_contact(name, mobile, email=None, address=None, organization=None, is_favorite=0, notes=None):
    if not name or not name.strip():
        raise ValueError("Contact name cannot be empty")
    if not mobile or not mobile.strip():
        raise ValueError("Mobile number cannot be empty")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO contacts (name, mobile, email, address, organization, is_favorite, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (
        name.strip(),
        mobile.strip(),
        email.strip() if email else None,
        address.strip() if address else None,
        organization.strip() if organization else None,
        1 if is_favorite else 0,
        notes.strip() if notes else None
    ))
    contact_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_contact_by_id(contact_id)

def update_contact(contact_id, name=None, mobile=None, email=None, address=None, organization=None, is_favorite=None, notes=None):
    current = get_contact_by_id(contact_id)
    if not current:
        return None

    new_name = name.strip() if (name and isinstance(name, str)) else current['name']
    new_mobile = mobile.strip() if (mobile and isinstance(mobile, str)) else current['mobile']
    new_email = email.strip() if (email and isinstance(email, str)) else (current['email'] if email is None else None)
    new_address = address.strip() if (address and isinstance(address, str)) else (current['address'] if address is None else None)
    new_org = organization.strip() if (organization and isinstance(organization, str)) else (current['organization'] if organization is None else None)
    new_fav = int(is_favorite) if is_favorite is not None else current['is_favorite']
    new_notes = notes.strip() if (notes and isinstance(notes, str)) else (current['notes'] if notes is None else None)

    if not new_name:
        raise ValueError("Contact name cannot be empty")
    if not new_mobile:
        raise ValueError("Mobile number cannot be empty")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE contacts
        SET name = ?, mobile = ?, email = ?, address = ?, organization = ?, 
            is_favorite = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_name, new_mobile, new_email, new_address, new_org, new_fav, new_notes, contact_id))

    conn.commit()
    conn.close()
    return get_contact_by_id(contact_id)

def delete_contact(contact_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def toggle_favorite(contact_id):
    current = get_contact_by_id(contact_id)
    if not current:
        return None
    new_status = 0 if current['is_favorite'] else 1
    return update_contact(contact_id, is_favorite=new_status)

def get_contact_by_id(contact_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_contacts(search=None, sort_by="name_asc", favorite_only=False, organization=None):
    """
    Retrieve contacts with flexible search and sorting.
    sort_by options:
        - 'name_asc' (A to Z)
        - 'name_desc' (Z to A)
        - 'org_asc' (By Organization)
        - 'date_desc' (Recently Added)
        - 'date_asc' (Oldest Added)
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM contacts WHERE 1=1"
    params = []

    if favorite_only:
        query += " AND is_favorite = 1"

    if organization and organization.lower() != "all":
        query += " AND LOWER(organization) = LOWER(?)"
        params.append(organization)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query += """ AND (
            name LIKE ? OR 
            mobile LIKE ? OR 
            email LIKE ? OR 
            organization LIKE ? OR 
            address LIKE ?
        )"""
        params.extend([term, term, term, term, term])

    # Sorting
    if sort_by == "name_desc":
        order_clause = "ORDER BY is_favorite DESC, name COLLATE NOCASE DESC, id DESC"
    elif sort_by == "org_asc":
        order_clause = "ORDER BY is_favorite DESC, organization COLLATE NOCASE ASC, name COLLATE NOCASE ASC, id ASC"
    elif sort_by == "date_desc":
        order_clause = "ORDER BY is_favorite DESC, created_at DESC, id DESC"
    elif sort_by == "date_asc":
        order_clause = "ORDER BY is_favorite DESC, created_at ASC, id ASC"
    else:  # default name_asc
        order_clause = "ORDER BY is_favorite DESC, name COLLATE NOCASE ASC, id ASC"

    query += f" {order_clause}"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_organizations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT organization FROM contacts WHERE organization IS NOT NULL AND organization != '' ORDER BY organization ASC")
    orgs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return orgs

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM contacts WHERE is_favorite = 1")
    favorites = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT organization) FROM contacts WHERE organization IS NOT NULL AND organization != ''")
    orgs = cursor.fetchone()[0]

    conn.close()
    return {
        "total": total,
        "favorites": favorites,
        "organizations": orgs
    }

def export_contacts_vcard():
    """Generates standard vCard (.vcf) formatted text for all contacts."""
    contacts = get_contacts(sort_by="name_asc")
    vcard_lines = []

    for c in contacts:
        vcard_lines.append("BEGIN:VCARD")
        vcard_lines.append("VERSION:3.0")
        vcard_lines.append(f"FN:{c['name']}")
        vcard_lines.append(f"TEL;TYPE=CELL,VOICE:{c['mobile']}")
        if c.get('email'):
            vcard_lines.append(f"EMAIL;TYPE=PREF,INTERNET:{c['email']}")
        if c.get('organization'):
            vcard_lines.append(f"ORG:{c['organization']}")
        if c.get('address'):
            vcard_lines.append(f"ADR;TYPE=WORK:;;{c['address'].replace(';', ' ')};;;")
        if c.get('notes'):
            vcard_lines.append(f"NOTE:{c['notes']}")
        vcard_lines.append("END:VCARD\n")

    return "\n".join(vcard_lines)

def export_contacts_csv():
    """Generates CSV string of contacts."""
    contacts = get_contacts(sort_by="name_asc")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Mobile", "Email", "Address", "Organization", "Is Favorite", "Notes", "Created At"])

    for c in contacts:
        writer.writerow([
            c['id'],
            c['name'],
            c['mobile'],
            c.get('email') or '',
            c.get('address') or '',
            c.get('organization') or '',
            "Yes" if c.get('is_favorite') else "No",
            c.get('notes') or '',
            c.get('created_at') or ''
        ])

    return output.getvalue()
