import re
import simplejson as json
from .https import video_data

class Video:

    _HEAD = 'https://www.youtube.com/watch?v='

    def __init__(self, video_id):
        """
        Represents a YouTube video

        Parameters
        ----------
        video_id : str
            The id or url of the video
        """
        # New fixed pattern PR#22
        pattern = re.compile(r'.be/(.*?)$|=(.*?)$|^([\w\-]{11})$')
        try:
            match = pattern.search(video_id)
            if match:
                self._matched_id = match.group(1) or match.group(2) or match.group(3)
            else:
                self._matched_id = None
            if self._matched_id:
                self._url = self._HEAD + self._matched_id
                self._video_data = video_data(self._matched_id)
            else:
                raise ValueError('invalid video id or url')
        except AttributeError:
            pass

    def __repr__(self):
        return '<Video {}>'.format(getattr(self, '_url', ''))

    @property
    def metadata(self):
        """
        Fetches video metadata in a dict format

        Returns
        -------
        Dict
            Video metadata in a dict format containing keys: title, id, views, duration, author_id,
            upload_date, url, thumbnails, tags, description
        """
        details_pattern = re.compile('videoDetails\":(.*?)\"isLiveContent\":.*?}')
        upload_date_pattern = re.compile("<meta itemprop=\"uploadDate\" content=\"(.*?)\">")
        genre_pattern = re.compile("<meta itemprop=\"genre\" content=\"(.*?)\">")
        like_count_pattern = re.compile("iconType\":\"LIKE\"},\"defaultText\":(.*?)}}")
        raw_details = details_pattern.search(self._video_data).group(0)
        upload_date = upload_date_pattern.search(self._video_data).group(1)
        metadata = json.loads(raw_details.replace('videoDetails\":', ''))
        data = {
            'title': metadata['title'],
            'id': metadata['videoId'],
            'views': metadata.get('viewCount'),
            'streamed': metadata['isLiveContent'],
            'duration': metadata['lengthSeconds'],
            'author_id': metadata['channelId'],
            'upload_date': upload_date,
            'url': "https://www.youtube.com/watch?v=%s" % (metadata['videoId']),
            'thumbnails': metadata.get('thumbnail', {}).get('thumbnails'),
            'tags': metadata.get('keywords'),
            'description': metadata.get('shortDescription'),
        }
        try:
            likes_count = like_count_pattern.search(self._video_data).group(1)
            data['likes'] = json.loads(likes_count + '}}}')[
                'accessibility'
            ]['accessibilityData']['label'].split(' ')[0].replace(',', '')
        except (AttributeError, KeyError, ValueError):
            data['likes'] = None
        try:
            data['genre'] = genre_pattern.search(self._video_data).group(1)
        except AttributeError:
            data['genre'] = None
        return data