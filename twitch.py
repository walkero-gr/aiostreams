#!python
# coding=utf-8
import cfg, cmn, vqw
import sys, argparse, re
import simplejson as json

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

_url_re = re.compile(r"""
    http(s)?://
    (?:
        (?P<subdomain>[\w\-]+)
        \.
    )?
    twitch.tv/
    (?:
        videos/(?P<videos_id>\d+)|
        (?P<channel>[^/]+)
    )
    (?:
        /
        (?P<video_type>[bcv])(?:ideo)?
        /
        (?P<video_id>\d+)
    )?
    (?:
        /(?:clip/)?
        (?P<clip_name>[\w]+)
    )?
""", re.VERBOSE)

class aiostreamsapiHandler:
    def __init__(self):
        self.baseurl = 'https://aiostreams.amiga-projects.net/v1/twitch'
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

    def getStreams(self, categoryId):
        endpoint = "getstreams/live"
        try:
            if int(categoryId) > 0:
                query = {
                    'gameid': categoryId
                }
            else:
                query = {}
        except (TypeError, ValueError):
            print ("The game ID should be a number and not a string. Please use -sg with the game title to get the ID")
            sys.exit()

        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def getTopGames(self):
        endpoint = "getcategories"
        query = {}
        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def searchByGameTitle(self, title):
        endpoint = "search/games"
        query = {
            'query': title
        }

        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def searchChannels(self, name):
        endpoint = "search/channels"
        query = {
            'query': name
        }

        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def getVideoInfo(self, vid, vtype):
        endpoint = "video/getinfo"
        query = {
            'id': vid,
            'type': vtype
        }

        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def getVideosByChannelId(self, chid):
        endpoint = "channel/videos"
        query = {
            'id': chid
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

        if (types['channel']):
            return {'type': 'live', 'id': types['channel']}

        if (types['videos_id']):
            return {'type': 'video', 'id': types['videos_id']}

        return None

    def getPrefferedVideoURL(self, data, isLive = False):
        for quality in vqw.twitchVQW:
            for idx in data:
                if (quality == idx['format_id']):
                    try: 
                        return idx['url']
                    except KeyError:
                        pass

        return None
    
    def printVideoFormats(self, data):
        print ("\nAvailable formats")
        print ("%-20s\t%-12s\t%-12s" % ('ID', 'VCodec', 'ACodec'))
        print ("%s" % ('-'*52))
        for idx in data:
            print ("%-20s\t%-12s\t%-12s" % (idx['format_id'], idx['vcodec'], idx['acodec']))
        sys.exit()
    
    def getChannelInfoByName(self, data, name):
        for item in data:
            if item['broadcaster_login'] == name:
                return item

        return None

def main(argv):
    global aiostreamsapi
    aioapi = aiostreamsapiHandler()
    h = helpersHandler()

    video = {'type': ''}

    if len(argv) == 0:
        print ("No arguments given. Use twitch.py -h for more info.\nThe script must be used from the shell.")
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(
        description=cmnHandler.getScriptDescription('twitch.tv'), 
        epilog=cmnHandler.getScriptEpilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    argParser.add_argument('-u', '--url', action='store', dest='url', help='The video/channel url. If this is found it will start playing in your video player')
    argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
    argParser.add_argument('-ts', '--top-streams', action='store_true', default=False, dest='topstreams', help='Get a list of the current Top Live Streams, based on the number of viewers')
    argParser.add_argument('-tg', '--top-games', action='store_true', default=False, dest='topgames', help='Get a list of the current Top Games with live streams available, based on the number of viewers')
    argParser.add_argument('-sg', '--search-game', action='store', dest='searchgame', help='Get game information based on its name')
    argParser.add_argument('-gv', '--game-videos', action='store', dest='gamevideos', help='Search for available streams based on game ID')
    argParser.add_argument('-cv', '--channel-videos', action='store_true', default=False, dest='channelvideos', help='Request the recorded videos of a channel. The -u argument is mandatory.')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    argParser.add_argument('-x', '--extra-info', action='store_true', default=False, dest='extrainfo', help='Show extra info in search results and video data')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()
    if (args.url):
        video = h.getVideoType(args.url)
    if (args.quality):
        vqw.twitchVQW.insert(0, args.quality)

    if (args.topstreams):
        streamList = aioapi.getStreams(0)
        print ("%-36s\t %-10s\t %-6s\t %-50s\t %s" % ('URL', 'Viewers', "Lang", 'Game', 'Title'))
        print ("%s" % ('-'*200))
        for stream in streamList['data']:
            print ("%-36s\t %-10d\t %-6s\t %-50s\t %s" % (
                'https://twitch.tv/' + stream['user_login'], 
                stream['viewer_count'], 
                stream['language'], 
                stream['game_name'], 
                cmnHandler.uniStrip(stream['title'])
            ))

        sys.exit()

    if (args.topgames):
        gamesList = aioapi.getTopGames()
        print ("%-12s\t%-50s" % ('ID', 'Game'))
        print ("%s" % ('-'*100))
        for game in gamesList['data']:
            print ("%-12s\t%-50s" % (game['id'], cmnHandler.uniStrip(game['name'])))

        sys.exit()

    if (args.gamevideos):
        streamList = aioapi.getStreams(args.gamevideos)
        print ("%-36s\t %-10s\t %-6s\t %-50s\t %s" % ('URL', 'Viewers', "Lang", 'Game', 'Title'))
        print ("%s" % ('-'*200))
        for stream in streamList['data']:
            print ("%-36s\t %-10d\t %-6s\t %-50s\t %s" % (
                'https://twitch.tv/' + stream['user_login'], 
                stream['viewer_count'], 
                stream['language'], 
                stream['game_name'], 
                cmnHandler.uniStrip(stream['title'])
            ))

        sys.exit()

    if (args.channelvideos):
        channels = aioapi.searchChannels(video['id'])
        channelInfo = h.getChannelInfoByName(channels['data'], video['id'])

        if channelInfo['id']:
            itemsList = aioapi.getVideosByChannelId(channelInfo['id'])
            print ("%-36s\t %-20s\t %-10s\t %s" % ('URL', 'Recorded at', 'Duration', 'Title'))
            print ("%s" % ('-'*200))
            for item in itemsList['data']:
                print ("%-36s\t %-20s\t %-10s\t %s" % (item['url'], item['created_at'], item['duration'], cmnHandler.uniStrip(item['title'])))

        sys.exit()

    if (args.searchgame):
        items = aioapi.searchByGameTitle(args.searchgame)
        print ("%-12s\t%-50s" % ('ID', 'Game'))
        print ("%s" % ('-'*100))
        for item in items['data']:
            print ("%-12s\t%-50s" % (item['id'], cmnHandler.uniStrip(item['name'])))
        
        sys.exit()

    if (video['id']):
        videoInfo = aioapi.getVideoInfo(video['id'], video['type'])
        
        if videoInfo:
            if args.extrainfo and (args.silence != True):
                h.printVideoFormats(videoInfo['formats'])

            uri = h.getPrefferedVideoURL(videoInfo['formats'], video['type'])

            if (uri):
                if cfg.verbose and (args.silence != True):
                    print ("\n%s" % (uri))
                if cfg.autoplay:
                    cmnHandler.videoAutoplay(uri, video['type'])
            else:
                print ("Not valid stream found")
        else:
            print ("There is no Live stream for the channel: %s" % (channelName))

        sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
