#!python
# coding=utf-8
import cfg, cmn, vqw
import sys, argparse, re, os
import myurlparse as urlparse
import simplejson as json
import aiotube as aiotube
from datetime import datetime, timedelta

if sys.version_info[0] == 2:
    import urllib
    import urllib2
    from urllib2 import Request as urlReq, urlopen as urlOpn, URLError

if sys.version_info[0] == 3:
    import urllib.parse as urllib
    import urllib3
    from urllib.request import Request as urlReq, urlopen as urlOpn
    from urllib.error import URLError

cmnHandler = cmn.cmnHandler()

_url_re = re.compile(r"""(?x)https?://
    (?:
        (?:
            (?:\w+\.)?\w+\.\w+
        )
        |
        (?:
            youtu\.be
        )
    )
    (?:
        (?:
            /(?:
                (?:
                    watch.+v=
                    |
                    embed/(?!live_stream)
                    |
                    v/
                    |
                    shorts/
                )
                |
                (?:)
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
        request = urlReq(url)
        request.add_header('User-Agent', cmnHandler.spoofAs('CHROME'))
        try:
            response = urlOpn(request)
            retData = response.read()
            response.close()
            return retData
        except (URLError):
            print (URLError["reason"])
        
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
            "video_id": videoId
        }
        responseData = self.call(endpoint, query)
        if responseData:
            return responseData
        return None
    
    def getLiveStreams(self, m3u8Url):
        return self.getURL(m3u8Url)

    def searchChannel(self, title, limit = 50):
        endpoint = "search"
        query = {
            "order": "relevance",
            "q": title,
            "part": "snippet",
            "type": "channel",
            "fields": "items(id,snippet(channelTitle))",
            "maxResults": limit
        }
        
        responseData = self.call(endpoint, query, True)
        if responseData:
            return json.loads(responseData)
        return None

    def searchVideo(self, title, minInfo = None, pageToken = None, limit = 50):
        endpoint = "search"
        query = {
            "order": "relevance",
            "q": title,
            "part": "snippet",
            "type": "video",
            "videoDefinition": "any",
            "videoEmbeddable": "true",
            "fields": "",
            "maxResults": limit
        }

        if (minInfo):
            query["fields"] = "nextPageToken"
        else:
            query["fields"] = "items(id,snippet(channelTitle,liveBroadcastContent,title,publishedAt)),nextPageToken"

        if (pageToken):
            query["pageToken"] = pageToken

        responseData = self.call(endpoint, query, True)
        if responseData:
            return json.loads(responseData)
        return None

    def searchLiveStreams(self, title, minInfo = None, pageToken = None, limit = 50):
        endpoint = "search"
        query = {
            "order": "viewCount",
            "q": title,
            "part": "snippet",
            "type": "video",
            "videoDefinition": "any",
            "videoEmbeddable": "true",
            "eventType": "live",
            "maxResults": limit
        }
        
        if (minInfo):
            query["fields"] = "nextPageToken"
        else:
            query["fields"] = "items(id,snippet(channelTitle,description,liveBroadcastContent,title)),nextPageToken,prevPageToken"

        if (pageToken):
            query["pageToken"] = pageToken

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
        request = urlReq(url)

        try:
            response = urlOpn(request)
            retData = response.read()
            response.close()
            return retData
        except (URLError):
            print (URLError["reason"])
        
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
            print ('Key error: Please contact the developer.')
            sys.exit()

class helpersHandler:
    def parseURL(self, url):
        try:
            return _url_re.match(url).groupdict()
        except AttributeError:
            print ('The provided url is not valid')
            sys.exit()
        

    def getVideoType(self, url):
        types = self.parseURL(url)

        if (types['video_id']):
            return {'type': 'video', 'video_id': types['video_id']}

        return None

    def getPrefferedVideoURL(self, data, isLive = False):
        for quality in vqw.ytVQW:
            for idx in data:
                try:
                    if (quality == int(idx['format_id'])):
                        try: 
                            return idx['url']
                        except KeyError:
                            pass
                except ValueError:
                    pass

        return None

    def printVideoFormats(self, data):
        print ("\nAvailable formats")
        print ("%-4s\t%-8s\t%-12s\t%-12s" % ('ID', 'Height', 'VCodec', 'ACodec'))
        print ("%s" % ('-'*52))
        for idx in data:
            vHeight = "na"
            vCodec = "na"
            aCodec = "na"
            try:
                vHeight = idx['height']
                vCodec = idx['vcodec']
                aCodec = idx['acodec']
            except (ValueError, KeyError):
                pass
            print ("%-4s\t%-8s\t%-12s\t%-12s" % (idx['format_id'], vHeight, vCodec, aCodec))
        sys.exit()

    def getURLFromCipher(self, cipher):
        cipherParsed = urlparse.parse_qs(cipher)
        return cipherParsed['url'][0]
        
    def parseDate(self, dtime):
        result = datetime.strptime(dtime, '%Y-%m-%dT%H:%M:%S%z')
        return result
        
    def parseDuration(self, dtime):
        return str(timedelta(seconds=int(dtime)))

def main(argv):
    global aiostreamsapi
    aiostreamsapi = aiostreamsapiHandler()
    ytApi = ytAPIHandler()
    helpers = helpersHandler()

    if len(argv) == 0:
        print ("No arguments given. Use youtube.py -h for more info.\nThe script must be used from the shell.")
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
    argParser.add_argument('-sc', '--search-channel', action='store', dest='searchchannel', help='Search channels based on description')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    argParser.add_argument('-p', '--page', action='store', dest='page', help='Set the page of search results, so to get more videos. This needs to be an integer greater than 0 and can be used with -sv and -ss')
    argParser.add_argument('-x', '--extra-info', action='store_true', default=False, dest='extrainfo', help='Show extra info in search results and video data')
    args = argParser.parse_args()

    startPage = 1

    if (args.silence != True):
        cmnHandler.showIntroText()
    if (args.url):
        video = helpers.getVideoType(args.url)
        videoId = video['video_id']
    if (args.quality):
        vqw.ytVQW.insert(0, int(args.quality))
    if (args.page):
        try:
            if (int(args.page) > 0):
                startPage = int(args.page)
        except (TypeError, ValueError):
            pass

    ############################################################
    # Search Videos By string
    # 
    if (args.searchvideo):
        searchQuery = args.searchvideo

        result = aiotube.Search.videos(searchQuery)
        if len(result) > 0:
            if args.extrainfo:
                print ("%-40s\t %-8s\t %-24s\t %-16s\t %-8s\t %s" % ('URL', 'Views', 'Channel', 'Date', 'Duration', 'Title'))
                print ("%s" % ('-'*200))
            else:
                print ("%-40s\t %-8s\t %s" % ('URL', 'Duration', 'Title'))
                print ("%s" % ('-'*120))
                
            videosDict = dict()
            videoIds = []
            for id in result:
                video = aiotube.Video(id)
                channel = aiotube.Channel(video.metadata['author_id'])

                videoId = id
                videosDict[videoId] = dict()
                videosDict[videoId]['url'] = video.metadata['url']
                videosDict[videoId]['title'] = video.metadata['title']
                videosDict[videoId]['channelTitle'] = cmnHandler.uniStrip(channel.metadata['name'])
                videosDict[videoId]['publishedAt'] = helpers.parseDate(video.metadata['upload_date'])
                videosDict[videoId]['viewCount'] = video.metadata['views']
                videosDict[videoId]['duration'] = helpers.parseDuration(video.metadata['duration'])
                videoIds.append(videoId)

            for key, video in videosDict.items():
                if args.extrainfo:
                    print (
                        "%-40s\t %-8s\t %-24s\t %-16s\t %-8s\t %s" % (
                            video['url'], video['viewCount'], video['channelTitle'], video['publishedAt'].date(), video['duration'], video['title']
                        ))
                else:
                    print ("%-40s\t %-8s\t %s" % (video['url'], video['duration'], video['title']))
        else:
            print ("No videos found based on the search query: %s" % (searchQuery))
        sys.exit()

    ############################################################
    # Search Live Streams By string
    # 
    if (args.searchstreams):
        nextPageToken = None
        searchQuery = args.searchstreams

        if (startPage > 0):
            for i in range(startPage-1):
                result = ytApi.searchLiveStreams(searchQuery, True, nextPageToken)
                try:
                    nextPageToken = result['nextPageToken']
                except (KeyError):
                    pass

        result = ytApi.searchLiveStreams(searchQuery, None, nextPageToken)
        if result['items']:
            print ("%-40s\t %-8s\t %s" % ('URL', 'Viewers', 'Title'))
            print ("%s" % ('-'*120))
            
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
                try:
                    videosDict[videoId]['viewCount'] = stats['statistics']['viewCount']
                except (KeyError):
                    videosDict[videoId]['viewCount'] = "n/a"

            for key, video in videosDict.items():
                try:
                    videoViewCount = video['viewCount'] 
                except KeyError:
                    videoViewCount = 'N/A'
                print ("%-40s\t %-8s\t %s" % (video['url'], videoViewCount, video['title']))
        else:
            print ("No live streams found based on the search query: %s" % (searchQuery))
        sys.exit()

    ############################################################
    # Search channels By string
    # 
    if (args.searchchannel):
        searchQuery = args.searchchannel
        result = ytApi.searchChannel(searchQuery)
        
        if result['items']:
            print ("%-32s\t%s" % ('Channel', 'RSS url'))
            print ("%s" % ('-'*100))

            for item in result['items']:
                channelId = item['id']['channelId']
                rssUrl = ''.join(["https://www.youtube.com/feeds/videos.xml?channel_id=", channelId])
                print ("%-32s\t%s" % (cmnHandler.uniStrip(item['snippet']['channelTitle']), rssUrl))

        else:
            print ("No channels found based on the search query: %s" % (searchQuery))
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
                print ("Title: %s" % (cmnHandler.uniStrip(response['title'])))

            videoFormats = response['formats']
            if args.extrainfo and (args.silence != True):
                helpers.printVideoFormats(videoFormats)

            uri = helpers.getPrefferedVideoURL(videoFormats, isLive)

            if (uri):
                if cfg.verbose and (args.silence != True):
                    print ("\n%s" % (uri))
                if cfg.autoplay:
                    if (isLive):
                        cmnHandler.videoAutoplay(uri, 'list')
                    else:
                        cmnHandler.videoAutoplay(uri, 'video')
            else:
                print ("Not valid video url found!")
        else:
            print ("There is info available about this video!")

        sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])

