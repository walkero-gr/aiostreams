import sys
from .errors import TooManyRequests, InvalidURL, RequestError

if sys.version_info[0] == 2:
    import urllib
    import urllib2
    from urllib2 import Request, urlopen, HTTPError

if sys.version_info[0] == 3:
    import urllib.parse as urllib
    import urllib3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    __all__ = ['dup_filter', 'request']

def request(url):
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
