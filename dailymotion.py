#!python
import urllib, urllib2, sys, argparse, re, string
import simplem3u8 as sm3u8
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random
import cfg

ver = "1.0"
userOS = sys.platform

try:
	import amiga
	userOS = "os4"
except:
	pass

_url_re = re.compile(r"""
	http(s)?://(\w+.)?dailymotion\.com/
    (?:
		video/(?P<video_id>[^/?]+)
	)?
""", re.VERBOSE)

class dailymotionAPIHandler:
	def __init__(self):
		self.baseurl = 'https://www.dailymotion.com'

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

	def getVideoInfoByID(self, videoId):
		endpoint = "player/metadata/video/%s" % (videoId)
		responseData = self.call(endpoint)
		if responseData:
			return json.loads(responseData)
		return None


class helpersHandler:
	def introText(self):
		print "dailymotion.py v%s - Created by George Sokianos\n" % (ver)
	
	def parseURL(self, url):
		return _url_re.match(url).groupdict()

	def getVideoType(self, url):
		types = self.parseURL(url)
        
		if (types['video_id']):
			return {'type': 'video', 'id': types['video_id']}

		if (types['videos_id']):
			return {'type': 'video', 'id': types['videos_id'], 'channel': types['channel']}

		return None

	def getPrefferedVideoURL(self, data):
		sm3u8Parser = sm3u8.parseHandler()
		playlists = sm3u8Parser.parse(data)
		
		for quality in cfg.dailymotionQualityWeight:
			for idx in playlists:
				if (playlists[idx]):
					streamQuality = playlists[idx]['name']
					if (streamQuality.find(quality) >= 0):
						return playlists[idx]['uri']
		
		return None
		
	def uniStrip(self, text):
		return re.sub(r'[^\x00-\x7f]',r'', text)

def main(argv):
	dailymotionApi = dailymotionAPIHandler()
	helpers = helpersHandler()
	global videoQualities

	helpers.introText()
	if len(argv) == 0:
		print "No arguments given. Use dailymotion.py -h for more info.\nThe script must be used from the shell."
		sys.exit()
		
	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that uses dailymotion.com to get information about videos for AmigaOS 4.1 and above.')
	argParser.add_argument('-u', '--url', action='store', dest='url', help='The video url from dailymotion.com')
	argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
	args = argParser.parse_args()

	if (args.url):
		dailymotionURL = args.url
		video = helpers.getVideoType(args.url)
	if (args.quality):
		cfg.dailymotionQualityWeight.insert(0, args.quality)

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
				if uri:
					if cfg.verbose:
						print "%s" % (uri)
					if cfg.autoplay:
						# print "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs)
						if (userOS == 'os4'):
							amiga.system( "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs) )
				else:
					print "Not valid video found"
		else:
			print "There is no video available!"

		sys.exit()
	
	sys.exit()

if __name__ == "__main__":
	main(sys.argv[1:])