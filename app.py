import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import database

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




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
