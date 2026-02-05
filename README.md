# Social Media Reputation Monitoring System

## Objective
Monitor public Twitter (X) mentions of Nestlé and its products and analyze customer sentiment in real time.

## Tools & Technologies
- Python
- Tweepy (Twitter API)
- TextBlob (Sentiment Analysis)
- SQLite (Database)
- Streamlit (User Interface)
- Slack Incoming Webhooks (Alerts)
- Matplotlib (Visualization)

## Features
- Collects live tweets using keywords (Nestle, Maggi, KitKat, Nescafe)
- Performs sentiment analysis (positive, neutral, negative)
- Stores tweets in SQLite database
- Displays historical data
- Visualizes sentiment distribution
- Sends Slack alerts for negative tweets
- Web-based user interface using Streamlit

## How It Works
1. Fetch tweets from Twitter API
2. Analyze sentiment using TextBlob
3. Save results into database
4. Send Slack alerts if negative sentiment detected
5. Display data in a Streamlit dashboard

## Outcome
- Improved brand monitoring
- Faster response to negative feedback
- Actionable insights from social media data
