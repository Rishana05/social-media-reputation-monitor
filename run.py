# run.py
import sqlite3
import json
import sys
from datetime import datetime
from textblob import TextBlob
import html

# HTTP for Slack
try:
    import requests
except Exception:
    requests = None  # we'll print a helpful message below

# Twitter client
try:
    import tweepy
except Exception as e:
    print("Missing tweepy. Run: pip install -r requirements.txt")
    sys.exit(1)

DB_PATH = "social_monitor.db"
TOKEN_FILE = "twitter_token.txt"  # file where you saved your Bearer Token
WEBHOOK_FILE = "slack_webhook.txt"  # file where you saved Slack webhook URL
# keywords you gave
QUERY = "Nestle India OR Maggi OR KitKat OR Nescafe OR \"Nestle milk\""

MAX_RESULTS = 10  # how many recent tweets to fetch (10 is fine for now)

def read_bearer_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            token = f.read().strip()
            return token
    except FileNotFoundError:
        print(f"Error: {TOKEN_FILE} not found. Place your Bearer Token in this file.")
        return None

def read_slack_webhook():
    try:
        with open(WEBHOOK_FILE, "r", encoding="utf-8") as f:
            webhook = f.read().strip()
            return webhook if webhook else None
    except FileNotFoundError:
        return None

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
      post_id TEXT PRIMARY KEY,
      platform TEXT,
      author_id TEXT,
      author_name TEXT,
      created_at TEXT,
      text TEXT,
      lang TEXT,
      sentiment_score REAL,
      sentiment_label TEXT,
      raw_json TEXT,
      fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()
    print("Database ready:", DB_PATH)

def analyze_sentiment(text):
    try:
        blob = TextBlob(text)
        score = blob.sentiment.polarity  # -1 .. 1
    except Exception:
        score = 0.0
    if score > 0.1:
        label = "positive"
    elif score < -0.1:
        label = "negative"
    else:
        label = "neutral"
    return score, label

def save_post(post):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    INSERT OR IGNORE INTO posts (post_id, platform, author_id, author_name, created_at, text, lang, sentiment_score, sentiment_label, raw_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        post['id'], 'twitter', post.get('author_id'), post.get('author_name'),
        post.get('created_at'), post.get('text'), post.get('lang'),
        post.get('sentiment_score'), post.get('sentiment_label'),
        json.dumps(post.get('raw', {}))
    ))
    conn.commit()
    conn.close()

def send_slack_alert(text, score, tweet_id=None):
    """Send a Slack message for strongly negative tweets."""
    webhook = read_slack_webhook()
    if not webhook:
        print("Slack webhook file not found; skipping Slack alert.")
        return
    if requests is None:
        print("requests library not installed; can't send Slack alert. Run: pip install requests")
        return

    safe_text = html.escape(text)[:800]  # limit length and escape HTML
    tweet_url = f"https://twitter.com/i/web/status/{tweet_id}" if tweet_id else ""
    payload = {
        "text": f"🚨 Negative tweet detected (score {score:.2f})",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn",
                "text": f"*Negative tweet detected*\n*Score:* {score:.2f}\n*Text:* {safe_text}"}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": tweet_url}]}
        ]
    }
    try:
        resp = requests.post(webhook, json=payload, timeout=10)
        if resp.status_code != 200:
            print("Slack webhook error:", resp.status_code, resp.text)
    except Exception as e:
        print("Error sending Slack alert:", e)

def fetch_tweets(bearer):
    client = tweepy.Client(bearer_token=bearer, wait_on_rate_limit=True)
    print("Searching Twitter for:", QUERY)
    try:
        resp = client.search_recent_tweets(query=QUERY, tweet_fields=["created_at","lang","author_id"], max_results=MAX_RESULTS)
    except Exception as e:
        print("Twitter API error:", e)
        return []
    if not getattr(resp, "data", None):
        print("No tweets found for that query (or API returned no data).")
        return []
    results = []
    for t in resp.data:
        text = t.text
        score, label = analyze_sentiment(text)
        post = {
            'id': str(t.id),
            'author_id': str(t.author_id) if hasattr(t, 'author_id') and t.author_id else None,
            'author_name': None,
            'created_at': t.created_at.isoformat() if hasattr(t, 'created_at') and t.created_at else None,
            'text': text,
            'lang': t.lang if hasattr(t, 'lang') else None,
            'sentiment_score': score,
            'sentiment_label': label,
            'raw': t.data if hasattr(t, 'data') else {}
        }
        results.append(post)
    return results

def main():
    print("RUN.PY STARTING...")
    bearer = read_bearer_token()
    if not bearer:
        print("Add your Bearer Token to twitter_token.txt (no quotes), then run: python run.py")
        return
    init_db()
    posts = fetch_tweets(bearer)
    if not posts:
        return
    for p in posts:
        save_post(p)
        print(f"Saved tweet {p['id']} | sentiment: {p['sentiment_label']} ({p['sentiment_score']:.2f})")
        # send Slack alert for very negative tweets (threshold <= -0.7)
        try:
            if p.get("sentiment_score") is not None and p["sentiment_score"] <= -0.7:
                send_slack_alert(p.get("text", ""), p["sentiment_score"], tweet_id=p.get("id"))
        except Exception as e:
            print("Error in alert logic:", e)
    print("Done. Run view.py to see results or open social_monitor.db with a DB viewer.")

if __name__ == "__main__":
    main()
