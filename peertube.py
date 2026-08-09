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


class peerseekAPIHandler:
    def __init__(self):
        self.baseurl = 'https://peerseek.video/v1'
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

    def searchVideos(self, title, limit = 50):
        endpoint = "search"
        query = {
            "q": title,
            "limit": limit
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

        if (types['video_uuid']):
            return {'type': 'video', 'uuid': types['video_uuid']}

        return None

    def getPrefferedVideoURL(self, data):
        print ("Available video qualities:")
        print ("--------------------------")
        for idx in data:
            print ("- %s" % (idx['resolution']['label']))
        print ("--------------------------")
        
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
    peerseekApi = peerseekAPIHandler()
    helpers = helpersHandler()

    if len(argv) == 0:
        print ("No arguments given. Use peertube.py -h for more info.\nThe script must be used from the shell.")
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(description=cmnHandler.getScriptDescription('PeerTube'), epilog=cmnHandler.getScriptEpilog(),
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    argParser.add_argument('-u', '--url', action='store', dest='url', help='The video url')
    argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
    argParser.add_argument('-sv', '--search-video', action='store', dest='searchvideo', help='Search videos based on description')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    argParser.add_argument('-x', '--extra-info', action='store_true', default=False, dest='extrainfo', help='Show extra info in search results and video data')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()
    
    video = {'type': ''}  # Initialize video dict
    
    ############################################################
    # Search Videos By string
    # 
    if (args.searchvideo):
        searchQuery = args.searchvideo
        result = peerseekApi.searchVideos(searchQuery)
        
        if result and 'videos' in result and len(result['videos']) > 0:
            if args.extrainfo:
                print ("%-75s\t %-16s\t %-12s\t %-30s\t %s" % ('URL', 'Date', 'Duration', 'Channel', 'Title'))
                print ("%s" % ('-'*220))
            else:
                print ("%-75s\t %-12s\t %s" % ('URL', 'Duration', 'Title'))
                print ("%s" % ('-'*175))
            
            for video in result['videos']:
                try:
                    video_id = video.get('id', '')
                    instance = video.get('instance', 'unknown')
                    title = cmnHandler.uniStrip(video.get('title', 'Unknown'))
                    channel = cmnHandler.uniStrip(video.get('channel', 'Unknown'))
                    published = video.get('publishedAt', '')[:10]  # Get just the date part
                    duration = video.get('durationSeconds', 0)
                    video_url = video.get('videoUrl', "https://%s/w/%s" % (instance, video_id))
                    
                    # Format duration
                    if duration:
                        mins, secs = divmod(int(duration), 60)
                        hours, mins = divmod(mins, 60)
                        if hours > 0:
                            duration_str = "%d:%02d:%02d" % (hours, mins, secs)
                        else:
                            duration_str = "%d:%02d" % (mins, secs)
                    else:
                        duration_str = "N/A"
                    
                    if args.extrainfo:
                        output = "%-75s\t %-16s\t %-12s\t %-30s\t %s" % (
                            video_url,
                            published,
                            duration_str,
                            channel[:30],
                            title[:80]
                        )
                    else:
                        output = "%-75s\t %-12s\t %s" % (
                            video_url,
                            duration_str,
                            title[:100]
                        )
                    
                    print (output)
                except Exception, e:
                    continue
        else:
            print ("No videos found based on the search query: %s" % (searchQuery))
        sys.exit()

    if (args.url):
        video = helpers.getVideoType(args.url)
    if (args.quality):
        vqw.peertubeVQW.insert(0, args.quality)

    if (video['type'] == 'video'):
        peertubeApi.baseurl = helpers.getInstanceUrl(args.url)
        videoUuid = video['uuid']
        streams = peertubeApi.getVideoInfoByID(videoUuid)
        print ("Video title: %s" % (streams['name']))
        if (streams):
            streamFiles = streams['streamingPlaylists'][0]['files'] + streams['files']

            if streamFiles:
                uri = helpers.getPrefferedVideoURL(streamFiles)
                if (uri):
                    if uri:
                        if cfg.verbose and (args.silence != True):
                            print ("%s" % (uri))
                        if cfg.autoplay:
                            cmnHandler.videoAutoplay(uri, 'video')
                    else:
                        print ("No valid video found")
                else:
                    print ("No valid video found")
            else:
                print ("There is no video files available!")

        else:
            print ("There is no info for this URL. Please check if this right.")

        sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])