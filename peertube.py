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
    http(s)?://(www.)?
    (?:
        (?P<instance>[^/?]+)/
    )
    (?:
        w/(?P<video_uuid>[^/?]+)
    )?
""", re.VERBOSE)

class peertubeAPIHandler:
    def __init__(self):
        self.baseurl = None

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

    def getVideoInfoByID(self, videoUuid):
        endpoint = "videos/%s" % (videoUuid)
        responseData = self.call(endpoint)
        if responseData:
            return json.loads(responseData)
        return None


class helpersHandler:
    def parseURL(self, url):
        return _url_re.match(url).groupdict()

    def getVideoType(self, url):
        types = self.parseURL(url)

        if (types['video_uuid']):
            return {'type': 'video', 'uuid': types['video_uuid']}

        return None

    def getPrefferedVideoURL(self, data):
        for quality in vqw.peertubeVQW:
            for idx in data:
                if (quality == idx['resolution']['label']):
                    return idx['fileUrl']
        
        return None

    def getInstanceUrl(self, url):
        types = self.parseURL(url)
        if (types['instance']):
            return "https://%s/api/v1" % (types['instance'])

        return None


def main(argv):
    peertubeApi = peertubeAPIHandler()
    helpers = helpersHandler()

    if len(argv) == 0:
        print ("No arguments given. Use peertube.py -h for more info.\nThe script must be used from the shell.")
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(description=cmnHandler.getScriptDescription('PeerTube'), epilog=cmnHandler.getScriptEpilog(),
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
        vqw.peertubeVQW.insert(0, args.quality)

    if (video['type'] == 'video'):
        peertubeApi.baseurl = helpers.getInstanceUrl(args.url)
        videoUuid = video['uuid']
        streams = peertubeApi.getVideoInfoByID(videoUuid)

        if (streams):
            streamFiles = streams['files']
            if len(streamFiles) == 0:
                streamFiles = streams['streamingPlaylists'][0]['files']

            if streamFiles:
                uri = helpers.getPrefferedVideoURL(streamFiles)

                if (uri):
                    if uri:
                        if cfg.verbose and (args.silence != True):
                            print ("%s" % (uri))
                        if cfg.autoplay:
                            cmnHandler.videoAutoplay(uri, 'video')
                    else:
                        print ("Not valid video found")
            else:
                print ("There is no video files available!")

        else:
            print ("There is no info for this URL. Please check if this right.")

        sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])