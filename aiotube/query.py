from __future__ import absolute_import

from .utils import dup_filter
from .video import Video
from .channel import Channel
from .playlist import Playlist
from .patterns import _QueryPatterns as Patterns
from .https import find_videos, find_channels, find_playlists

class Search(object):
    @staticmethod
    def video(keywords):
        """
        :param keywords: str
        :return: Video or None
        """
        video_ids = Patterns.video_id.findall(find_videos(keywords))
        if video_ids:
            return Video(video_ids[0])
        return None

    @staticmethod
    def channel(keywords):
        """
        :param keywords: str
        :return: Channel or None
        """
        channel_ids = Patterns.channel_id.findall(find_channels(keywords))
        if channel_ids:
            return Channel(channel_ids[0])
        return None

    @staticmethod
    def playlist(keywords):
        """
        :param keywords: str
        :return: Playlist or None
        """
        playlist_ids = Patterns.playlist_id.findall(find_playlists(keywords))
        if playlist_ids:
            return Playlist(playlist_ids[0])
        return None

    @staticmethod
    def videos(keywords, limit=20):
        """
        :param keywords: str
        :param limit: int
        :return: list or None
        """
        return dup_filter(Patterns.video_id.findall(find_videos(keywords)), limit)

    @staticmethod
    def channels(keywords, limit=20):
        """
        :param keywords: str
        :param limit: int
        :return: list or None
        """
        return dup_filter(Patterns.channel_id.findall(find_channels(keywords)), limit)

    @staticmethod
    def playlists(keywords, limit=20):
        """
        :param keywords: str
        :param limit: int
        :return: list or None
        """
        return dup_filter(Patterns.playlist_id.findall(find_playlists(keywords)), limit)
