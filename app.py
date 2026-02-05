import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Nestle Social Media Monitor", layout="wide")

st.title("📊 Nestlé Social Media Reputation Monitoring")

# Connect to database
conn = sqlite3.connect("social_monitor.db")
df = pd.read_sql_query(
    "SELECT created_at, sentiment_label, sentiment_score, text FROM posts ORDER BY fetched_at DESC",
    conn
)
conn.close()

# Show metrics
st.subheader("📈 Sentiment Summary")

sentiment_counts = df["sentiment_label"].value_counts()

col1, col2, col3 = st.columns(3)
col1.metric("Positive", sentiment_counts.get("positive", 0))
col2.metric("Neutral", sentiment_counts.get("neutral", 0))
col3.metric("Negative", sentiment_counts.get("negative", 0))

# Pie chart
st.subheader("🧠 Sentiment Distribution")

fig, ax = plt.subplots()
ax.pie(
    sentiment_counts.values,
    labels=sentiment_counts.index,
    autopct="%1.1f%%"
)
st.pyplot(fig)

# Table
st.subheader("📝 Recent Tweets")
st.dataframe(df, use_container_width=True)

st.caption("Data source: Twitter (X) API | Sentiment: TextBlob")