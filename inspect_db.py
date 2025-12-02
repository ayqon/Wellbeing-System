import sqlite3
import os

# Try to find the DB file.
db_path = 'instance/wellbeing.db' # Default for prototype
if not os.path.exists(db_path):
    print(f"DB file {db_path} not found in current directory.")
    # Try root swats.db just in case
    db_path = 'swats.db'
    if not os.path.exists(db_path):
        print(f"DB file {db_path} not found.")
        # Try to find it via config if possible, or just list dir
        print("Listing current directory:")
        print(os.listdir('.'))
        if os.path.exists('instance'):
            print("Listing instance directory:")
            print(os.listdir('instance'))
        exit(1)

print(f"Inspecting DB at: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("Columns in 'users' table:")
    found_names = []
    for col in columns:
        print(col)
        found_names.append(col[1])
    
    if 'first_name' in found_names and 'last_name' in found_names:
        print("\nSUCCESS: Name columns found.")
    else:
        print("\nFAILURE: Name columns MISSING.")
        
    # Check if data is populated
    cursor.execute("SELECT username, first_name, last_name, role FROM users WHERE role = 'STUDENT' LIMIT 5")
    rows = cursor.fetchall()
    print("\nSample Student Data:")
    for row in rows:
        print(row)

except Exception as e:
    print(f"Error: {e}")
finally:
    print("\nColumns in 'courses' table:")
    cursor.execute("PRAGMA table_info(courses)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)

    print("\nSample Course Data:")
    cursor.execute("SELECT * FROM courses")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    conn.close()
