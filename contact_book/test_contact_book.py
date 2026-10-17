"""
Unit tests for Python Contact Book Application
Tests adding, searching, updating, deleting, displaying, and exporting contacts.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database

class TestContactBook(unittest.TestCase):
    def setUp(self):
        database.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_contacts.db")
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)
        database.init_db()

    def tearDown(self):
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)

    def test_add_and_get_contact(self):
        contact = database.add_contact(
            name="Alice Walker",
            mobile="+1 (555) 123-4567",
            email="alice@innovate.com",
            address="123 Tech Way, Silicon Valley, CA",
            organization="Innovate Corp",
            is_favorite=1,
            notes="Lead Developer"
        )
        self.assertIsNotNone(contact)
        self.assertEqual(contact["name"], "Alice Walker")
        self.assertEqual(contact["mobile"], "+1 (555) 123-4567")
        self.assertEqual(contact["email"], "alice@innovate.com")
        self.assertEqual(contact["organization"], "Innovate Corp")
        self.assertEqual(contact["is_favorite"], 1)

        fetched = database.get_contact_by_id(contact["id"])
        self.assertEqual(fetched["name"], "Alice Walker")

    def test_add_contact_validation(self):
        with self.assertRaises(ValueError):
            database.add_contact(name="", mobile="+1234567890")
        with self.assertRaises(ValueError):
            database.add_contact(name="John Doe", mobile="")

    def test_update_contact(self):
        contact = database.add_contact(
            name="Bob Smith",
            mobile="+1 555-0001",
            organization="Old Org"
        )
        updated = database.update_contact(
            contact["id"],
            name="Robert Smith",
            mobile="+1 555-9999",
            organization="New Org",
            is_favorite=1
        )
        self.assertEqual(updated["name"], "Robert Smith")
        self.assertEqual(updated["mobile"], "+1 555-9999")
        self.assertEqual(updated["organization"], "New Org")
        self.assertEqual(updated["is_favorite"], 1)

    def test_delete_contact(self):
        contact = database.add_contact(
            name="Temporary Contact",
            mobile="+1 555-0002"
        )
        self.assertTrue(database.delete_contact(contact["id"]))
        self.assertIsNone(database.get_contact_by_id(contact["id"]))

    def test_search_contacts(self):
        database.add_contact("Charlie Chaplin", "+1 111-2222", email="charlie@cinema.com", organization="United Artists")
        database.add_contact("Grace Hopper", "+1 333-4444", email="grace@navy.mil", organization="US Navy")

        # Search by name
        results = database.get_contacts(search="Charlie")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Charlie Chaplin")

        # Search by organization
        results_org = database.get_contacts(search="Navy")
        self.assertEqual(len(results_org), 1)
        self.assertEqual(results_org[0]["name"], "Grace Hopper")

        # Search by phone
        results_phone = database.get_contacts(search="111-2222")
        self.assertEqual(len(results_phone), 1)
        self.assertEqual(results_phone[0]["name"], "Charlie Chaplin")

    def test_display_all_and_sort(self):
        database.add_contact("Zachary Taylor", "+1 555-0003", organization="Beta Co")
        database.add_contact("Arthur Dent", "+1 555-0004", organization="Alpha Co")
        database.add_contact("Marie Curie", "+1 555-0005", organization="Gamma Co")

        # A to Z
        contacts_asc = database.get_contacts(sort_by="name_asc")
        names = [c["name"] for c in contacts_asc]
        self.assertEqual(names, ["Arthur Dent", "Marie Curie", "Zachary Taylor"])

        # Z to A
        contacts_desc = database.get_contacts(sort_by="name_desc")
        names_desc = [c["name"] for c in contacts_desc]
        self.assertEqual(names_desc, ["Zachary Taylor", "Marie Curie", "Arthur Dent"])

    def test_vcard_and_csv_export(self):
        database.add_contact("Ada Lovelace", "+44 20 1234 5678", email="ada@analytical.org", organization="Babbage Labs")

        vcf = database.export_contacts_vcard()
        self.assertIn("BEGIN:VCARD", vcf)
        self.assertIn("FN:Ada Lovelace", vcf)
        self.assertIn("TEL;TYPE=CELL,VOICE:+44 20 1234 5678", vcf)
        self.assertIn("EMAIL;TYPE=PREF,INTERNET:ada@analytical.org", vcf)
        self.assertIn("ORG:Babbage Labs", vcf)

        csv_str = database.export_contacts_csv()
        self.assertIn("Ada Lovelace", csv_str)
        self.assertIn("Babbage Labs", csv_str)

if __name__ == "__main__":
    unittest.main()
