import sqlite3
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import database
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)
CORS(app)

def get_db_connection():
    connection = sqlite3.connect("inventory.db")
    connection.row_factory = sqlite3.Row
    return connection

def log_activity(message):
    connection = get_db_connection()

    connection.execute(
        "INSERT INTO activities (message) VALUES (?)",
        (message,),
    )

    connection.commit()
    connection.close()

@app.route("/")
def home():
    return jsonify({"message": "UsherStock backend is running"})

#READ: get all items
@app.route("/items", methods=["GET"])
def get_items():
    connection = get_db_connection()
    items = connection.execute("SELECT * FROM items").fetchall()
    connection.close()

    return jsonify([dict(item) for item in items])

#CREATE: add new item
@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json()

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO items (name, category, quantity, minimum_required, location)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data["name"],
            data["category"],
            data["quantity"],
            data["minimumRequired"],
            data["location"],
        ),
    )

    connection.commit()
    connection.close()

    log_activity(f"Added {data['name']}")

    return jsonify({"message": "Item added successfully"}), 201

#UPDATE: update quantity
@app.route("/items/<int:item_id>/quantity", methods=["PATCH"])
def update_quantity(item_id):
    data = request.get_json()

    connection = get_db_connection()

    item = connection.execute(
    "SELECT * FROM items WHERE id = ?",
    (item_id,),
    ).fetchone()

    connection.execute(
        """
        UPDATE items
        SET quantity = ?
        WHERE id = ?
        """,
        (data["quantity"], item_id),
    )

    connection.commit()
    connection.close()

    log_activity(f"Updated quantity for {item['name']}")

    return jsonify({"message": "Quantity updated successfully"})

@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json()

    connection = get_db_connection()

    connection.execute(
        """
        UPDATE items
        SET name = ?, category = ?, minimum_required = ?, location = ?
        WHERE id = ?
        """,
        (
            data["name"],
            data["category"],
            data["minimumRequired"],
            data["location"],
            item_id,
        ),
    )

    connection.commit()
    connection.close()

    log_activity(f"Updated {data['name']}")

    return jsonify({"message": "Item updated successfully"})

#DELETE: delete item
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    connection = get_db_connection()

    item = connection.execute(
    "SELECT * FROM items WHERE id = ?",
    (item_id,),
    ).fetchone()

    connection.execute(
        "DELETE FROM items WHERE id = ?",
        (item_id,),
    )

    connection.commit()
    connection.close()

    log_activity(f"Deleted {item['name']}")

    return jsonify({"message": "Item deleted successfully"})

@app.route("/activities")
def get_activities():
    connection = get_db_connection()

    activities = connection.execute(
        """
        SELECT *
        FROM activities
        ORDER BY created_at DESC
        LIMIT 10
        """
    ).fetchall()

    connection.close()

    return jsonify([
        dict(activity)
        for activity in activities
    ])


@app.route("/reports/inventory")
def generate_inventory_report():
    connection = get_db_connection()

    items = connection.execute(
        "SELECT * FROM items ORDER BY category, name"
    ).fetchall()

    connection.close()

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 60

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, y, "Welcome Home Inventory Report")

    y -= 30

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, "Generated inventory overview for the welcome home team.")

    y -= 40

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Item")
    pdf.drawString(200, y, "Category")
    pdf.drawString(320, y, "Qty")
    pdf.drawString(370, y, "Minimum")
    pdf.drawString(450, y, "Location")

    y -= 20

    pdf.setFont("Helvetica", 10)

    for item in items:
        if y < 60:
            pdf.showPage()
            y = height - 60
            pdf.setFont("Helvetica", 10)

        pdf.drawString(50, y, str(item["name"]))
        pdf.drawString(200, y, str(item["category"]))
        pdf.drawString(320, y, str(item["quantity"]))
        pdf.drawString(370, y, str(item["minimum_required"]))
        pdf.drawString(450, y, str(item["location"]))

        y -= 20

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="welcome-home-inventory-report.pdf",
        mimetype="application/pdf",
    )




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
