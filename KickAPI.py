import requests
from bs4 import BeautifulSoup
import json
# URL of the resource you want to access

def getKickAPI(username):

        # Headers to simulate a
    url = 'https://kick.com/api/v2/channels/4Fortune8'

    # Headers to simulate a request from a real browser
    headers = {
                "Accept": "application/json",
                "Accept-Language": "ar,en-US;q=0.7,en;q=0.3",
                "Alt-Used": "kick.com",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"
            }
    # Making the GET request with custom headers
    response = requests.get(url, headers=headers)

    # Check the status code
    if response.status_code == 200:
        print('Request was successful')
        # Print the content of the response

    # Try to parse the text as JSON
        try:
                data = json.loads(response.text)
                # Access channel attributes
                if data:
                    print("Channel ID:", data["id"])
                    print("Username:", data["user"]["username"])
                    print("Bio:", data["user"]["bio"])
                    print("Avatar URL:", data["user"]["profile_pic"])
                    print("Followers:", data["followers_count"])
                    print("Playback URL:", data["playback_url"])
                    try:
                        print("Current live viewers:", data["livestream"]["viewer_count"])
                        return [data["followers_count"],data["livestream"]["viewer_count"] ]
                    except:
                        print("Channel is not live")
                    return data
        except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")

