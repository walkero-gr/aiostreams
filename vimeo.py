#!python
# coding=utf-8
import cfg, cmn, vqw
import sys, argparse, re
import simplem3u8 as sm3u8
import simplejson as json

if sys.version_info[0] == 2:
    import urllib
    import urllib2
    from urllib2 import Request as urlReq, urlopen as urlOpn, URLError as urlErr

if sys.version_info[0] == 3:
    import urllib.parse as urllib
    import urllib3
    from urllib.request import Request as urlReq, urlopen as urlOpn
    from urllib.error import URLError as urlErr

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
        request = urlReq(url)
        try:
            response = urlOpn(request)
            retData = response.read()
            response.close()
            return retData
        except (urlErr, e):
            print (e)
        
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

    def getVideoURI(self, data):
        retData = dict()

        for quality in vqw.vimeoVQW:
            for stream in data:
                if quality == stream['quality']:
                    return stream['url']

def main(argv):
    vimeoApi = vimeoAPIHandler()
    helpers = helpersHandler()
    global videoQualities

    if len(argv) == 0:
        print ("No arguments given. Use vimeo.py -h for more info.\nThe script must be used from the shell.")
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(description=cmnHandler.getScriptDescription('vimeo.com'), epilog=cmnHandler.getScriptEpilog(),
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
        vqw.vimeoVQW.insert(0, args.quality)

    if (video['type'] == 'video'):
        videoId = video['id']
        streams = vimeoApi.getVideoInfoByID(videoId)
        videos = streams['request']['files']

        if (len(videos['progressive']) > 0):
            uri = helpers.getVideoURI(videos['progressive'])
            if uri:
                if cfg.verbose and (args.silence != True):
                    print ("%s" % (uri))
                if cfg.autoplay:
                    cmnHandler.videoAutoplay(uri, 'list')
            else:
                print ("Not valid video found")
            
            sys.exit()

        defaultCdn = videos['hls']['default_cdn']
        if (defaultCdn != ""):
            uri = videos['hls']['cdns'][defaultCdn]['url']
            if uri:
                if cfg.verbose and (args.silence != True):
                    print ("%s" % (uri))
                if cfg.autoplay:
                    cmnHandler.videoAutoplay(uri, 'list')
            else:
                print ("Not valid hls found")
            
            sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])