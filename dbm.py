import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('ring.db')
c = conn.cursor()

# Create table if it doesn't exist
try:
    c.execute('CREATE TABLE IF NOT EXISTS ring (duration INTEGER, task TEXT)')
except sqlite3.Error as e:
    pass

# Function to insert a task
def put(a, b):
    try:
        c.execute('INSERT INTO ring (duration, task) VALUES (?, ?)', (a, b))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")

# Function to delete a task by rowid
def delete(rowid):
    try:
        c.execute('DELETE FROM ring WHERE rowid = ?', (rowid,))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error deleting data: {e}")

#c.execute('DROP TABLE ring')
#conn.commit()


#conn.close()