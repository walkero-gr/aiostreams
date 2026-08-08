import sys
import re

if sys.version_info[0] == 2:
    import urllib2
    from urllib2 import Request, urlopen, HTTPError
    try:
        import simplejson as json
    except ImportError:
        import json

if sys.version_info[0] == 3:
    import json
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

from .errors import InvalidURL, RequestError, TooManyRequests

__all__ = ['dup_filter', 'request', 'extract_initial_data']


def request(url):
    """
    The base function for making a request with proper headers.

    Args:
        url (str): The url to make a request.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/107.0.0.0 Safari/537.36"
        ),
    }
    req = Request(url)
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        resp = urlopen(req)
        return resp.read().decode('utf-8')
    except HTTPError:
        _, e, _ = sys.exc_info()
        if hasattr(e, 'code'):
            if e.code == 404:
                raise InvalidURL('can not find anything with the requested url')
            if e.code == 429:
                raise TooManyRequests('you are being rate-limited for sending too many requests')
        raise RequestError('%r' % e)
    except Exception:
        _, e, _ = sys.exc_info()
        raise RequestError('%r' % e)


def dup_filter(iterable, limit=None):
    """
    Utility function for filtering out duplicate items.

    Args:
        iterable (list): The list of items to filter.
        limit (Optional[int]): The maximum number of items to return.
    """
    if not iterable:
        return []
    lim = limit if limit else len(iterable)

    # Fallback for Python <2.7
    seen = set()
    converted = []
    for item in iterable:
        if item not in seen:
            seen.add(item)
            converted.append(item)

    if len(converted) - lim > 0:
        return converted[:-len(converted) + lim]
    else:
        return converted


def extract_initial_data(html):
    """
    Utility function for extracting the initial data from the HTML of a YouTube page.

    Args:
        html (str): The HTML of the YouTube page.
    """
    pattern = re.compile('ytInitialData = {(.+?)};')
    results = pattern.finditer(html)
    try:
        item = next(results)
    except (NameError, StopIteration):
        item = results.next()
    return json.loads('{' + item.group(1) + '}')
