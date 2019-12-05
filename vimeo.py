#!python
# coding=utf-8
import cfg, cmn
import urllib, urllib2, sys, argparse, re, string
import simplem3u8 as sm3u8
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random

cmnHandler = cmn.cmnHandler()
_url_re = re.compile(r"""
    http(s)?://(\w+.)?vimeo\.com/
    (?:
        channels/(?P<channel>[^/?]+)/(?P<videos_id>[^/?]+)|
        (?P<video_id>[^/?]+)
    )?
""", re.VERBOSE)

class vimeoAPIHandler:
    def __init__(self):
        self.baseurl = 'https://player.vimeo.com'

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

    def call(self, endpoint, query = None):
        url = "%s/%s" % (self.baseurl, endpoint)
        if (query):
            queryArgs = urllib.urlencode(query)
            url = "%s/%s?%s" % (self.baseurl, endpoint, queryArgs)

        return self.getURL(url)

    def getVideoInfoByID(self, videoId):
        endpoint = "video/%s/config" % (videoId)
        responseData = self.call(endpoint)
        if responseData:
            return json.loads(responseData)
        return None

class helpersHandler:
    def parseURL(self, url):
        return _url_re.match(url).groupdict()

    def getVideoType(self, url):
        types = self.parseURL(url)
        
        if (types['video_id']):
            return {'type': 'video', 'id': types['video_id']}

        if (types['videos_id']):
            return {'type': 'video', 'id': types['videos_id'], 'channel': types['channel']}

        return None

    def getPrefferedVideoURL(self, data):
        sm3u8Parser = sm3u8.parseHandler()
        playlists = sm3u8Parser.parse(data)
        
        for quality in cfg.vimeoQualityWeight:
            for idx in playlists:
                if (playlists[idx]):
                    streamQuality = self.getQualityByUri(playlists[idx]['uri'])
                    if (streamQuality.find(quality) >= 0):
                        return playlists[idx]['uri']
        
        return None

    def getQualityByUri(self, uri):
        for idx, quality in videoQualities.items():
            if (uri.find(str(idx)) >= 0):
                return quality

        return None

    def getVideoQualities(self, data):
        retData = dict()
        for stream in data['streams']:
            retData[stream['id']] = stream['quality']

        return retData

    def buildUri(self, cdnurl, uri):
        uriClean = uri.replace("../", "")
        cdnSplit = cdnurl.split('/')

        for x in range(2):
            delIdx = len(cdnSplit) - 1
            del(cdnSplit[delIdx])

        retUri = '/'.join(cdnSplit)
        retUri = '%s/%s' % (retUri, uriClean)

        return retUri


def main(argv):
    vimeoApi = vimeoAPIHandler()
    helpers = helpersHandler()
    global videoQualities

    if len(argv) == 0:
        print "No arguments given. Use vimeo.py -h for more info.\nThe script must be used from the shell."
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(description='This is a python script that uses vimeo.com to get information about videos for AmigaOS 4.1 and above.')
    argParser.add_argument('-u', '--url', action='store', dest='url', help='The video url from vimeo.com')
    argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()
    if (args.url):
        vimeoURL = args.url
        video = helpers.getVideoType(args.url)
    if (args.quality):
        cfg.vimeoQualityWeight.insert(0, args.quality)

    if (video['type'] == 'video'):
        videoId = video['id']
        streams = vimeoApi.getVideoInfoByID(videoId)
        videos = streams['request']['files']
        videoQualities = helpers.getVideoQualities(videos['dash'])

        if (videos['hls']['cdns']):
            cdns = videos['hls']['cdns']
            for idx in cdns:
                if (cdns[idx]['url']):
                    m3u8Response = vimeoApi.getURL(cdns[idx]['url'])
                    if (m3u8Response):
                        break

            if (m3u8Response):
                uri = helpers.getPrefferedVideoURL(m3u8Response)
                if uri:
                    playlistUri = helpers.buildUri(cdns[idx]['url'], uri)
                    if cfg.verbose and (args.silence != True):
                        print "%s" % (playlistUri)
                    if cfg.autoplay:
                        cmnHandler.videoAutoplay(playlistUri, 'list')
                else:
                    print "Not valid video found"
        else:
            print "There is no video available!"

        sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])