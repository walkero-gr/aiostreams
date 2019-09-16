#!/usr/bin/env python
# coding=utf-8
import cfg, cmn
import urllib, urllib2, sys, argparse, re, string, os
import myurlparse as urlparse
import simplem3u8 as sm3u8
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random
try:
	import amiga
	userOS = "os4"
except:
	pass

cmnHandler = cmn.cmnHandler()
apikey = 'AIzaSyAqIPMWKY6ty9JG66oiL17ZliALtZOJuzg'

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
		self.apiurl = 'https://www.googleapis.com/youtube/v3'

		return

	def getURL(self, url):
		request = urllib2.Request(url)
		request.add_header('User-Agent', cmnHandler.spoofAs('CHROME'))
		try:
			response = urllib2.urlopen(request)
			retData = response.read()
			response.close()
			return retData
		except URLError, e:
			print e
		
		return None

	def call(self, endpoint, query = None, apiCall = False):
		queryArgs = None
		if (query):
			query['key'] = apikey
			queryArgs = urllib.urlencode(query)
		
		requestUrl = self.baseurl
		if apiCall:
			requestUrl = self.apiurl

		url = "%s/%s?%s" % (requestUrl, endpoint, queryArgs)
		return self.getURL(url)

	def getVideoInfo(self, videoId):
		endpoint = "get_video_info"
		query = {
			"video_id": videoId,
			# "sts": 18143,
			# "el": "detailpage"
			# "el": "embedded",
			# "eurl": "https://youtube.googleapis.com/v/%s" % (videoId)
		}
		responseData = self.call(endpoint, query)
		if responseData:
			return responseData
		return None
	
	def getLiveStreams(self, m3u8Url):
		return self.getURL(m3u8Url)

	def searchVideo(self, title, limit = 50):
		endpoint = "search"
		query = {
			"order": "relevance",
			"q": title,
			"part": "snippet",
			"type": "video",
			"videoDefinition": "any",
			"videoEmbeddable": "true",
			"fields": "items(id,snippet(channelTitle,description,liveBroadcastContent,title))",
			"maxResults": limit
		}
		
		responseData = self.call(endpoint, query, True)
		if responseData:
			return json.loads(responseData)
		return None

	def searchLiveStreams(self, title, limit = 50):
		endpoint = "search"
		query = {
			"order": "viewCount",
			"q": title,
			"part": "snippet",
			"type": "video",
			"videoDefinition": "any",
			"videoEmbeddable": "true",
			"eventType": "live",
			"fields": "items(id,snippet(channelTitle,description,liveBroadcastContent,title))",
			"maxResults": limit
		}
		
		responseData = self.call(endpoint, query, True)
		if responseData:
			return json.loads(responseData)
		return None

	def getVideoStatistics(self, videoId):
		endpoint = "videos"
		query = {
			"id": videoId,
			"part": "statistics,contentDetails",
			"fields": "items(id,statistics,contentDetails/duration)"
		}
		
		responseData = self.call(endpoint, query, True)
		if responseData:
			return json.loads(responseData)
		return None

class helpersHandler:
	def parseURL(self, url):
		return _url_re.match(url).groupdict()

	def getVideoType(self, url):
		types = self.parseURL(url)

		if (types['video_id']):
			return {'type': 'video', 'video_id': types['video_id']}

		return None

	def getPrefferedVideoURL(self, data, isLive = False, isCiphered = False):
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
					try: 
						return idx['url']
					except KeyError:
						pass
					if isCiphered:
						try:
							return self.getURLFromCipher(idx['cipher'])
						except KeyError:
							print "Cipher does not exist"

		return None
	
	def getURLFromCipher(self, cipher):
		cipherParsed = urlparse.parse_qs(cipher)
		return cipherParsed['url'][0]

def main(argv):
	ytApi = ytAPIHandler()
	helpers = helpersHandler()

	if len(argv) == 0:
		print "No arguments given. Use youtube.py -h for more info.\nThe script must be used from the shell."
		sys.exit()

	############################################################
	# Parse the arguments
	# 
	argParser = argparse.ArgumentParser(description='This is a python script that uses youtube.com API to get information about videos.')
	argParser.add_argument('-u', '--url', action='store', dest='url', help='The video url')
	argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
	argParser.add_argument('-sv', '--search-video', action='store', dest='searchvideo', help='Search recorded videos based on description')
	argParser.add_argument('-ss', '--search-streams', action='store', dest='searchstreams', help='Search live streams based on description')
	argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
	args = argParser.parse_args()

	if (args.silence != True):
		cmnHandler.showIntroText()
	if (args.url):
		video = helpers.getVideoType(args.url)
		videoId = video['video_id']
	if (args.quality):
		cfg.ytQualityWeight.insert(0, int(args.quality))

	############################################################
	# Search Videos By string
	# 
	if (args.searchvideo):
		searchQuery = args.searchvideo
		result = ytApi.searchVideo(searchQuery)
		
		if result['items']:
			print "%-40s\t %-8s\t %s" % ('URL', 'Views', 'Title')
			print "%s" % ('-'*200)
			videosDict = dict()
			videoIds = []
			for video in result['items']:
				videoId = video['id']['videoId']
				videosDict[videoId] = dict()
				videosDict[videoId]['url'] = ''.join(["https://www.youtube.com/watch?v=", videoId])
				videosDict[videoId]['title'] = cmnHandler.uniStrip(video['snippet']['title'])
				videoIds.append(videoId)
			
			# Get video statistics in one call
			videoStats = ytApi.getVideoStatistics(','.join(videoIds))
			for stats in videoStats['items']:
				videoId = stats['id']
				videosDict[videoId]['viewCount'] = stats['statistics']['viewCount']

			for key, video in videosDict.items():
				print "%-40s\t %-8s\t %s" % (video['url'], video['viewCount'], video['title'])
		else:
			print "No videos found based on the search query: %s" % (searchQuery)
		sys.exit()

	############################################################
	# Search Live Streams By string
	# 
	if (args.searchstreams):
		searchQuery = args.searchstreams
		result = ytApi.searchLiveStreams(searchQuery)
		
		if result['items']:
			print "%-40s\t %-8s\t %s" % ('URL', 'Viewers', 'Title')
			print "%s" % ('-'*200)
			videosDict = dict()
			videoIds = []
			for video in result['items']:
				videoId = video['id']['videoId']
				videosDict[videoId] = dict()
				videosDict[videoId]['url'] = ''.join(["https://www.youtube.com/watch?v=", videoId])
				videosDict[videoId]['title'] = cmnHandler.uniStrip(video['snippet']['title'])
				videoIds.append(videoId)
			
			# Get video statistics in one call
			videoStats = ytApi.getVideoStatistics(','.join(videoIds))
			for stats in videoStats['items']:
				videoId = stats['id']
				videosDict[videoId]['viewCount'] = stats['statistics']['viewCount']

			for key, video in videosDict.items():
				try:
					videoViewCount = video['viewCount'] 
				except KeyError:
					videoViewCount = 'N/A'
				print "%-40s\t %-8s\t %s" % (video['url'], videoViewCount, video['title'])
		else:
			print "No live streams found based on the search query: %s" % (searchQuery)
		sys.exit()

	############################################################
	# Return info for recorded/live video and stream it
	# 
	if (videoId):
		videoInfo = ytApi.getVideoInfo(videoId)
		if videoInfo:
			vUrlParsed = urlparse.parse_qs(videoInfo)
			playerResponse = vUrlParsed['player_response']
			response = json.loads(playerResponse[0])
			
			if response['playabilityStatus']['status'] != "OK":
				print response['playabilityStatus']['reason']
				sys.exit()

			useCipher = False
			isLive = False
			if (response['videoDetails']['isLiveContent']):
				isLive = True
			if (response['videoDetails']['useCipher']):
				useCipher = True
				print "This video is protected. Protected videos are not currently supported!"
				sys.exit()

			if (args.silence != True):
				print "Title: %s" % (cmnHandler.uniStrip(response['videoDetails']['title']))
				print "Author: %s" % (cmnHandler.uniStrip(response['videoDetails']['author']))
				if (isLive == False):
					print "Length: %ssec" % (response['videoDetails']['lengthSeconds'])
					print "%-5s\t %-10s\t %-16s\t %-10s\t %s" % ('TagID', 'Quality', 'Audio Quality', 'Resolution', 'Mime type')
					print "%s" % ('-'*200)
					for format in response['streamingData']['formats']:
						print "%-5s\t %-10s\t %-16s\t %sx%s\t %s" % (format['itag'], format['qualityLabel'], format['audioQuality'], format['width'], format['height'], format['mimeType'])
				
				if (response['videoDetails']['isLiveContent']):
					print "Live streaming with %s viewers" % (response['videoDetails']['viewCount'])
						
				print "\nDescription:\n%s\n%s" % ('-'*30, cmnHandler.uniStrip(response['videoDetails']['shortDescription']))
				
			if (isLive):
				videoFormats = ytApi.getLiveStreams(response['streamingData']['hlsManifestUrl'])
			else:
				videoFormats = response['streamingData']['formats']
			uri = helpers.getPrefferedVideoURL(videoFormats, isLive, useCipher)
					
			if (uri):
				if cfg.verbose and (args.silence != True):
					print "\n%s" % (uri)
				if cfg.autoplay:
					# print '%s "%s" %s' % (cfg.sPlayer, uri, cfg.sPlayerArgs)
					if (cmnHandler.getUserOS() == 'os4'):
						if (isLive):
							amiga.system( "Run <>NIL: %s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs) )
						else:
							amiga.system( "Run <>NIL: %s %s %s" % (cfg.vPlayer, uri, cfg.vPlayerArgs) )
					# else:
					# 	os.system( '%s "%s" %s' % (cfg.sPlayer, uri, cfg.sPlayerArgs) )
			else:
				print "Not valid video url found!"
		else:
			print "There is info available about this video!"

		sys.exit()
	
	sys.exit()

if __name__ == "__main__":
	main(sys.argv[1:])