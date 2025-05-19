import os
from dotenv import load_dotenv
from urllib.parse import urlencode
import requests


def get_youtube_videos(query: str, results: int = 5):
    load_dotenv()
    API_KEY = os.getenv('YOUTUBE_API_KEY')

    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': results,
        'key': API_KEY
    }

    url = f'https://www.googleapis.com/youtube/v3/search?{urlencode(params)}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        videos = []
        for item in data.get('items', []):
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            video_url = f'https://www.youtube.com/embed/{video_id}'
            videos.append({
                'id': video_id,
                'title': title,
                'url': video_url
            })
        return videos
    else:
        return []
