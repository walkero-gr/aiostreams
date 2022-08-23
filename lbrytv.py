#!python
# coding=utf-8
import cfg, cmn, vqw
import urllib, urllib2, sys, argparse, re, string, time
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random
from datetime import datetime

cmnHandler = cmn.cmnHandler()
_url_re = re.compile(r"""
    http(s)?://(lbry|odysee)\.(tv|com)/
    (?:
        @(?P<channel>[^/?]+)
    )
    (?:
        /(?P<video_id>[^/?]+)
    )?
""", re.VERBOSE)

class lbrytvAPIHandler:
    def __init__(self):
        self.baseurl = 'https://api.lbry.tv/api/v1'
        self.searchurl = 'https://lighthouse.lbry.com'

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

    def searchCall(self, endpoint, query = None):
        url = "%s/%s" % (self.searchurl, endpoint)
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

    def getChannelInfoByName(self, uri):
        endpoint = "proxy"
        query = {
            "jsonrpc": "2.0",
            "method": "resolve",
            "params": {
                "urls": 
                    uri
                ,
                "include_purchase_receipt": "true",
                "include_is_my_output": "true"
            },
            "id": int(time.time())
        }
        
        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def getVideosByClaimId(self, id):
        endpoint = "proxy"
        query = {
            "jsonrpc": "2.0",
            "method": "claim_search",
            "params": {
                "page_size": 20,
                "page": 1,
                "no_totals": "true",
                "channel_ids": [
                    id
                ],
                "not_channel_ids": [],
                "not_tags": [
                    "porn", "porno", "nsfw", "mature", "xxx", "sex", "creampie",
                    "blowjob", "handjob", "vagina", "boobs", "big boobgs",
                    "big dick", "pussy", "cumshot", "anal", "hard fucking",
                    "ass", "fuck", "hentai"
                ],
                "order_by": [
                    "release_time"
                ],
                "release_time": "<%d" % (int(time.time())),
                "fee_amount": ">=0",
                "include_purchase_receipt": "true"
            },
            "id": int(time.time())
        }
        
        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def search(self, query, claimType):
        params = {
            "s": query,
            "size": 30,
            "from": 0,
            "claimType": claimType,
            "nsfw": "false"
        }
        endpoint = "search?%s" % (urllib.urlencode(params))

        responseData = self.searchCall(endpoint)
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

        if (types['channel']):
            return {'type': 'channel', 'channel': types['channel']}

        return None

    def buildUri(self, video, type = "video"):
        try:
            channel = video['channel'].replace(":", "#")
        except KeyError:
            pass

        try:
            videoId = video['id'].replace(":", "#")
        except KeyError:
            pass

        if (type == 'channel'):
            return 'lbry://@%s' % (channel)
        
        return 'lbry://@%s/%s' % (channel, videoId)
    
    def buildHttpUrl(self, uri):
        uri = uri.replace("lbry://", "https://lbry.tv/")
        return uri.replace("#", ":")

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
    argParser.add_argument('-cv', '--channel-videos', action='store_true', default=False, dest='channelvideos', help='Request the recorded videos of a channel. The -u argument is mandatory.')
    argParser.add_argument('-sv', '--search-video', action='store', dest='searchvideo', help='Search recorded videos based on description')
    argParser.add_argument('-sc', '--search-channel', action='store', dest='searchchannel', help='Search channels based on description')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()
    if (args.url):
        video = helpers.getVideoType(args.url)

    ############################################################
    # Search Videos By string
    # 
    if (args.searchvideo):
        searchQuery = args.searchvideo
        result = lbrytvApi.search(searchQuery, 'file')
        if result:
            print "%-100s\t %s" % ('Title', 'Channel')
            print "%s" % ('#'*180)
            videoIds = []
            for item in result:
                videoId = ''.join(['lbry://', item['name'], '#', item['claimId']])
                videoIds.append(videoId)

            videosData = lbrytvApi.getChannelInfoByName(videoIds)
            if videosData:
                for key in videosData['result']:
                    item = videosData['result'][key]
                    try:
                        print "%-100s\t %s\n%-100s\t %s\n%s" % (\
                            cmnHandler.uniStrip(item['value']['title']),\
                            cmnHandler.uniStrip(item['signing_channel']['name']),\
                            helpers.buildHttpUrl(item['canonical_url']),\
                            helpers.buildHttpUrl(item['signing_channel']['canonical_url']),
                            datetime.fromtimestamp(int(item['value']['release_time']))
                        )
                        print "%s" % ('-'*180)
                    except KeyError:
                        pass
            else:
                print "No videos found!"
        sys.exit()

    ############################################################
    # Search Channels By string
    # 
    if (args.searchchannel):
        searchQuery = args.searchchannel
        result = lbrytvApi.search(searchQuery, 'channel')
        if result:
            print "%-60s\t %-30s\t %s" % ('Title', 'Channel', 'URL')
            print "%s" % ('#'*180)
            videoIds = []
            for item in result:
                videoId = ''.join(['lbry://', item['name'], '#', item['claimId']])
                videoIds.append(videoId)

            channelsData = lbrytvApi.getChannelInfoByName(videoIds)
            if channelsData:
                for key in channelsData['result']:
                    item = channelsData['result'][key]
                    try: 
                        print "%-60s\t %-30s\t %s" % (\
                            cmnHandler.uniStrip(item['value']['title']),\
                            cmnHandler.uniStrip(item['name']),\
                            helpers.buildHttpUrl(item['canonical_url'])
                        )
                    except KeyError:
                        pass
            else:
                print "No channels found!"
        sys.exit()

    if (args.channelvideos):
        uri = helpers.buildUri(video, 'channel')
        channelInfo = lbrytvApi.getChannelInfoByName(uri)

        try:
            claimId = channelInfo['result'][uri]['claim_id']
            videoList = lbrytvApi.getVideosByClaimId(claimId)
            print "%-90s\t %-20s\t %s" % ('URL', 'Recorded at', 'Title')
            print "%s" % ('-'*200)
            for item in videoList['result']['items']:
                print "%-90s\t %-20s\t %s" % (helpers.buildHttpUrl(item['canonical_url']), datetime.fromtimestamp(int(item['value']['release_time'])), cmnHandler.uniStrip(item['value']['title']))
        except KeyError:
            try: 
                print channelInfo['result'][uri]['error']['text']
            except KeyError:
                print "There was an error with the channel! Please, check that it is right."
        sys.exit()

    if (video['type'] == 'video'):
        uri = helpers.buildUri(video, 'video')
        streams = lbrytvApi.getVideoInfoByUri(uri)

        video = streams['result']['streaming_url']
        if (video):
            if cfg.autoplay:
                cmnHandler.videoAutoplay(video, 'list')
        else:
            print "There is no video available!"

        sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])