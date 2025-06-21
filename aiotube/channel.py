import sys
import re
import simplejson as json

if sys.version_info[0] == 2:
    import urllib
    import urllib2
    unquote = urllib.unquote
else:
    from urllib.parse import unquote

from .https import (
    channel_about,
    streams_data,
    uploads_data,
    channel_playlists,
    upcoming_videos
)
from .video import Video
from .pool import collect
from .utils import dup_filter
from .patterns import _ChannelPatterns as Patterns

class Channel(object):

    _HEAD = 'https://www.youtube.com/channel/'
    _CUSTOM = 'https://www.youtube.com/c/'
    _USER = 'https://www.youtube.com/'

    def __init__(self, channel_id):
        pattern = re.compile("UC(.+)|c/(.+)|@(.+)")
        results = pattern.findall(channel_id)
        if not results:
            self._usable_id = channel_id
            self._target_url = self._CUSTOM + channel_id
        elif results[0][0]:
            self._usable_id = results[0][0]
            self._target_url = self._HEAD + 'UC' + results[0][0]
        elif results[0][1]:
            self._usable_id = results[0][1]
            self._target_url = self._CUSTOM + results[0][1]
        elif results[0][2]:
            self._usable_id = results[0][2]
            self._target_url = self._USER + '@' + results[0][2]
        self.id = None
        self.name = None
        self.subscribers = None
        self.views = None
        self.country = None
        self.custom_url = None
        self.avatar = None
        self.banner = None
        self.url = None
        self.description = None
        self.socials = None
        self.__meta = None
        self._about_page = channel_about(self._target_url)
        self.__populate()

    def __populate(self):
        self.__meta = self.__prepare_metadata()
        for k, v in self.__meta.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<Channel `{}`>'.format(self._target_url)

    def __prepare_metadata(self):
        patterns = [
            Patterns.name,
            Patterns.avatar,
            Patterns.banner,
            Patterns.verified,
            Patterns.socials
        ]
        extracted = collect(lambda x: x.findall(self._about_page) or None, patterns)
        name, avatar, banner, verified, socials = [e[0] if e else None for e in extracted]
        info_match = re.compile("\\[{\"aboutChannelRenderer\":(.*?)],").search(self._about_page)
        if info_match:
            info = info_match.group(1) + "]}}}}"
        else:
            info = ""
        try:
            info = json.loads(info)["metadata"]["aboutChannelViewModel"]
        except Exception:
            try:
                info = re.compile("\\[{\"aboutChannelRenderer\":(.*?)],").search(self._about_page).group(1) + "]}}}"
                info = json.loads(info)["metadata"]["aboutChannelViewModel"]
            except Exception:
                info = re.compile("\\[{\"aboutChannelRenderer\":(.*?)],").search(self._about_page).group(1)
                info = json.loads(info[:len(info)-1])["metadata"]["aboutChannelViewModel"]

        return {
            "id": info.get("channelId", ""),
            "name": name,
            "url": "https://www.youtube.com/channel/" + info.get("channelId", ""),
            "description": info.get("description", ""),
            "country": info.get("country", ""),
            "custom_url": info.get("canonicalChannelUrl", ""),
            "subscribers": info.get("subscriberCountText", "").split(' ')[0] if info.get("subscriberCountText") else "",
            "views": info.get("viewCountText", "").replace(' views', '') if info.get("viewCountText") else "",
            "created_at": info.get("joinedDateText", {}).get("content", "").replace('Joined ', "") if info.get("joinedDateText") else "",
            "video_count": info.get("videoCountText", "").split(' ')[0] if info.get("videoCountText") else "",
            "avatar": avatar,
            "banner": banner,
            "verified": bool(verified),
            "socials": unquote(socials) if socials else ""
        }

    @property
    def metadata(self):
        return self.__meta

    @property
    def live(self):
        return bool(self.current_streams)

    @property
    def streaming_now(self):
        streams = self.current_streams
        return streams[0] if streams else None

    @property
    def current_streams(self):
        raw = streams_data(self._target_url)
        filtered_ids = dup_filter(Patterns.stream_ids.findall(raw))
        if not filtered_ids:
            return None
        return [id_ for id_ in filtered_ids if "vi/{}/hqdefault_live.jpg".format(id_) in raw]

    @property
    def old_streams(self):
        raw = streams_data(self._target_url)
        filtered_ids = dup_filter(Patterns.stream_ids.findall(raw))
        if not filtered_ids:
            return None
        return [id_ for id_ in filtered_ids if "vi/{}/hqdefault_live.jpg".format(id_) not in raw]

    @property
    def last_streamed(self):
        ids = self.old_streams
        return ids[0] if ids else None

    def uploads(self, limit=20):
        return dup_filter(Patterns.upload_ids.findall(uploads_data(self._target_url)), limit)

    @property
    def last_uploaded(self):
        ids = self.uploads()
        return ids[0] if ids else None

    @property
    def upcoming(self):
        raw = upcoming_videos(self._target_url)
        if not Patterns.upcoming_check.search(raw):
            return None
        upcoming = Patterns.upcoming.findall(raw)
        return Video(upcoming[0]) if upcoming else None

    @property
    def upcomings(self):
        raw = upcoming_videos(self._target_url)
        if not Patterns.upcoming_check.search(raw):
            return None
        video_ids = Patterns.upcoming.findall(raw)
        return video_ids

    @property
    def playlists(self):
        return dup_filter(Patterns.playlists.findall(channel_playlists(self._target_url)))
