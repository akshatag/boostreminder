from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta
import os
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import html

def extract_twitter_links(text):
    """Extract Twitter/X links from text."""
    # Pattern to match Slack's URL format: <url|url> or <url>
    slack_pattern = r'<(https?://(?:www\.)?(?:twitter\.com|x\.com)/[^|>]+)(?:\|[^>]+)?>'
    matches = re.findall(slack_pattern, text)
    # Unescape HTML entities in the URLs
    return [html.unescape(url) for url in matches]

def get_channel_messages(client, channel_id, since_ts):
    """Get messages from the channel after the given timestamp."""
    try:
        result = client.conversations_history(
            channel=channel_id,
            oldest=since_ts
        )
        print(f"Found {len(result['messages'])} messages")
        return result["messages"]
    except SlackApiError as e:
        print(f"Error getting messages: {e}")
        return []

def create_daily_thread(client, source_channel_id, target_channel_id, draft_mode=False):
    """Create a thread with all Twitter links from the past day."""
    # Get timestamp for 24 hours ago
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_ts = yesterday.timestamp()
    
    # Get messages from the last 24 hours from source channel
    messages = get_channel_messages(client, source_channel_id, yesterday_ts)
    
    # Extract all Twitter links
    all_links = []
    for message in messages:
        if "text" in message:
            print(f"\nProcessing message: {message['text']}")
            links = extract_twitter_links(message["text"])
            all_links.extend(links)
    
    # Remove duplicates while preserving order
    unique_links = list(dict.fromkeys(all_links))
    print(f"\nFinal unique links: {unique_links}")
    
    if not unique_links:
        return {"main_message": None, "thread_messages": None}
    
    # Create the main message with @channel notification
    main_message = "<!channel> 🚀 *Daily Boost Reminder* 🚀\nHere are today's posts that need your support! Please take a moment to boost each post in this thread. Every engagement helps increase our visibility! 💪"
    
    # Create individual messages for each link
    thread_messages = [f"{link}" for link in unique_links]
    
    if draft_mode:
        return {
            "main_message": main_message,
            "thread_messages": thread_messages
        }
    
    try:
        # Post the main message to target channel
        result = client.chat_postMessage(
            channel=target_channel_id,
            text=main_message
        )
        
        # Create individual replies for each link
        thread_ts = result["ts"]
        for message in thread_messages:
            client.chat_postMessage(
                channel=target_channel_id,
                thread_ts=thread_ts,
                text=message
            )
        return "Thread created successfully"
        
    except SlackApiError as e:
        return f"Error posting message: {e}"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Initialize Slack client
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        source_channel_id = os.environ["SOURCE_CHANNEL_ID"]
        target_channel_id = os.environ["TARGET_CHANNEL_ID"]
        
        result = create_daily_thread(client, source_channel_id, target_channel_id, draft_mode=False)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(str(result).encode())
