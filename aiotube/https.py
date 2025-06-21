import sys
from .utils import request

if sys.version_info[0] == 2:
    import urllib
    import urllib2
    quote = urllib.quote
else:
    from urllib.parse import quote

def channel_about(head):
    return request(head + '/about')


def video_count(channel_id):
    head = 'https://www.youtube.com/results?search_query='
    tail = '&sp=EgIQAg%253D%253D'
    return request(head + channel_id + tail)


def uploads_data(head):
    url = head + '/videos'
    return request(url)


def streams_data(head):
    url = head + '/streams'
    return request(url)


def channel_playlists(head):
    url = head + '/playlists'
    return request(url)


def upcoming_videos(head):
    url = head + '/videos?view=2&live_view=502'
    return request(url)


def video_data(video_id):
    url = 'https://www.youtube.com/watch?v=' + video_id
    return request(url)


def playlist_data(playlist_id):
    url = 'https://www.youtube.com/playlist?list=' + playlist_id
    return request(url)


def trending_videos():
    return request('https://www.youtube.com/feed/trending')


def trending_songs():
    return request('https://www.youtube.com/feed/music')


def trending_games():
    return request('https://www.youtube.com/gaming')


def trending_feeds():
    return request('https://www.youtube.com/news')


def trending_streams():
    return request('https://www.youtube.com/live')


def _get_trending_learning_videos():
    return request('https://www.youtube.com/learning')


def trending_sports():
    return request('https://www.youtube.com/sports')


def find_videos(query):
    head = 'https://www.youtube.com/results?search_query='
    tail = '&sp=EgIQAQ%253D%253D'
    return request(head + quote(query) + tail)


def find_channels(query):
    head = 'https://www.youtube.com/results?search_query='
    tail = '&sp=EgIQAg%253D%253D'
    return request(head + quote(query) + tail)


def find_playlists(query):
    head = 'https://www.youtube.com/results?search_query='
    tail = '&sp=EgIQAw%253D%253D'
    return request(head + quote(query) + tail)
