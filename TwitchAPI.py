import requests

def get_oauth_token(client_id, client_secret):
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()['access_token']

def get_user_id(client_id, access_token, username):
    url = 'https://api.twitch.tv/helix/users'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'login': username
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    if data['data']:
        return data['data'][0]['id']
    else:
        raise ValueError(f'User {username} not found')

def get_followers_count(client_id, access_token, user_id):
    url = f'https://api.twitch.tv/helix/channels/followers?broadcaster_id={user_id}'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data['total']

def get_stream_views(client_id, access_token, username):
    url = 'https://api.twitch.tv/helix/streams'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'user_login': username
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    if data['data']:
        return data['data'][0]['viewer_count']
    else:
        return 'Stream is not live'

# Replace with your Twitch client ID, client secret, and username
def getTwitchData(username):
    client_id = 'vrxefmrp3ri462ot6sh2z5g1cy57q5'
    client_secret = 'fimfe3mj8psivfyuh4d0v2euqks40v'


    # Get OAuth token
    access_token = get_oauth_token(client_id, client_secret)

    # Get stream views
    views = get_stream_views(client_id, access_token, username)
    user_id = get_user_id(client_id, access_token, username)

    # Get followers count
    followers_count = get_followers_count(client_id, access_token, user_id)
    print(f'Current live viewers: {views}')
    print(f'Followers count: {followers_count}')
    return [followers_count,views]


