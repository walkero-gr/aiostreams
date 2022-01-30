#!python
# coding=utf-8
import cfg, cmn, vqw
import urllib, urllib2, sys, argparse, re, string, os
import myurlparse as urlparse
import simplem3u8 as sm3u8
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random
from datetime import datetime

cmnHandler = cmn.cmnHandler()

_url_re = re.compile(r"""(?x)https?://(?:\w+\.)?youtube\.com
    (?:
        (?:
            /(?:
                watch.+v=
                |
                embed/(?!live_stream)
                |
                v/
            )(?P<video_id>[0-9A-z_-]{11})
        )
        |
        (?:
            /(?:
                (?:user|c(?:hannel)?)/
                |
                embed/live_stream\?channel=
            )[^/?&]+
        )
        |
        (?:
            /(?:c/)?[^/?]+/live/?$
        )
    )
""")

class ytAPIHandler:
    def __init__(self):
        self.baseurl = 'https://youtube.com'
        self.apiurl = 'https://www.googleapis.com/youtube/v3'

        return None

    def getClientId(self):
        keyData = aiostreamsapi.getKey()
        return keyData['clientId']

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
            query['key'] = self.getClientId()
            queryArgs = urllib.urlencode(query)
            url = "%s/%s?%s" % (requestUrl, endpoint, queryArgs)

        return self.getURL(url)

    def getVideoInfo(self, videoId):
        endpoint = "get_video_info"
        query = {
            "video_id": videoId,
            # "sts": 18143,
            # "el": "detailpage"
            # "el": "embedded",
            # "eurl": "https://youtube.googleapis.com/v/%s" % (videoId)
        }
        responseData = self.call(endpoint, query)
        if responseData:
            return responseData
        return None
    
    def getLiveStreams(self, m3u8Url):
        return self.getURL(m3u8Url)

    def searchVideo(self, title, limit = 50):
        endpoint = "search"
        query = {
            "order": "relevance",
            "q": title,
            "part": "snippet",
            "type": "video",
            "videoDefinition": "any",
            "videoEmbeddable": "true",
            "fields": "items(id,snippet(channelTitle,liveBroadcastContent,title,publishedAt))",
            "maxResults": limit
        }
        
        responseData = self.call(endpoint, query, True)
        if responseData:
            return json.loads(responseData)
        return None

    def searchLiveStreams(self, title, limit = 50):
        endpoint = "search"
        query = {
            "order": "viewCount",
            "q": title,
            "part": "snippet",
            "type": "video",
            "videoDefinition": "any",
            "videoEmbeddable": "true",
            "eventType": "live",
            "fields": "items(id,snippet(channelTitle,description,liveBroadcastContent,title))",
            "maxResults": limit
        }
        
        responseData = self.call(endpoint, query, True)
        if responseData:
            return json.loads(responseData)
        return None

    def getVideoStatistics(self, videoId):
        endpoint = "videos"
        query = {
            "id": videoId,
            "part": "statistics,contentDetails",
            "fields": "items(id,statistics,contentDetails/duration)"
        }
        
        responseData = self.call(endpoint, query, True)
        if responseData:
            return json.loads(responseData)
        return None

class aiostreamsapiHandler:
    def __init__(self):
        self.baseurl = 'https://aiostreams.amiga-projects.net/v1/youtube'
        
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

    def getVideoInfo(self, videoId):
        endpoint = "get_video_info"
        query = {
            "video_id": videoId
        }
        responseData = self.call(endpoint, query)
        if responseData:
            return responseData
        return None

    def getKey(self):
        endpoint = "getkey"
        responseData = self.call(endpoint)
        if responseData:
            return json.loads(responseData)
        else:
            print 'Key error: Please contact the developer.'
            sys.exit()

class helpersHandler:
    def parseURL(self, url):
        return _url_re.match(url).groupdict()

    def getVideoType(self, url):
        types = self.parseURL(url)

        if (types['video_id']):
            return {'type': 'video', 'video_id': types['video_id']}

        return None

    def getPrefferedVideoURL(self, data, isLive = False):
        for quality in vqw.ytVQW:
            for idx in data:
                if (quality == int(idx['format_id'])):
                    try: 
                        return idx['url']
                    except KeyError:
                        pass

        return None

    def printVideoFormats(self, data):
        print "\nAvailable formats"
        for idx in data:
            print "%s - %sp\t %s, %s" % (idx['format_id'], idx['height'], idx['vcodec'], idx['acodec'])

    def getURLFromCipher(self, cipher):
        cipherParsed = urlparse.parse_qs(cipher)
        return cipherParsed['url'][0]
        
    def parseDate(self, dtime):
        result = datetime.strptime(dtime, '%Y-%m-%dT%H:%M:%SZ')
        return result
        
    def parseDuration(self, dtime):
        result = dtime.replace("PT", '')
        result = result.replace("H", 'h ')
        result = result.replace("M", 'm ')
        result = result.replace("S", 's')
        return result

def main(argv):
    global aiostreamsapi
    aiostreamsapi = aiostreamsapiHandler()
    ytApi = ytAPIHandler()
    helpers = helpersHandler()

    if len(argv) == 0:
        print "No arguments given. Use youtube.py -h for more info.\nThe script must be used from the shell."
        sys.exit()

    ############################################################
    # Parse the arguments
    # 
    argParser = argparse.ArgumentParser(description=cmnHandler.getScriptDescription('youtube.com'), epilog=cmnHandler.getScriptEpilog(),
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    argParser.add_argument('-u', '--url', action='store', dest='url', help='The video url')
    argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
    argParser.add_argument('-sv', '--search-video', action='store', dest='searchvideo', help='Search recorded videos based on description')
    argParser.add_argument('-ss', '--search-streams', action='store', dest='searchstreams', help='Search live streams based on description')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    argParser.add_argument('-x', '--extra-info', action='store_true', default=False, dest='extrainfo', help='Show extra info in search results and video data')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()
    if (args.url):
        video = helpers.getVideoType(args.url)
        videoId = video['video_id']
    if (args.quality):
        vqw.ytVQW.insert(0, int(args.quality))

    ############################################################
    # Search Videos By string
    # 
    if (args.searchvideo):
        searchQuery = args.searchvideo
        result = ytApi.searchVideo(searchQuery)
        if result['items']:
            if args.extrainfo:
                print "%-40s\t %-8s\t %-24s\t %-16s\t %-8s\t %s" % ('URL', 'Views', 'Channel', 'Date', 'Duration', 'Title')
                print "%s" % ('-'*200)
            else:
                print "%-40s\t %-8s\t %s" % ('URL', 'Views', 'Title')
                print "%s" % ('-'*120)
                
            videosDict = dict()
            videoIds = []
            for video in result['items']:
                videoId = video['id']['videoId']
                videosDict[videoId] = dict()
                videosDict[videoId]['url'] = ''.join(["https://www.youtube.com/watch?v=", videoId])
                videosDict[videoId]['title'] = cmnHandler.uniStrip(video['snippet']['title'])
                videosDict[videoId]['channelTitle'] = cmnHandler.uniStrip(video['snippet']['channelTitle'])
                videosDict[videoId]['publishedAt'] = helpers.parseDate(video['snippet']['publishedAt'])
                videoIds.append(videoId)
            
            # Get video statistics in one call
            videoStats = ytApi.getVideoStatistics(','.join(videoIds))
            for stats in videoStats['items']:
                videoId = stats['id']
                videosDict[videoId]['viewCount'] = stats['statistics']['viewCount']
                videosDict[videoId]['duration'] = helpers.parseDuration(stats['contentDetails']['duration'])

            for key, video in videosDict.items():
                if args.extrainfo:
                    print "%-40s\t %-8s\t %-24s\t %-16s\t %-8s\t %s" % (video['url'], video['viewCount'], video['channelTitle'], video['publishedAt'], video['duration'], video['title'])
                else:
                    print "%-40s\t %-8s\t %s" % (video['url'], video['viewCount'], video['title'])
        else:
            print "No videos found based on the search query: %s" % (searchQuery)
        sys.exit()

    ############################################################
    # Search Live Streams By string
    # 
    if (args.searchstreams):
        searchQuery = args.searchstreams
        result = ytApi.searchLiveStreams(searchQuery)
        
        if result['items']:
            print "%-40s\t %-8s\t %s" % ('URL', 'Viewers', 'Title')
            print "%s" % ('-'*120)
            
            videosDict = dict()
            videoIds = []
            for video in result['items']:
                videoId = video['id']['videoId']
                videosDict[videoId] = dict()
                videosDict[videoId]['url'] = ''.join(["https://www.youtube.com/watch?v=", videoId])
                videosDict[videoId]['title'] = cmnHandler.uniStrip(video['snippet']['title'])
                videoIds.append(videoId)
            
            # Get video statistics in one call
            videoStats = ytApi.getVideoStatistics(','.join(videoIds))
            for stats in videoStats['items']:
                videoId = stats['id']
                videosDict[videoId]['viewCount'] = stats['statistics']['viewCount']

            for key, video in videosDict.items():
                try:
                    videoViewCount = video['viewCount'] 
                except KeyError:
                    videoViewCount = 'N/A'
                print "%-40s\t %-8s\t %s" % (video['url'], videoViewCount, video['title'])
        else:
            print "No live streams found based on the search query: %s" % (searchQuery)
        sys.exit()

    ############################################################
    # Return info for recorded/live video and stream it
    # 
    if (videoId):
        videoInfo = aiostreamsapi.getVideoInfo(videoId)
        if videoInfo:
            response = json.loads(videoInfo)

            isLive = False
            try:
                if (response['is_live']):
                    isLive = True
            except KeyError:
                pass

            if (args.silence != True):
                print "Title: %s" % (cmnHandler.uniStrip(response['title']))

            if args.extrainfo and (args.silence != True):
                helpers.printVideoFormats(response['formats'])

            videoFormats = response['formats']
            uri = helpers.getPrefferedVideoURL(videoFormats, isLive)

            if (uri):
                if cfg.verbose and (args.silence != True):
                    print "\n%s" % (uri)
                if cfg.autoplay:
                    if (isLive):
                        cmnHandler.videoAutoplay(uri, 'list')
                    else:
                        cmnHandler.videoAutoplay(uri, 'video')
            else:
                print "Not valid video url found!"
        else:
            print "There is info available about this video!"

        sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])

