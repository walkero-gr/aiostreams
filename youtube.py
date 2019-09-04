#!python
import cfg, cmn
import urllib, urllib2, sys, argparse, re, string, urlparse
import simplem3u8 as sm3u8
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random

userOS = sys.platform

try:
	import amiga
	userOS = "os4"
except:
	pass

_url_re = re.compile(r"""(?x)https?://(?:\w+\.)?youtube\.com
    (?:
        (?:
            /(?:
                watch.+v=
                |
                embed/(?!live_stream)
                |
                v/
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

		return

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
		queryArgs = None
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
	
	def getLiveStreams(self, m3u8Url):
		return self.getURL(m3u8Url)

class helpersHandler:
	def parseURL(self, url):
		return _url_re.match(url).groupdict()

	def getVideoType(self, url):
		types = self.parseURL(url)

		if (types['video_id']):
			return {'type': 'video', 'video_id': types['video_id']}

		return None
		
	def uniStrip(self, text):
		return re.sub(r'[^\x00-\x7f]',r'', text)

	def getPrefferedVideoURL(self, data, isLive = False):
		if isLive:
			sm3u8Parser = sm3u8.parseHandler()
			data = sm3u8Parser.parse(data)
			for quality in cfg.ytLiveQualityWeight:
				for idx in data:
					streamQuality = data[idx]['resolution']
					if (streamQuality.find(str(quality)) >= 0):
						return data[idx]['uri']

		for quality in cfg.ytQualityWeight:
			for idx in data:
				if (quality == idx['itag']):
					return idx['url']

		return None
		
def main(argv):
	cmnHandler = cmn.cmnHandler()
	ytApi = ytAPIHandler()
	helpers = helpersHandler()

	if len(argv) == 0:
		print "No arguments given. Use youtube.py -h for more info.\nThe script must be used from the shell."
		sys.exit()
		
	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that uses youtube.com API to get information about videos.')
	argParser.add_argument('-u', '--url', action='store', dest='url', help='The video url')
	argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
	argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
	args = argParser.parse_args()

	if (args.silence != True):
		cmnHandler.showIntroText()
	if (args.url):
		video = helpers.getVideoType(args.url)
		videoId = video['video_id']
	if (args.quality):
		cfg.ytQualityWeight.insert(0, int(args.quality))

	if (videoId):
		videoInfo = ytApi.getVideoInfo(videoId)
		
		if videoInfo:
			vUrlParsed = urlparse.parse_qs(videoInfo)
			playerResponse = vUrlParsed['player_response']
			response = json.loads(playerResponse[0])
			
			if response['playabilityStatus']['status'] != "OK":
				print response['playabilityStatus']['reason']
				sys.exit()

			if (args.silence != True):
				print "Title: %s" % (response['videoDetails']['title'])
				print "Author: %s" % (response['videoDetails']['author'])
				if (response['videoDetails']['isLiveContent'] == False):
					print "Length: %ssec" % (response['videoDetails']['lengthSeconds'])
					uri = helpers.getPrefferedVideoURL(response['streamingData']['adaptiveFormats'])
				
				if (response['videoDetails']['isLiveContent']):
					print "Live streaming with %s viewers" % (response['videoDetails']['viewCount'])
					m3u8Response = ytApi.getLiveStreams(response['streamingData']['hlsManifestUrl'])
					if m3u8Response:
						uri = helpers.getPrefferedVideoURL(m3u8Response, True)
				
				print "\nDescription:\n%s\n%s" % ('-'*30, response['videoDetails']['shortDescription'])

			if (uri):
				if cfg.verbose and (args.silence != True):
					print "\n%s" % (uri)
				if cfg.autoplay:
					# print "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs)
					if (userOS == 'os4'):
						amiga.system( "Run <>NIL: %s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs) )
			else:
				print "Not valid video url found!"
		else:
			print "There is info available about this video!"

		sys.exit()
	
	sys.exit()

if __name__ == "__main__":
	main(sys.argv[1:])