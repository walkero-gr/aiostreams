import sys

if sys.version_info[0] == 2:
    from urllib import quote

if sys.version_info[0] == 3:
    from urllib.parse import quote

from .utils import request


def channel_about(head):
    return request('%s/about' % head)


def uploads_data(head):
    return request('%s/videos' % head)


def shorts_data(head):
    return request('%s/shorts' % head)


def streams_data(head):
    return request('%s/streams' % head)


def channel_playlists(head):
    return request('%s/playlists' % head)


def upcoming_videos(head):
    return request('%s/videos?view=2&live_view=502' % head)


def video_data(video_id):
    return request('https://www.youtube.com/watch?v=%s' % video_id)


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
