from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta
import os
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import html

def extract_social_links(text):
    """Extract Twitter/X and LinkedIn links from text."""
    # Pattern to match Slack's URL format: <url|url> or <url>
    slack_pattern = r'<(https?://(?:www\.)?(?:twitter\.com|x\.com|linkedin\.com)/[^|>]+)(?:\|[^>]+)?>'
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
        print(f"Found {len(result['messages'])} messages in channel")
        return result["messages"]
    except SlackApiError as e:
        print(f"Error getting messages: {e}")
        return []

def should_boost_message(message):
    """Check if a message should be boosted (contains #boost)."""
    return "#boost" in message.get("text", "").lower()

def create_daily_boost(client, source_channel_id, target_channel_id, draft_mode=False):
    """Create a single message with all social media posts marked for boosting."""
    # Get timestamp for 24 hours ago
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_ts = yesterday.timestamp()
    
    # Get messages from the last 24 hours
    messages = get_channel_messages(client, source_channel_id, yesterday_ts)
    
    # Extract all social media links from messages with #boost
    all_links = []
    for message in messages:
        if "text" in message and should_boost_message(message):
            print(f"\nProcessing boost message: {message['text']}")
            links = extract_social_links(message["text"])
            all_links.extend(links)
    
    # Remove duplicates while preserving order
    unique_links = list(dict.fromkeys(all_links))
    print(f"\nFinal unique links marked for boost: {unique_links}")
    
    if not unique_links:
        return "No posts marked for boost in the last 24 hours"
    
    # Create the message with all links
    message_lines = [
        "<!channel> Here are today's posts that need your support! Every engagement helps increase our visibility. Please take a moment to boost and react with 🚀 once you do\n"
    ]
    
    # Add each link as a bullet point
    for link in unique_links:
        message_lines.append(f"• {link}")
    
    final_message = "\n".join(message_lines)
    
    if draft_mode:
        return final_message
    
    try:
        # Post the message
        result = client.chat_postMessage(
            channel=target_channel_id,
            text=final_message
        )
        return "Message posted successfully"
        
    except SlackApiError as e:
        return f"Error posting message: {e}"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Initialize Slack client
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        source_channel_id = os.environ["SOURCE_CHANNEL_ID"]
        target_channel_id = os.environ["TARGET_CHANNEL_ID"]
        
        result = create_daily_boost(client, source_channel_id, target_channel_id, draft_mode=False)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(str(result).encode())
