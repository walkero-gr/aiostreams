#!python
# coding=utf-8
import cfg, cmn, vqw
import sys, argparse, re
import simplem3u8 as sm3u8
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
    http(s)?://(\w+.)?dailymotion\.com/
    (?:
        video/(?P<video_id>[^/?]+)
    )?
""", re.VERBOSE)

class dailymotionAPIHandler:
    def __init__(self):
        self.baseurl = 'https://www.dailymotion.com'

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

    def getVideoInfoByID(self, videoId):
        endpoint = "player/metadata/video/%s" % (videoId)
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

        return None

    def getPrefferedVideoURL(self, data):
        sm3u8Parser = sm3u8.parseHandler()
        playlists = sm3u8Parser.parse(data)
        
        for quality in vqw.dailymotionVQW:
            for idx in playlists:
                if (playlists[idx]):
                    streamQuality = playlists[idx]['name']
                    if (streamQuality.find(quality) >= 0):
                        return playlists[idx]['uri']
        
        return None
        
    def clearUri(self, uri):
        uriSplit = uri.split('#')
        return uriSplit[0]

def main(argv):
    dailymotionApi = dailymotionAPIHandler()
    helpers = helpersHandler()

    if len(argv) == 0:
        print ("No arguments given. Use dailymotion.py -h for more info.\nThe script must be used from the shell.")
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(description=cmnHandler.getScriptDescription('dailymotion.com'), epilog=cmnHandler.getScriptEpilog(),
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    argParser.add_argument('-u', '--url', action='store', dest='url', help='The video url')
    argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()
    if (args.url):
        video = helpers.getVideoType(args.url)
    if (args.quality):
        vqw.dailymotionVQW.insert(0, args.quality)

    if (video['type'] == 'video'):
        videoId = video['id']
        streams = dailymotionApi.getVideoInfoByID(videoId)
        qualities = streams['qualities']

        if (qualities):
            for idx in qualities:
                if (idx == 'auto'):
                    m3u8Response = dailymotionApi.getURL(qualities[idx][0]['url'])
                    if (m3u8Response):
                        break

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