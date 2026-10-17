#!/usr/bin/env python3
"""
Interactive Command-Line Interface (CLI) for Python Contact Book Application.
Allows users to add, search, update, delete, display, and export contacts.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database

def print_header(title):
    print("\n" + "=" * 65)
    print(f" 📇  {title.upper()}")
    print("=" * 65)

def display_contact_card(c, index=None):
    idx_str = f"[{index}] " if index is not None else ""
    fav_badge = " ⭐ [FAVORITE]" if c.get('is_favorite') else ""
    
    print("-" * 65)
    print(f"{idx_str}ID: #{c['id']} | {c['name']}{fav_badge}")
    print(f"🏢 Organization : {c.get('organization') or 'Not specified'}")
    print(f"📱 Mobile       : {c['mobile']}")
    print(f"✉️  Email        : {c.get('email') or 'Not specified'}")
    print(f"📍 Address      : {c.get('address') or 'Not specified'}")
    if c.get('notes'):
        print(f"📝 Notes        : {c['notes']}")
    print("-" * 65)

def add_contact_cli():
    print_header("ADD NEW CONTACT")
    name = input("Contact Full Name *: ").strip()
    if not name:
        print("❌ Error: Name is required!")
        return

    mobile = input("Mobile Number *: ").strip()
    if not mobile:
        print("❌ Error: Mobile number is required!")
        return

    email = input("Email Address: ").strip()
    organization = input("Organization / Company: ").strip()
    address = input("Physical Address: ").strip()
    notes = input("Additional Notes: ").strip()
    fav_input = input("Mark as favorite? (y/N): ").strip().lower()
    is_favorite = 1 if fav_input in ('y', 'yes') else 0

    try:
        contact = database.add_contact(
            name=name,
            mobile=mobile,
            email=email or None,
            address=address or None,
            organization=organization or None,
            is_favorite=is_favorite,
            notes=notes or None
        )
        print("\n✅ Contact successfully saved!")
        display_contact_card(contact)
    except Exception as e:
        print(f"❌ Failed to add contact: {e}")

def display_all_contacts_cli():
    print_header("DISPLAY ALL SAVED CONTACTS")
    print("Sort Options:")
    print("  1. Alphabetical (A to Z)")
    print("  2. Alphabetical (Z to A)")
    print("  3. By Organization")
    print("  4. Recently Added First")
    print("  5. Favorites Only")
    
    choice = input("Select sort/filter [1-5, default 1]: ").strip()
    
    sort_map = {
        "1": ("name_asc", False),
        "2": ("name_desc", False),
        "3": ("org_asc", False),
        "4": ("date_desc", False),
        "5": ("name_asc", True)
    }
    sort_by, fav_only = sort_map.get(choice, ("name_asc", False))
    
    contacts = database.get_contacts(sort_by=sort_by, favorite_only=fav_only)
    print(f"\nTotal Contacts Found: {len(contacts)}")
    
    if not contacts:
        print("No contacts stored in the contact book yet.")
        return

    for i, c in enumerate(contacts, 1):
        display_contact_card(c, index=i)

def search_contacts_cli():
    print_header("SEARCH CONTACTS")
    keyword = input("Enter search term (name, mobile, email, organization, address): ").strip()
    if not keyword:
        print("Search cancelled (empty query).")
        return

    contacts = database.get_contacts(search=keyword)
    print(f"\nSearch results for '{keyword}' ({len(contacts)} match{'es' if len(contacts) != 1 else ''}):")

    if not contacts:
        print("No matching contacts found.")
        return

    for i, c in enumerate(contacts, 1):
        display_contact_card(c, index=i)

def update_contact_cli():
    print_header("UPDATE CONTACT DETAILS")
    search_term = input("Enter contact name or ID to search for updating: ").strip()
    if not search_term:
        return

    if search_term.isdigit():
        target = database.get_contact_by_id(int(search_term))
        contacts = [target] if target else []
    else:
        contacts = database.get_contacts(search=search_term)

    if not contacts:
        print("No contacts found matching your query.")
        return

    if len(contacts) > 1:
        print("\nMultiple contacts found. Please select one:")
        for idx, c in enumerate(contacts, 1):
            print(f"  {idx}. ID #{c['id']}: {c['name']} ({c['mobile']}) - {c.get('organization') or 'N/A'}")
        sel = input("Enter number [1-{0}]: ".format(len(contacts))).strip()
        if not sel.isdigit() or not (1 <= int(sel) <= len(contacts)):
            print("Invalid selection.")
            return
        contact = contacts[int(sel) - 1]
    else:
        contact = contacts[0]

    print("\nCurrent Contact Details:")
    display_contact_card(contact)
    print("Leave fields blank to keep existing values.\n")

    name = input(f"New Name [{contact['name']}]: ").strip()
    mobile = input(f"New Mobile [{contact['mobile']}]: ").strip()
    email = input(f"New Email [{contact.get('email') or 'None'}]: ").strip()
    org = input(f"New Organization [{contact.get('organization') or 'None'}]: ").strip()
    address = input(f"New Address [{contact.get('address') or 'None'}]: ").strip()
    notes = input(f"New Notes [{contact.get('notes') or 'None'}]: ").strip()

    fav_str = "Yes" if contact['is_favorite'] else "No"
    fav_in = input(f"Favorite? Current: {fav_str} (y/n or blank to keep): ").strip().lower()
    is_favorite = None
    if fav_in in ('y', 'yes'):
        is_favorite = 1
    elif fav_in in ('n', 'no'):
        is_favorite = 0

    try:
        updated = database.update_contact(
            contact_id=contact['id'],
            name=name or None,
            mobile=mobile or None,
            email=email or None,
            organization=org or None,
            address=address or None,
            notes=notes or None,
            is_favorite=is_favorite
        )
        print("\n✅ Contact updated successfully!")
        display_contact_card(updated)
    except Exception as e:
        print(f"❌ Update failed: {e}")

def delete_contact_cli():
    print_header("DELETE UNWANTED CONTACT")
    identifier = input("Enter Contact ID or Name to delete: ").strip()
    if not identifier:
        return

    if identifier.isdigit():
        contact = database.get_contact_by_id(int(identifier))
    else:
        results = database.get_contacts(search=identifier)
        if not results:
            print("No contact found.")
            return
        contact = results[0]

    if not contact:
        print("Contact not found.")
        return

    print("\nTarget Contact:")
    display_contact_card(contact)
    confirm = input(f"⚠️ Are you sure you want to permanently delete {contact['name']}? (y/N): ").strip().lower()

    if confirm in ('y', 'yes'):
        if database.delete_contact(contact['id']):
            print(f"✅ Contact '{contact['name']}' has been deleted.")
        else:
            print("Failed to delete contact.")
    else:
        print("Deletion cancelled.")

def export_contacts_cli():
    print_header("EXPORT CONTACTS")
    print("Export Formats:")
    print("  1. vCard (.vcf) - Standard format for Apple/Android/Google Contacts")
    print("  2. CSV (.csv)   - Excel / Spreadsheet format")
    choice = input("Select format [1-2]: ").strip()

    if choice == "1":
        vcf_data = database.export_contacts_vcard()
        filename = "contacts_export.vcf"
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(vcf_data)
        print(f"✅ Exported vCard to: {filepath}")
    elif choice == "2":
        csv_data = database.export_contacts_csv()
        filename = "contacts_export.csv"
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(csv_data)
        print(f"✅ Exported CSV to: {filepath}")
    else:
        print("Invalid choice.")

def main_menu():
    database.init_db()
    database.seed_sample_contacts()

    while True:
        stats = database.get_stats()
        print("\n" + "=" * 65)
        print(" 📖  PYTHON CONTACT BOOK - MANAGEMENT CONSOLE")
        print("=" * 65)
        print(f" 📊 Stored Contacts: {stats['total']} | ⭐ Favorites: {stats['favorites']} | 🏢 Organizations: {stats['organizations']}")
        print("=" * 65)
        print(" 1. ➕ Add New Contact")
        print(" 2. 📇 Display All Contacts (Sort by Name, Org, Date, Favorites)")
        print(" 3. 🔍 Search Contacts (Name, Mobile, Email, Org, Address)")
        print(" 4. ✏️  Update Contact Details")
        print(" 5. 🗑️  Delete Unwanted Contact")
        print(" 6. 📤 Export Contacts (vCard / CSV)")
        print(" 0. 🚪 Exit")
        print("=" * 65)

        choice = input("Select an option [0-6]: ").strip()

        if choice == "1":
            add_contact_cli()
        elif choice == "2":
            display_all_contacts_cli()
        elif choice == "3":
            search_contacts_cli()
        elif choice == "4":
            update_contact_cli()
        elif choice == "5":
            delete_contact_cli()
        elif choice == "6":
            export_contacts_cli()
        elif choice == "0":
            print("\nThank you for using Contact Book. Goodbye!\n")
            sys.exit(0)
        else:
            print("Invalid choice. Please select between 0 and 6.")

if __name__ == "__main__":
    main_menu()
