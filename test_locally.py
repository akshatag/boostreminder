from dotenv import load_dotenv
from slack_sdk import WebClient
import os
from api.daily_boost import create_daily_boost

# Load environment variables from .env file
load_dotenv()

def main():
    # Initialize Slack client
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    
    # Get channel IDs from environment variables
    source_channel_id = os.environ["SOURCE_CHANNEL_ID"]
    test_channel_id = os.environ["TEST_CHANNEL_ID"]
    
    # Run in draft mode first to see the output
    print("\nTesting in draft mode...")
    result = create_daily_boost(client, source_channel_id, test_channel_id, draft_mode=True)
    print(f"\nDraft message:\n{result}")
    
    # Ask for confirmation before posting
    response = input("\nDo you want to post this message to the test channel? (y/n): ")
    if response.lower() == 'y':
        print("\nPosting to test channel...")
        result = create_daily_boost(client, source_channel_id, test_channel_id, draft_mode=False)
        print(f"\nResult: {result}")
    else:
        print("\nAborted. No message was posted.")

if __name__ == "__main__":
    main()
