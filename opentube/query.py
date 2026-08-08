from .channel import Channel
from .https import find_channels, find_playlists, find_videos
from .patterns import _QueryPatterns as Patterns
from .playlist import Playlist
from .utils import dup_filter
from .video import Video


class Search:

    @staticmethod
    def video(keywords):
        video_ids = Patterns.video_id.findall(find_videos(keywords))
        return Video(video_ids[0]) if video_ids else None

    @staticmethod
    def channel(keywords):
        channel_ids = Patterns.channel_id.findall(find_channels(keywords))
        return Channel(channel_ids[0]) if channel_ids else None

    @staticmethod
    def playlist(keywords):
        playlist_ids = Patterns.playlist_id.findall(find_playlists(keywords))
        return Playlist(playlist_ids[0]) if playlist_ids else None

    @staticmethod
    def videos(keywords, limit=20):
        return dup_filter(Patterns.video_id.findall(find_videos(keywords)), limit)

    @staticmethod
    def channels(keywords, limit=20):
        return dup_filter(Patterns.channel_id.findall(find_channels(keywords)), limit)

    @staticmethod
    def playlists(keywords, limit=20):
        return dup_filter(Patterns.playlist_id.findall(find_playlists(keywords)), limit)
