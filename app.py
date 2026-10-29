"""
Root entry point for Contact Book (Vercel Serverless & Local WSGI).
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
contact_book_dir = os.path.join(current_dir, "contact_book")
if contact_book_dir not in sys.path:
    sys.path.insert(0, contact_book_dir)

from contact_book.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port)
