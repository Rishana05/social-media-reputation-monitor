import sqlite3
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect("social_monitor.db")
cur = conn.cursor()

cur.execute("""
SELECT sentiment_label, COUNT(*) 
FROM posts
GROUP BY sentiment_label;
""")

data = cur.fetchall()
conn.close()

# Separate labels and values
labels = [row[0] for row in data]
counts = [row[1] for row in data]

# Plot the pie chart
plt.figure(figsize=(6, 6))
plt.pie(counts, labels=labels, autopct='%1.1f%%')
plt.title("Sentiment Distribution for Nestle Tweets")
plt.show()
