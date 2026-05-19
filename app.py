import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db_connection():
    connection = sqlite3.connect("inventory.db")
    connection.row_factory = sqlite3.Row
    return connection

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

    return jsonify({"message": "Item added successfully"}), 201

#UPDATE: update quantity
@app.route("/items/<int:item_id>/quantity", methods=["PATCH"])
def update_quantity(item_id):
    data = request.get_json()

    connection = get_db_connection()

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

    return jsonify({"message": "Quantity updated successfully"})

#DELETE: delete item
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    connection = get_db_connection()

    connection.execute(
        "DELETE FROM items WHERE id = ?",
        (item_id),
    )

    connection.commit()
    connection.close()

    return jsonify({"message": "Item deleted successfully"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
