#!python
# coding=utf-8
import cfg, cmn, vqw
import urllib, urllib2, sys, argparse, re, string, time
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random

cmnHandler = cmn.cmnHandler()
_url_re = re.compile(r"""
    http(s)?://lbry\.tv/
    (?:
        @(?P<channel>[^/?]+)/(?P<video_id>[^/?]+)
    )?
""", re.VERBOSE)

class lbrytvAPIHandler:
    def __init__(self):
        self.baseurl = 'https://api.lbry.tv/api/v1'

        return None

    def getURL(self, url, jsonParams = None):
        request = urllib2.Request(url)
        try:
            if (jsonParams):
                request.add_header('Content-Type', 'application/json')
                response = urllib2.urlopen(request, json.dumps(jsonParams))
            else:
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
            return self.getURL(url, query)
        
        return self.getURL(url)

    def getVideoInfoByUri(self, uri):
        endpoint = "proxy"
        query = {
            "jsonrpc": "2.0",
            "method": "get",
            "params": {
                "uri": uri,
                "save_file": "false"
            },
            "id": int(time.time())
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

        if (types['video_id']):
            return {'type': 'video', 'id': types['video_id'], 'channel': types['channel']}

        return None

    def buildUri(self, video):
        channel = video['channel'].replace(":", "#")
        videoId = video['id'].replace(":", "#")
        retUri = 'lbry://@%s/%s' % (channel, videoId)
        
        return retUri

def main(argv):
    lbrytvApi = lbrytvAPIHandler()
    helpers = helpersHandler()

    if len(argv) == 0:
        print "No arguments given. Use lbrytv.py -h for more info.\nThe script must be used from the shell."
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(description=cmnHandler.getScriptDescription('lbry.tv'), epilog=cmnHandler.getScriptEpilog(),
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    argParser.add_argument('-u', '--url', action='store', dest='url', help='The video url')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()
    if (args.url):
        video = helpers.getVideoType(args.url)

    if (video['type'] == 'video'):
        uri = helpers.buildUri(video)
        streams = lbrytvApi.getVideoInfoByUri(uri)

        video = streams['result']['streaming_url']
        if (video):
            if cfg.autoplay:
                cmnHandler.videoAutoplay(video, 'video')
        else:
            print "There is no video available!"

        sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])