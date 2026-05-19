import sqlite3

items = [
    ("Welcome Cards", "Cards", 120, 200, "Ushering Cabinet"),
    ("Communion Cups", "Communion", 500, 300, "Storage Room A"),
    ("Offering Envelopes", "Forms", 250, 200, "Finance Desk"),
    ("Pens", "Stationery", 25, 40, "Ushering Cabinet"),
    ("Usher Badges", "Ushering", 18, 25, "Team Leader Bag"),
    ("Visitor Forms", "Forms", 80, 150, "Welcome Desk"),
    ("Tissue Packs", "Cleaning", 35, 50, "Storage Room B"),
    ("Bottled Water", "Refreshments", 60, 100, "Kitchen Area"),
    ("Clipboards", "Stationery", 12, 15, "Ushering Cabinet"),
    ("First-Time Guest Stickers", "Cards", 30, 100, "Welcome Desk"),
]

connection = sqlite3.connect("inventory.db")
cursor = connection.cursor()

cursor.executemany(
    """
    INSERT INTO items (name, category, quantity, minimum_required, location)
    VALUES (?, ?, ?, ?, ?)
    """,
    items,
)

connection.commit()
connection.close()

print("Seed data added.")