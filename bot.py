import os
import re
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
import schedule
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
load_dotenv()

# Initialize Slack client
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
CHANNEL_ID = os.environ["CHANNEL_ID"]

def extract_twitter_links(text):
    """Extract Twitter/X links from text."""
    twitter_pattern = r'https?://(?:www\.)?(twitter\.com|x\.com)/[^\s]+'
    return re.findall(twitter_pattern, text)

def get_channel_messages(since_ts):
    """Get messages from the channel after the given timestamp."""
    try:
        result = client.conversations_history(
            channel=CHANNEL_ID,
            oldest=since_ts
        )
        return result["messages"]
    except SlackApiError as e:
        print(f"Error getting messages: {e}")
        return []

def create_daily_thread():
    """Create a thread with all Twitter links from the past day."""
    # Get timestamp for 24 hours ago
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_ts = yesterday.timestamp()
    
    # Get messages from the last 24 hours
    messages = get_channel_messages(yesterday_ts)
    
    # Extract all Twitter links
    all_links = []
    for message in messages:
        if "text" in message:
            links = extract_twitter_links(message["text"])
            all_links.extend(links)
    
    # Remove duplicates while preserving order
    unique_links = list(dict.fromkeys(all_links))
    
    if not unique_links:
        return
    
    # Create the main message
    main_message = "🚀 *Daily Boost Reminder* 🚀\nHere are today's posts that need your support! Please take a moment to boost them. Every engagement helps increase our visibility! 💪"
    
    try:
        # Post the main message
        result = client.chat_postMessage(
            channel=CHANNEL_ID,
            text=main_message
        )
        
        # Create the thread with all links
        thread_ts = result["ts"]
        link_message = "\n\n".join([f"• {link}" for link in unique_links])
        client.chat_postMessage(
            channel=CHANNEL_ID,
            thread_ts=thread_ts,
            text=f"Here are all the posts from the last 24 hours:\n\n{link_message}"
        )
        
    except SlackApiError as e:
        print(f"Error posting message: {e}")

def main():
    # Schedule the daily thread
    schedule.every().day.at("10:00").do(create_daily_thread)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
