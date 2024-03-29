#!python
# coding=utf-8
import cfg, cmn, vqw
import sys, argparse, re
import simplem3u8 as sm3u8
import simplejson as json

if sys.version_info[0] == 2:
    import urllib, cookielib
    import urllib2
    from urllib2 import Request as urlReq, urlopen as urlOpn, URLError
    from urllib2 import HTTPHandler as httpHan, HTTPSHandler as httpsHan, \
        HTTPCookieProcessor as cookieProc, build_opener as buildOpener

if sys.version_info[0] == 3:
    import http.cookiejar as cookielib
    import urllib.parse as urllib
    import urllib3
    from urllib.request import Request as urlReq, urlopen as urlOpn
    from urllib.request import HTTPHandler as httpHan, HTTPSHandler as httpsHan, \
        HTTPCookieProcessor as cookieProc, build_opener as buildOpener
    from urllib.error import URLError

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
        request = urlReq(url)
        try:
            response = urlOpn(request)
            retData = response.read()
            response.close()
            return retData
        except (URLError):
            print (URLError["reason"])
        
        return None

    def getApiURL(self, url):
        # Request the anon token and get the cookies
        authUrl = "%s/auth/anon-token" % (self.baseurl)
        cookies = cookielib.CookieJar()
        handlers = [
            httpHan(),
            httpsHan(),
            cookieProc(cookies)
        ]
        opener = buildOpener(*handlers)
        authRequest = urlReq(authUrl)
        opener.open(authRequest)

        # Request the endpoint
        request = urlReq(url)
        request.add_header('User-Agent', cmnHandler.spoofAs('CHROME'))
        try:
            response = opener.open(request)
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

    def getTopGames(self, page = 0, limit = 50):
        endpoint = "games"
        query = {
            "limit": limit,
            "offset": page
        }
        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def searchByGameTitle(self, title, page = 0, limit = 50):
        endpoint = "search/games"
        query = {
            "search_phrase": title,
            "limit": limit,
            "offset": page
        }
        
        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def getTopStreamsByGameID(self, id, page = 0, limit = 50):
        endpoint = "media-containers"
        query = {
            "media_container_status": "RUNNING",
            "game_id": id,
            "media_container_type": "SINGLE,COOP",
            "order_direction": "DESC",
            "order_type": "VIEWERS",
            "limit": limit,
            "offset": page
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
        if (uri.find('#') >= 0):
            uriSplit = uri.split('#')
            return uriSplit[0]
        return uri

def main(argv):
    wasdApi = wasdAPIHandler()
    helpers = helpersHandler()

    if len(argv) == 0:
        print ("No arguments given. Use wasd.py -h for more info.\nThe script must be used from the shell.")
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(description=cmnHandler.getScriptDescription('wasd.tv'), epilog=cmnHandler.getScriptEpilog(),
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    argParser.add_argument('-u', '--url', action='store', dest='url', help='The video/channel url')
    argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
    argParser.add_argument('-tg', '--top-games', action='store_true', default=False, dest='topgames', help='Get a list of the current Top Games with live streams available, based on the number of viewers')
    argParser.add_argument('-sg', '--search-game', action='store', dest='searchgame', help='Search for available streams based on game title/id')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()
    if (args.url):
        videoType = helpers.getVideoType(args.url)
    if (args.quality):
        vqw.wasdVQW.insert(0, args.quality)

    if (args.topgames):
        gamesList = wasdApi.getTopGames()
        print ("%-10s\t %-50s\t %-10s\t %-10s" % ('Game ID', 'Game', 'Viewers', 'Streams'))
        print ("%s" % ('-'*200))
        for game in gamesList['result']:
            print ("%-10s\t %-50s\t %-10d\t %-10d" % (game['game_id'], cmnHandler.uniStrip(game['game_name']), game['viewers_count'], game['stream_count']))
        sys.exit()

    if (args.searchgame):
        gameTitle = args.searchgame
        gameId = 0
        try: 
            if int(gameTitle) >= 1:
                gameId = gameTitle
        except ValueError:
            gameData = wasdApi.searchByGameTitle(gameTitle)
            if gameData['result']['count'] > 1:
                gamesList = gameData['result']['rows']
                print ("Found more than one game with the title %s. Select the one you want by the Game ID")
                print ("%-10s\t %-50s\t %-10s\t %-10s" % ('Game ID', 'Game', 'Viewers', 'Streams'))
                print ("%s" % ('-'*200))
                for game in gamesList:
                    print ("%-10s\t %-50s\t %-10d\t %-10d" % (game['game_id'], cmnHandler.uniStrip(game['game_name']), game['viewers_count'], game['stream_count']))
            else:
                gameId = gameData['result']['rows'][0]['game_id']

        if gameId > 0:
            gameStreams = wasdApi.getTopStreamsByGameID(gameId)
            if gameStreams:
                print ("%-36s\t %-10s\t %s" % ('URL', 'Viewers', 'Title'))
                print ("%s" % ('-'*200))
                for stream in gameStreams['result']:
                    streamUrl = "https://wasd.tv/channel/%s" % (stream['channel_id'])
                    print ("%-36s\t %-10d\t %s" % (streamUrl, stream['media_container_streams'][0]['stream_current_viewers'], cmnHandler.uniStrip(stream['media_container_name'])))
            else:
                print ("No streams found for the game: %s" % (gameTitle))
        sys.exit()

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
                        print ("%s" % (uri))
                    if cfg.autoplay:
                        cmnHandler.videoAutoplay(uri, 'list')
                else:
                    print ("Not valid video found")
        else:
            print ("There is no video available!")

        sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])