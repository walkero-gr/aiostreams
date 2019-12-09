#!python
# coding=utf-8
import cfg, cmn, vqw
import cookielib, urllib, urllib2, sys, argparse, re, string
import simplem3u8 as sm3u8
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random

cmnHandler = cmn.cmnHandler()
_url_re = re.compile(r"""
    http(s)?://(\w+.)?wasd\.tv/
    (?:
        channel/(?P<channel_id>\d+)
    )
    (?:
        /(?:videos/)?
        (?P<video_id>\d+)
    )?
""", re.VERBOSE)

class wasdAPIHandler:
    def __init__(self):
        self.baseurl = 'https://wasd.tv/api'

        return None

    def getURL(self, url):
        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request)
            retData = response.read()
            response.close()
            return retData
        except URLError, e:
            print e
        
        return None

    def getApiURL(self, url):
        # Request the anon token and get the cookies
        authUrl = "%s/auth/anon-token" % (self.baseurl)
        cookies = cookielib.CookieJar()
        handlers = [
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.HTTPCookieProcessor(cookies)
        ]
        opener = urllib2.build_opener(*handlers)
        authRequest = urllib2.Request(authUrl)
        authResponse = opener.open(authRequest)

        # Request the endpoint
        request = urllib2.Request(url)
        request.add_header('User-Agent', cmnHandler.spoofAs('CHROME'))
        try:
            response = opener.open(request)
            retData = response.read()
            response.close()
            return retData
        except URLError, e:
            print e
        
        return None

    def call(self, endpoint, query = None):
        url = "%s/%s" % (self.baseurl, endpoint)
        if (query):
            queryArgs = urllib.urlencode(query)
            url = "%s/%s?%s" % (self.baseurl, endpoint, queryArgs)

        return self.getApiURL(url)

    def getVideoInfoByID(self, videoId):
        endpoint = "media-containers/%s" % (videoId)
        query = {
            "media_container_status": "RUNNING",
            "limit": 1,
            "offset": 0,
            "channel_id": videoId,
            "media_container_type": "SINGLE,COOP"
        }

        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def getStreamInfoByID(self, streamId):
        endpoint = "media-containers"
        query = {
            "media_container_status": "RUNNING",
            "limit": 1,
            "offset": 0,
            "channel_id": streamId,
            "media_container_type": "SINGLE,COOP"
        }

        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None


class helpersHandler:
    def parseURL(self, url):
        return _url_re.match(url).groupdict()

    def getVideoType(self, url):
        types = self.parseURL(url)

        return {'channel': types['channel_id'], 'video': types['video_id']}

    def getPrefferedVideoURL(self, data):
        sm3u8Parser = sm3u8.parseHandler()
        playlists = sm3u8Parser.parse(data)
        
        for quality in vqw.wasdVQW:
            for idx in playlists:
                if (playlists[idx]):
                    streamQuality = playlists[idx]
                    if (streamQuality['resolution'].find(quality) >= 0):
                        return playlists[idx]['uri']
        sys.exit()
        return None
        
    def clearUri(self, uri):
        uriSplit = uri.split('#')
        return uriSplit[0]

def main(argv):
    wasdApi = wasdAPIHandler()
    helpers = helpersHandler()
    global videoQualities

    if len(argv) == 0:
        print "No arguments given. Use wasd.py -h for more info.\nThe script must be used from the shell."
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(description=cmnHandler.getScriptDescription('wasd.tv'), epilog=cmnHandler.getScriptEpilog(),
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    argParser.add_argument('-u', '--url', action='store', dest='url', help='The video/channel url')
    argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()
    if (args.url):
        wasdURL = args.url
        videoType = helpers.getVideoType(args.url)
    if (args.quality):
        vqw.wasdVQW.insert(0, args.quality)

    if (videoType['channel'] or videoType['video']):
        if videoType['video']:
            streamId = videoType['video']
            streams = wasdApi.getVideoInfoByID(streamId)
            stream_result = streams['result']
        else:
            streamId = videoType['channel']
            streams = wasdApi.getStreamInfoByID(streamId)
            stream_result = streams['result'][0]

        stream_media = stream_result['media_container_streams'][0]['stream_media']

        if (stream_media):
            m3u8Response = wasdApi.getURL(stream_media[0]['media_meta']['media_url'])
            if (m3u8Response):
                uri = helpers.getPrefferedVideoURL(m3u8Response)
                uri = helpers.clearUri(uri)
                if uri:
                    if cfg.verbose and (args.silence != True):
                        print "%s" % (uri)
                    if cfg.autoplay:
                        cmnHandler.videoAutoplay(uri, 'list')
                else:
                    print "Not valid video found"
        else:
            print "There is no video available!"

        sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])