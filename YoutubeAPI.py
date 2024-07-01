
from googleapiclient.discovery import build
import re

def get_channel_id_from_handle(api_key, handle):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Request for the channel details using the handle
    request = youtube.search().list(
        part='snippet',
        q=handle,
        type='channel'
    )
    response = request.execute()
    
    # Extract the channel ID if available
    if response['items']:
        channel_id = response['items'][0]['snippet']['channelId']
        return channel_id
    else:
        return None

def get_subscriber_count(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Request for the channel statistics
    request = youtube.channels().list(
        part='statistics',
        id=channel_id
    )
    response = request.execute()

    # Extract the subscriber count if available
    if response['items']:
        subscriber_count = response['items'][0]['statistics']['subscriberCount']
        return subscriber_count
    else:
        return 'No subscriber data found'
    
def get_live_stream_id(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

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

def get_live_viewers(api_key, live_stream_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Request for the live stream details
    request = youtube.videos().list(
        part='liveStreamingDetails',
        id=live_stream_id
    )
    response = request.execute()

    # Extract the number of concurrent viewers
    live_details = response['items'][0]['liveStreamingDetails']
    concurrent_viewers = live_details.get('concurrentViewers', 'Not live')

    return concurrent_viewers
def getYoutubeStats(channel_handle_url):

    # Replace with your API key and channel handle URL
    api_key = 'AIzaSyDkjeGFhKizc5IoaZtLuS3cqfJvVxjpb1U'
    
    # Extract the handle from the URL
    match = re.search(r'@([a-zA-Z0-9_]+)', channel_handle_url)
    if match==None:
        match = get_channel_id_from_url(channel_handle_url)
    if match:
        try:
            handle = match.group(0)
        except:
            handle = match
        channel_id = get_channel_id_from_handle(api_key, handle)
        if channel_id:
            live_stream_id = get_live_stream_id(api_key, channel_id)
            print(f'Live stream ID: {live_stream_id}')
            viewers = get_live_viewers(api_key, live_stream_id)
            subs= get_subscriber_count(api_key, channel_id)
            print(f'Current live viewers: {viewers}')
            print(f'Subscribers: {subs}')
            return [subs,viewers]
        else:
            print('Invalid channel handle or no channel found')
    else:
        print('Invalid channel URL')



getYoutubeStats('https://www.youtube.com/@NBCNews')