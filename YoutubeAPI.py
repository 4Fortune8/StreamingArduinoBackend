import os
import time
import re
from googleapiclient.discovery import build
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from dotenv import load_dotenv

load_dotenv()
# Define the required scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
def main(channel_handle_url, channel_id, live_stream_id):
    api_key = os.getenv("yt_api_key")
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    # Replace with your API key and channel handle URL
    api_key = 'AIzaSyDkjeGFhKizc5IoaZtLuS3cqfJvVxjpb1U'
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

    # Extract the handle from the URL
    match = re.search(r'@([a-zA-Z0-9_]+)', channel_handle_url)
    if match==None:
        match = get_channel_id_from_url(channel_handle_url)
    if match:
        try:
            handle = match.group(0)
        except:
            handle = match

    # Replace with your live stream video ID and channel ID

    if channel_id == None:
        channel_id = get_channel_id_from_handle(youtube, handle)
    if live_stream_id == None:
        live_stream_id = get_live_stream_id(youtube, channel_id)
    # Get live chat ID
    live_chat_id = get_live_chat_id(youtube, live_stream_id)
    if not live_chat_id:
        return

    previous_viewer_count = None
    previous_subscriber_count = None
    next_page_token = None
    chat_polling_interval = 65  # Default polling interval for chat in seconds
    viewer_polling_interval = 60  # Poll viewer count every 15 seconds
    subscriber_polling_interval = 600  # Poll subscriber count every 60 seconds

    last_viewer_poll = time.time()
    last_subscriber_poll = time.time()

    while True:
        current_time = time.time()
        # Monitor Live Chat Messages
        if current_time - last_viewer_poll >= chat_polling_interval:
            try:
                chat_response = get_live_chat_messages(youtube, live_chat_id, next_page_token)
                # Process chat messages
                for item in chat_response.get('items', []):
                    author = item['authorDetails']['displayName']
                    message = item['snippet']['displayMessage']
                    timestamp = item['snippet']['publishedAt']
                    print(f"[{timestamp}] {author}: {message}")

                # Update next page token and polling interval
                next_page_token = chat_response.get('nextPageToken')
                chat_polling_interval = int(chat_response.get('pollingIntervalMillis', 2000)) / 1000.0
            except Exception as e:
                print(f"Chat Error: {e}")
                chat_polling_interval = min(60, chat_polling_interval * 2)  # Exponential backoff on errors

        # Monitor Viewer Count
        if current_time - last_viewer_poll >= viewer_polling_interval:
            try:
                viewer_count = get_viewer_count(youtube, live_stream_id)
                print(f"Current Viewers: {viewer_count}")
                # React to changes
                if previous_viewer_count is not None and viewer_count != previous_viewer_count:
                    print("Viewer count changed!")
                previous_viewer_count = viewer_count
                last_viewer_poll = current_time
            except Exception as e:
                print(f"Viewer Error: {e}")
                viewer_polling_interval = min(300, viewer_polling_interval * 2)

        # Monitor Subscriber Count
        if current_time - last_subscriber_poll >= subscriber_polling_interval:
            try:
                subscriber_count = get_subscriber_count(youtube, channel_id)
                print(f"Subscriber Count: {subscriber_count}")
                # React to changes
                if previous_subscriber_count is not None and subscriber_count != previous_subscriber_count:
                    print("Subscriber count changed!")
                previous_subscriber_count = subscriber_count
                last_subscriber_poll = current_time
            except Exception as e:
                print(f"Subscriber Error: {e}")
                subscriber_polling_interval = min(300, subscriber_polling_interval * 2)

        # Sleep until the next polling interval
        time.sleep(chat_polling_interval)

def get_live_chat_id(youtube, video_id):
    request = youtube.videos().list(
        part='liveStreamingDetails',
        id=video_id
    )
    response = request.execute()
    items = response.get('items', [])
    if items:
        live_details = items[0]['liveStreamingDetails']
        live_chat_id = live_details.get('activeLiveChatId')
        if live_chat_id:
            return live_chat_id
    print("No active live chat found.")
    return None

def get_viewer_count(youtube, video_id):
    request = youtube.videos().list(
        part='liveStreamingDetails',
        id=video_id
    )
    response = request.execute()
    items = response.get('items', [])
    if items:
        live_details = items[0]['liveStreamingDetails']
        concurrent_viewers = live_details.get('concurrentViewers')
        return int(concurrent_viewers) if concurrent_viewers else 0
    return 0


def get_live_chat_messages(youtube, live_chat_id, page_token=None):
    request = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part='snippet,authorDetails',
        pageToken=page_token or ''
    )
    response = request.execute()
    return response


def get_subscriber_count(youtube, channel_id):
    request = youtube.channels().list(
        part='statistics',
        id=channel_id
    )
    response = request.execute()
    items = response.get('items', [])
    if items:
        statistics = items[0]['statistics']
        subscriber_count = statistics.get('subscriberCount')
        return int(subscriber_count) if subscriber_count else 0
    return 0

def get_channel_id_from_handle(youtube, handle):

    # Request for the channel details using the handle
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        forHandle=handle
    )
    response = request.execute()

    # Extract the channel ID if available
    if response['items']:
        channel_id = response['items'][0]['id']
        return channel_id
    else:
        return None

def get_live_stream_id(youtube, channel_id):
    # Request for the live broadcasts in the channel
    request = youtube.search().list(
        part='id',
        channelId=channel_id,
        eventType='live',
        type='video'
    )
    response = request.execute()

    # Extract the live stream ID if available
    if response['items']:
        live_stream_id = response['items'][0]['id']['videoId']
        return live_stream_id
    else:
        return 'No live stream found'


def get_channel_id_from_url(channel_url):
    # Extract the channel ID from the URL
    match = re.search(r'channel/([a-zA-Z0-9_-]+)', channel_url)
    if match == None:
        match = channel_url.split('https://www.youtube.com/', 1)
        return match[1]
    if match:
        return match.group(1)
    else:
        return None
if __name__ == '__main__':
    main("https://www.youtube.com/@HealthyGamerGG","UClHVl2N3jPEbkNJVx-ItQIQ","NkRvfSGq0Qk")
