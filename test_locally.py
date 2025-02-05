from api.daily_boost import create_daily_thread
from slack_sdk import WebClient
import os
from dotenv import load_dotenv
import json

def test_boost_reminder(draft_mode=False):
    # Load environment variables
    load_dotenv()
    
    # Check if environment variables are set
    if not os.getenv("SLACK_BOT_TOKEN"):
        print("Error: SLACK_BOT_TOKEN not set in .env file")
        return
    if not os.getenv("SOURCE_CHANNEL_ID"):
        print("Error: SOURCE_CHANNEL_ID not set in .env file")
        return
    if not os.getenv("TARGET_CHANNEL_ID"):
        print("Error: TARGET_CHANNEL_ID not set in .env file")
        return
    
    # Initialize Slack client
    client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
    source_channel_id = os.getenv("SOURCE_CHANNEL_ID")
    target_channel_id = os.getenv("TARGET_CHANNEL_ID")
    
    print("Running boost reminder...")
    print(f"Reading from channel: {source_channel_id}")
    print(f"{'Preview for' if draft_mode else 'Posting to'} channel: {target_channel_id}")
    
    result = create_daily_thread(client, source_channel_id, target_channel_id, draft_mode=draft_mode)
    
    if draft_mode:
        if result["main_message"] is None:
            print("\nNo Twitter/X links found in the last 24 hours!")
            return
        
        print("\n=== DRAFT PREVIEW ===")
        print("\nMain Message:")
        print("-" * 50)
        print(result["main_message"])
        print("\nThread Replies:")
        print("-" * 50)
        for i, message in enumerate(result["thread_messages"], 1):
            print(f"\nReply {i}:")
            print(message)
        print("\n=== END PREVIEW ===")
    else:
        print(f"\nResult: {result}")

if __name__ == "__main__":
    # Set draft_mode=False to post to Slack
    test_boost_reminder(draft_mode=False)
