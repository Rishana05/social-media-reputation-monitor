# view.py
import sqlite3

DB_PATH = "social_monitor.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for row in cur.execute("SELECT post_id, created_at, sentiment_label, text FROM posts ORDER BY fetched_at DESC LIMIT 20"):
        print("\nID:", row[0])
        print("Date:", row[1])
        print("Sentiment:", row[2])
        print("Text:", row[3])
    conn.close()

if __name__ == "__main__":
    main()
