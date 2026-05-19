import sqlite3

connection = sqlite3.connect("inventory.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    minimum_required INTEGER NOT NULL,
    location TEXT NOT NULL
)
""")

cursor.execute("""
INSERT INTO items (
    name,
    category,
    quantity,
    minimum_required,
    location
)
VALUES (
    'Welcome Cards',
    'Cards',
    40,
    150,
    'Ushering Cabinet'
)
""")


connection.commit()

connection.close()

print("Database and table created.")