#!python
import urllib, urllib2, sys, argparse, re, string
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
# http://www.skaitv.gr/episode/enimerosi/oi-eidiseis-tou-ska-stis-2/2019-09-02-14
# http://www.skaitv.gr/episode/enimerosi/ta-nea-tou-ska-stis-2000/2019-09-02-19
# http://www.skaitv.gr/episode/psuchagogia/radio-arbula/2019-05-20-23
# http://www.skaitv.gr/episode/psuchagogia/radio-arbula/2019-05-20-23/radio-arbula-istories-agapis-20052019

_url_re = re.compile(r"""
	http(s)?://(\w+.)?skaitv\.gr/
    (?:
		episode/(?P<categ>[^/?]+)
		/
		(?P<caption2>[^/?]+)
		/
		(?P<caption>[^/?]+)
	)
    (?:
		/
		(?P<clip>[^/?]+)
    )?
""", re.VERBOSE)

class skaiAPIHandler:
	def __init__(self):
		self.baseurl = 'http://www.skaitv.gr/json'

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


class helpersHandler:
	def introText(self):
		print "skai.py v%s - Created by George Sokianos\n" % (ver)
	
	def parseURL(self, url):
		return _url_re.match(url).groupdict()

	def getVideoType(self, url):
		types = self.parseURL(url)

		if (types['caption'] and types['caption2']):
			return {'type': 'video', 'caption': types['caption'], 'caption2': types['caption2'], 'clip': types['clip']}

		# TODO: Support Live streams
		#if (types['videos_id']):
		#	return {'type': 'live', 'id': types['videos_id'], 'channel': types['channel']}

		return None

		
	def uniStrip(self, text):
		return re.sub(r'[^\x00-\x7f]',r'', text)

	def buildM3U8Uri(self, media):
		return "http://videostream.skai.gr/%s.m3u8" % (media)
		

def main(argv):
	skaiApi = skaiAPIHandler()
	helpers = helpersHandler()
	global videoQualities

	if len(argv) == 0:
		print "No arguments given. Use skai.py -h for more info.\nThe script must be used from the shell."
		sys.exit()
		
	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that uses skai.gr to get information about videos for AmigaOS 4.1 and above.')
	argParser.add_argument('-u', '--url', action='store', dest='url', help='The video url from skai.gr')
	argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
	args = argParser.parse_args()

	if (args.silence != True):
		helpers.introText()
	if (args.url):
		skaiURL = args.url
		video = helpers.getVideoType(args.url)

	if (video['type'] == 'video'):
		videoInfo = skaiApi.getVideoInfo(video)

		if videoInfo['episode']:
			uri = None
			for episode in videoInfo['episode']:
				if video['clip'] == None and episode['media_type'] == "1":
					uri = helpers.buildM3U8Uri(episode['media_item_file'])
					break
				if video['clip'] != None and episode['mi_caption'] == video['clip']:
					uri = helpers.buildM3U8Uri(episode['media_item_file'])
					break

			if (uri):
				m3u8Response = skaiApi.getURL(uri)

				if m3u8Response:
					if cfg.verbose and (args.silence != True):
						print "%s" % (uri)
					if cfg.autoplay:
						# print "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs)
						if (userOS == 'os4'):
							amiga.system( "Run <>NIL: %s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs) )
				else:
					print "Not valid video playlist found"
		else:
			print "There is no video available!"

		sys.exit()
	
	sys.exit()

if __name__ == "__main__":
	main(sys.argv[1:])