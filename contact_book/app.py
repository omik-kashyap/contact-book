"""
Contact Book - Flask Web Application
Provides full REST API and Modern Web Interface.
"""

from flask import Flask, render_template, request, jsonify, Response
import os
import sys

# Ensure package and local imports work properly
try:
    from . import database
except (ImportError, ValueError):
    import database

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

database.init_db()
database.seed_sample_contacts()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/contacts", methods=["GET"])
def api_get_contacts():
    search = request.args.get("search", "")
    sort_by = request.args.get("sort_by", "name_asc")
    favorite_only = request.args.get("favorite_only", "false").lower() in ("true", "1")
    organization = request.args.get("organization", "all")

    contacts = database.get_contacts(
        search=search,
        sort_by=sort_by,
        favorite_only=favorite_only,
        organization=organization
    )
    return jsonify({
        "success": True,
        "count": len(contacts),
        "contacts": contacts
    })

@app.route("/api/contacts/<int:contact_id>", methods=["GET"])
def api_get_contact(contact_id):
    contact = database.get_contact_by_id(contact_id)
    if not contact:
        return jsonify({"success": False, "error": "Contact not found"}), 404
    return jsonify({"success": True, "contact": contact})

@app.route("/api/contacts", methods=["POST"])
def api_create_contact():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    mobile = (data.get("mobile") or "").strip()
    email = (data.get("email") or "").strip()
    address = (data.get("address") or "").strip()
    organization = (data.get("organization") or "").strip()
    notes = (data.get("notes") or "").strip()
    is_favorite = 1 if data.get("is_favorite") in (True, 1, "1", "true") else 0

    if not name:
        return jsonify({"success": False, "error": "Name is required"}), 400
    if not mobile:
        return jsonify({"success": False, "error": "Mobile number is required"}), 400

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
        return jsonify({"success": True, "contact": contact, "message": "Contact created successfully"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/contacts/<int:contact_id>", methods=["PUT"])
def api_update_contact(contact_id):
    data = request.get_json() or {}
    contact = database.get_contact_by_id(contact_id)
    if not contact:
        return jsonify({"success": False, "error": "Contact not found"}), 404

    try:
        updated = database.update_contact(
            contact_id=contact_id,
            name=data.get("name"),
            mobile=data.get("mobile"),
            email=data.get("email"),
            address=data.get("address"),
            organization=data.get("organization"),
            is_favorite=data.get("is_favorite"),
            notes=data.get("notes")
        )
        return jsonify({"success": True, "contact": updated, "message": "Contact updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/contacts/<int:contact_id>", methods=["DELETE"])
def api_delete_contact(contact_id):
    deleted = database.delete_contact(contact_id)
    if not deleted:
        return jsonify({"success": False, "error": "Contact not found or already deleted"}), 404
    return jsonify({"success": True, "message": f"Contact #{contact_id} deleted successfully"})

@app.route("/api/contacts/<int:contact_id>/toggle-favorite", methods=["POST"])
def api_toggle_favorite(contact_id):
    contact = database.toggle_favorite(contact_id)
    if not contact:
        return jsonify({"success": False, "error": "Contact not found"}), 404
    return jsonify({"success": True, "contact": contact})

@app.route("/api/contacts/export/vcf", methods=["GET"])
def api_export_vcf():
    vcf_content = database.export_contacts_vcard()
    return Response(
        vcf_content,
        mimetype="text/vcard",
        headers={"Content-Disposition": "attachment;filename=contacts.vcf"}
    )

@app.route("/api/contacts/export/csv", methods=["GET"])
def api_export_csv():
    csv_content = database.export_contacts_csv()
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=contacts.csv"}
    )

@app.route("/api/organizations", methods=["GET"])
def api_get_organizations():
    orgs = database.get_organizations()
    return jsonify({"success": True, "organizations": orgs})

@app.route("/api/stats", methods=["GET"])
def api_get_stats():
    stats = database.get_stats()
    return jsonify({"success": True, "stats": stats})

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    port = int(os.environ.get("PORT", 5002))
    print(f"📇 Contact Book running at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
