# Boost Reminder Slack Bot

This Slack bot creates a daily thread in your specified channel containing all Twitter/X posts from the last 24 hours, encouraging team members to boost the posts.

## Features

- Runs daily at 10:00 AM using Vercel Cron Jobs
- Collects all Twitter/X links posted in the last 24 hours
- Creates a thread with all unique links
- Sends a friendly reminder to boost the posts

## Setup Instructions

1. Create a new Slack App at https://api.slack.com/apps
2. Add the following OAuth scopes to your bot:
   - `channels:history`
   - `chat:write`
   - `chat:write.public`
3. Install the app to your workspace
4. Copy the Bot User OAuth Token
5. Copy the channel ID of your external-content channel

### Deployment to Vercel

1. Install the Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy to Vercel:
   ```bash
   vercel
   ```

4. Add environment variables in the Vercel dashboard:
   - `SLACK_BOT_TOKEN`: Your Slack Bot User OAuth Token
   - `CHANNEL_ID`: Your channel ID

5. The bot will automatically run every day at 10:00 AM using Vercel Cron Jobs

## How it Works

The bot is implemented as a serverless function that runs on Vercel's infrastructure. It uses Vercel's Cron Jobs feature to trigger the function daily at 10:00 AM. When triggered, it:

1. Fetches all messages from the last 24 hours in the specified channel
2. Extracts all Twitter/X links from these messages
3. Creates a new thread with a reminder message
4. Adds all the collected links to the thread

## Troubleshooting

If you're not seeing the daily posts:
1. Check the Vercel deployment logs for any errors
2. Verify that your environment variables are set correctly
3. Ensure the Slack bot has the correct permissions
4. Check that the channel ID is correct
