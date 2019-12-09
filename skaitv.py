#!python
# coding=utf-8
import cfg, cmn
import urllib, urllib2, sys, argparse, re, string
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random

cmnHandler = cmn.cmnHandler()

_url_re = re.compile(r"""
    http(s)?://(\w+.)?skaitv\.gr/
    (?:
        episode/(?P<categ>[^/?]+)
        /
        (?P<caption2>[^/?]+)
        /
        (?P<caption>[^/?]+)|
        (?P<live>[^/?]+)
    )
    (?:
        /
        (?P<clip>[^/?]+)
    )?
""", re.VERBOSE)

class skaiAPIHandler:
    def __init__(self):
        self.baseurl = 'http://www.skaitv.gr'

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

    def getVideoInfo(self, parsedUrl):
        endpoint = "episode.php"
        query = {
            "caption": "no",
            "show_caption": parsedUrl['caption'],
            "epanalipsi": "",
            "cat_caption2": parsedUrl['caption2']
        }
        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def getLiveInfo(self, parsedUrl):
        endpoint = "live"
        responseHtml = self.call(endpoint)
        if responseHtml:
            return self.getJsonData(responseHtml)
        return None
    
    def getJsonData(self, html):
        start = html.find('var data = ')
        end = html.find('initPlayer', start)
        end = end-46

        return json.loads(html[start+11:end])


class helpersHandler:
    def parseURL(self, url):
        try:
            return _url_re.match(url).groupdict()
        except AttributeError:
            print "The url you provided seems wrong. Please, consult the manual about the supported urls."
            sys.exit()

    def getVideoType(self, url):
        types = self.parseURL(url)

        if types:
            if (types['caption'] and types['caption2']):
                return {'type': 'video', 'caption': types['caption'], 'caption2': types['caption2'], 'clip': types['clip']}

            if (types['live'] == 'live'):
                return {'type': 'live'}

        return None

    def buildM3U8Uri(self, media):
        vsUrl = "http://videostream.skai.gr"
        slash = "/"
        if (media.startswith(('/'))):
            slash = ""

        return "%s%s%s.m3u8" % (vsUrl, slash, media)


def main(argv):
    skaiApi = skaiAPIHandler()
    helpers = helpersHandler()

    if len(argv) == 0:
        print "No arguments given. Use skaitv.py -h for more info.\nThe script must be used from the shell."
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(description=cmnHandler.getScriptDescription('skaitv.gr'), epilog=cmnHandler.getScriptEpilog(),
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    argParser.add_argument('-u', '--url', action='store', dest='url', help='The video url')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    argParser.add_argument('-l', '--live', action='store_true', default=False, dest='live', help='Play the current live stream. If -u argument is set, this is ignored.')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()
    if (args.url):
        skaiURL = args.url
        video = helpers.getVideoType(args.url)
    if (args.live):
        video = {'type': 'live'}

    if (video['type'] == 'video'):
        videoInfo = skaiApi.getVideoInfo(video)
        if videoInfo['episode']:
            uri = None
            for episode in videoInfo['episode']:
                if video['clip'] == None and episode['media_type'] == "1" and episode['media_type_id'] == "2":
                    uri = helpers.buildM3U8Uri(episode['media_item_file'])
                    break
                if video['clip'] == None and episode['media_type'] == "1" and episode['media_type_id'] == "4":
                    uri = 'https://www.youtube.com/watch?v=%s' % (episode['media_item_file'])
                    break
                if video['clip'] != None and episode['mi_caption'] == video['clip']:
                    uri = helpers.buildM3U8Uri(episode['media_item_file'])
                    break
            
            if (uri):
                if (episode['media_type_id'] == "2"):
                    m3u8Response = skaiApi.getURL(uri)
                    if m3u8Response:
                        if cfg.verbose and (args.silence != True):
                            print "%s" % (uri)
                        if cfg.autoplay:
                            cmnHandler.videoAutoplay(uri, 'list')
                    else:
                        print "Not valid video playlist found"

                # This is a YouTube video
                if (episode['media_type_id'] == "4"):
                    if cfg.verbose and (args.silence != True):
                        print "%s" % (uri)
                    if cfg.autoplay:
                        print "Use youtube script to autoplay this video:\nyoutube.py -u %s" % (uri)

            else:
                print "There is no video available!"
        else:
            print "There is no video available!"

        sys.exit()

    if (video['type'] == 'live'):
        videoInfo = skaiApi.getLiveInfo(video)
        if videoInfo:
            if (args.silence != True):
                try:
                    print "Title: %s" % (cmnHandler.uniStrip(videoInfo['now']['title']))
                    print "Description:\n%s" % (cmnHandler.uniStrip(videoInfo['now']['short_descr']))
                except KeyError:
                    print "There is no live stream right now."
                    sys.exit()

                try:
                    print "\nWatch next: %s" % (cmnHandler.uniStrip(videoInfo['next'][0]['title']))
                    print "Starting at: %s" % (cmnHandler.uniStrip(videoInfo['next'][0]['start']))
                    print "Description:\n%s" % (cmnHandler.uniStrip(videoInfo['next'][0]['short_descr']))
                except KeyError:
                    pass
                
            try:
                livestreamUrl = videoInfo['now']['livestream']
            except KeyError:
                print "There is no live stream right now."
                sys.exit()

            if livestreamUrl:
                if cfg.verbose and (args.silence != True):
                    print "\nLivestream: %s" % (livestreamUrl)
                if cfg.autoplay:
                    print "Use youtube script to autoplay this live stream:\nyoutube.py -u %s" % (livestreamUrl)

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])