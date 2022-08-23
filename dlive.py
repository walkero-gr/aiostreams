#!python
# coding=utf-8
import cfg, cmn, vqw
import urllib, urllib2, sys, argparse, re, string
import simplem3u8 as sm3u8
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random

cmnHandler = cmn.cmnHandler()

_url_re = re.compile(r"""
    http(s)?://(\w+.)?dlive\.tv/
    (?:
        p/(?P<video_id>[^/]+)|
        (?P<channel>[^/]+)
    )?
""", re.VERBOSE)

class dliveAPIHandler:
    def __init__(self):
        self.baseurl = 'http://aiostreams.amiga-projects.net/v1/dlive'
        self.apiurl = 'https://live.prd.dlive.tv'

        return None

    def getURL(self, url):
        request = urllib2.Request(url)
        request.add_header('User-Agent', cmnHandler.spoofAs('CHROME'))

        try:
            response = urllib2.urlopen(request)
            retData = response.read()
            response.close()
            return retData
        except URLError, e:
            print e
        
        return None

    def call(self, endpoint, query = None, apiCall = False):
        requestUrl = self.baseurl
        if apiCall:
            requestUrl = self.apiurl

        url = "%s/%s" % (requestUrl, endpoint)
        if (query):
            queryArgs = urllib.urlencode(query)
            url = "%s/%s?%s" % (requestUrl, endpoint, queryArgs)
        
        return self.getURL(url)

    def getChannelInfoByName(self, channelName):
        endpoint = "channel/%s" % (channelName)
        responseData = self.call(endpoint)
        if responseData:
            return responseData
        return None

    def getVideoInfoByName(self, videoId):
        endpoint = "video/%s" % (videoId)
        responseData = self.call(endpoint)
        if responseData:
            return responseData
        return None

    def getStreamsByUsername(self, username):
        endpoint = "hls/live/%s.m3u8" % (username)
        responseData = self.call(endpoint, None, True)
        if responseData:
            return responseData
        return None

class helpersHandler:
    def parseURL(self, url):
        return _url_re.match(url).groupdict()

    def getVideoType(self, url):
        types = self.parseURL(url)
        
        if (types['video_id']):
            return {'type': 'video', 'id': types['video_id']}

        if (types['channel']):
            return {'type': 'channel', 'id': types['channel']}

        return None

    def getPrefferedVideoURL(self, data):
        sm3u8Parser = sm3u8.parseHandler()
        playlists = sm3u8Parser.parse(data)
        
        for quality in vqw.dliveVQW:
            for idx in playlists:
                if (playlists[idx]):
                    if (playlists[idx]['name'].find(quality) >= 0):
                        return playlists[idx]['uri']
        
        return None

    def getDisplayName(self, jsondata):
        jsonDict = json.loads(jsondata)
        for key, values in jsonDict['defaultClient'].items():
            if (key.startswith('user:')):
                try:
                    return values['displayname']
                except KeyError:
                    pass
        
        return None

    def getUserName(self, jsondata):
        jsonDict = json.loads(jsondata)
        for key, values in jsonDict['defaultClient'].items():
            if (key.startswith('user:')):
                try:
                    return values['username']
                except KeyError:
                    pass
        
        return None

    def getChanneAbout(self, jsondata):
        jsonDict = json.loads(jsondata)
        for key, values in jsonDict['defaultClient'].items():
            if (key.startswith('user:')):
                try:
                    return values['about']
                except KeyError:
                    pass
        
        return None

    def isLiveStream(self, jsondata):
        jsonDict = json.loads(jsondata)
        for key, values in jsonDict['defaultClient'].items():
            if (key.startswith('user:')):
                try:
                    if values['livestream']:
                        return True
                except KeyError:
                    pass
        
        return None

    def getLiveStreamId(self, jsondata):
        jsonDict = json.loads(jsondata)
        for key, values in jsonDict['defaultClient'].items():
            if (key.startswith('user:')):
                if values['livestream']:
                    try:
                        return values['livestream']['id']
                    except KeyError:
                        pass
        
        return None

    def getPlaybackUrl(self, jsondata):
        jsonDict = json.loads(jsondata)
        for key, values in jsonDict['defaultClient'].items():
            if (key.startswith('$ROOT_QUERY.pastBroadcast') and key.endswith('})')):
                try:
                    return values['playbackUrl']
                except KeyError:
                    pass

        return None


def main(argv):
    dliveApi = dliveAPIHandler()
    helpers = helpersHandler()

    if len(argv) == 0:
        print "No arguments given. Use dlive.py -h for more info.\nThe script must be used from the shell."
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(description=cmnHandler.getScriptDescription('dlive.tv'), epilog=cmnHandler.getScriptEpilog(),
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    argParser.add_argument('-u', '--url', action='store', dest='url', help='The video/channel url')
    argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()
    if (args.url):
        video = helpers.getVideoType(args.url)

    if (args.quality):
        vqw.dliveVQW.insert(0, args.quality)

    if (video['type'] == 'channel'):
        channelName = video['id']
        apolloJson = dliveApi.getChannelInfoByName(channelName)

        username = helpers.getUserName(apolloJson)

        if helpers.isLiveStream:
            m3u8Response = dliveApi.getStreamsByUsername(username)

            if (m3u8Response):
                uri = helpers.getPrefferedVideoURL(m3u8Response)
                if uri:
                    if cfg.verbose and (args.silence != True):
                        print "%s" % (uri)
                    if cfg.autoplay:
                        cmnHandler.videoAutoplay(uri, 'video')
                else:
                    print "Not valid stream found"
            else:
                print "There was an error with the m3u8 reading"

        sys.exit()

    if (video['type'] == 'video'):
        video = video['id']
        apolloJson = dliveApi.getVideoInfoByName(video)

        username = helpers.getUserName(apolloJson)
        playbackUrl = helpers.getPlaybackUrl(apolloJson)

        m3u8Response = dliveApi.getURL(playbackUrl)
        if (m3u8Response):
            uri = helpers.getPrefferedVideoURL(m3u8Response)
            if uri:
                if cfg.verbose and (args.silence != True):
                    print "%s" % (uri)
                if cfg.autoplay:
                    cmnHandler.videoAutoplay(uri, 'video')
            else:
                print "Not valid video found"
        else:
            print "There was an error with the m3u8 reading"

        sys.exit()

    sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
