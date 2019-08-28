#!python
import urllib, urllib2, sys, argparse, re, string
import simplem3u8 as sm3u8
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random
import cfg

ver = "1.0"
clientId = "b1cb746d2751f467188edbb12997d4412b711011f640ce04"
userOS = sys.platform

try:
	import amiga
	userOS = "os4"
except:
	pass	

_url_re = re.compile(r"""
	http(s)?://(\w+.)?mixer\.com/
    (?:
		(?P<channel>[^/?]+)
	)
    (?:
        (?:\?vod=)?
        (?P<video_id>[\w]+)
    )?
""", re.VERBOSE)

class mixerAPIHandler:
	def __init__(self):
		self.baseurl = 'https://mixer.com/api/v1'

		return

	def call(self, endpoint, query = None):
		queryArgs = None
		if (query):
			queryArgs = urllib.urlencode(query)
		url = "%s/%s?%s" % (self.baseurl, endpoint, queryArgs)

		request = urllib2.Request(url)
		request.add_header('Client-ID', clientId)
		try:
			response = urllib2.urlopen(request)
			retData = response.read()
			response.close()
			return retData
		except URLError, e:
			print e
		
		return None

	def getChannelInfoByName(self, channelName):
		endpoint = "channels/%s" % (channelName)
		responseData = self.call(endpoint)
		if responseData:
			return json.loads(responseData)
		return None

	def getStreamsByChannelID(self, channelID):
		endpoint = "channels/%d/manifest.m3u8" % (channelID)
		query = {
			"cdn": "false"
		}
		return self.call(endpoint, query)

	def getTopStreamsByGameID(self, gameID):
		endpoint = "channels"
		query = {
			"order": "viewersCurrent:DESC",
			"where": "typeId:eq:%d,online:eq:true" % (gameID),
			"page": 0
		}
		responseData = self.call(endpoint, query)
		if responseData:
			return json.loads(responseData)
		return None

	def getVideoInfoByID(self, videoId):
		endpoint = "recordings/%s" % (videoId)
		responseData = self.call(endpoint)
		if responseData:
			return json.loads(responseData)
		return None

	def searchByGameTitle(self, title):
		endpoint = "types"
		query = {
			"order": "viewersCurrent:DESC",
			"where": "name:eq:%s" % (title),
			"page": 0
		}
		responseData = self.call(endpoint, query)
		if responseData:
			return json.loads(responseData)
		return None
	
	def getTopStreams(self):
		endpoint = "channels"
		query = {
			"order": "viewersCurrent:DESC",
			"where": "online:eq:true",
			"page": 0
		}
		responseData = self.call(endpoint, query)
		return json.loads(responseData)

	def getTopGames(self):
		endpoint = "types"
		query = {
			"order": "viewersCurrent:DESC",
			"where": "parent:eq:Games",
			"page": 0
		}
		responseData = self.call(endpoint, query)
		return json.loads(responseData)

	def getVideosByChannel(self, channelID):
		endpoint = "channels/%d/recordings" % (channelID)
		query = {
			"order": "createdAt:DESC"
		}
		responseData = self.call(endpoint, query)
		return json.loads(responseData)

class helpersHandler:
	def introText(self):
		print "mixer.py v%s - Created by George Sokianos\n" % (ver)
	
	def parseURL(self, url):
		return _url_re.match(url).groupdict()

	def getVideoType(self, url):
		types = self.parseURL(url)

		if (types['video_id']):
			return {'type': 'video', 'id': types['video_id']}

		if (types['channel']):
			return {'type': 'channel', 'id': types['channel']}

		return None

	def getPrefferedVideoURL(self, data):
		sm3u8Parser = sm3u8.parseHandler()
		playlists = sm3u8Parser.parse(data)
		
		for quality in cfg.mixerQualityWeight:
			for idx in playlists:
				if (playlists[idx]):
					if (playlists[idx]['name'].find(quality) >= 0):
						return playlists[idx]['uri']
		
		return None
		
	def uniStrip(self, text):
		return re.sub(r'[^\x00-\x7f]',r'', text)

def main(argv):
	mixerApi = mixerAPIHandler()
	helpers = helpersHandler()
	playlists = dict()
	
	helpers.introText()
	if len(argv) == 0:
		print "No arguments given. Use mixer.py -h for more info.\nThe script must be used from the shell."
		sys.exit()
		
	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that uses mixer.com API to get information about channels/videos for AmigaOS 4.1 and above.')
	argParser.add_argument('-u', '--url', action='store', dest='url', help='The video/channel url from mixer.com')
	argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
	argParser.add_argument('-ts', '--top-streams', action='store_true', default=False, dest='topstreams', help='Get a list of the current Top Streams that are live')
	argParser.add_argument('-tg', '--top-games', action='store_true', default=False, dest='topgames', help='Get a list of the current Top Games that are live, based on their viewers')
	argParser.add_argument('-sg', '--search-game', action='store', dest='searchgame', help='Search for available streams based on game title')
	argParser.add_argument('-cv', '--channel-videos', action='store_true', default=False, dest='channelvideos', help='Request the recorded videos of a channel. The -u argument is mandatory.')
	args = argParser.parse_args()
	
	if (args.url):
		mixerURL = args.url
		video = helpers.getVideoType(args.url)

	if (args.quality):
		cfg.mixerQualityWeight.insert(0, args.quality)

	if (args.topstreams):
		streamList = mixerApi.getTopStreams()
		print "%-36s\t %-20s\t %-50s\t %s" % ('URL', 'Type', 'Game', 'Title')
		print "%s" % ('-'*200)
		for stream in streamList:
			streamType = stream['type']
			streamUrl = ''.join(["https://mixer.com/", stream['token']])
			print "%-36s\t %-20s\t %-50s\t %s" % (streamUrl, streamType['parent'], streamType['name'], helpers.uniStrip(stream['name']))

		sys.exit()

	if (args.topgames):
		gamesList = mixerApi.getTopGames()
		print "%-50s\t %-10s\t %-10s" % ('Game', 'Viewers', 'Streams')
		print "%s" % ('-'*200)
		for game in gamesList:
			print "%-50s\t %-10d\t %-10d" % (helpers.uniStrip(game['name']), game['viewersCurrent'], game['online'])

		sys.exit()

	if (args.channelvideos):
		channelName = video['id']
		channelInfo = mixerApi.getChannelInfoByName(channelName)
		recordingsList = mixerApi.getVideosByChannel(channelInfo['id'])
		print "%-50s\t %-30s\t %s" % ('URL', 'Recorded at', 'Title')
		print "%s" % ('-'*200)
		for recording in recordingsList:
			streamUrl = "https://mixer.com/%s?vod=%d" % (channelName, recording['id'])
			print "%-50s\t %-30s\t %s" % (streamUrl, recording['createdAt'], helpers.uniStrip(recording['name']))

		sys.exit()

	if (args.searchgame):
		gameTitle = args.searchgame
		gameData = mixerApi.searchByGameTitle(gameTitle)
		if gameData:
			print helpers.uniStrip(gameData[0]['name'])
			print helpers.uniStrip(gameData[0]['description'])
			print "Current Viewers: %d" % (gameData[0]['viewersCurrent'])
			print "Available Streams: %d\n" % (gameData[0]['online'])

			gameStreams = mixerApi.getTopStreamsByGameID(gameData[0]['id'])
			print "%-36s\t %-10s\t %-20s\t %-50s\t %s" % ('URL', 'Viewers', 'Type', 'Game', 'Title')
			print "%s" % ('-'*200)
			for stream in gameStreams:
				streamType = stream['type']
				streamUrl = ''.join(["https://mixer.com/", stream['token']])
				print "%-36s\t %-10d\t %-20s\t %-50s\t %s" % (streamUrl, stream['viewersCurrent'], streamType['parent'], streamType['name'], helpers.uniStrip(stream['name']))
		else:
			print "No information for the game: %s" % (gameTitle)
		sys.exit()

	if (video['type'] == 'channel'):
		channelName = video['id']
		channelInfo = mixerApi.getChannelInfoByName(channelName)

		if (channelInfo):
			channelID = channelInfo['id']
			channelType = channelInfo['type']
			print "Name: %s" % (helpers.uniStrip(channelInfo['name']))
			print "Type: %s/%s" % (channelType['parent'], channelType['name'])
			print "Total Viewers: %d" % (channelInfo['viewersTotal'])
			print "Current Viewers: %d" % (channelInfo['viewersCurrent'])

			m3u8Response = mixerApi.getStreamsByChannelID(channelID)
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
					print "Not valid stream found"
			else:
				print "There was an error with the usherApi"
		else:
			print "There is no Live stream for the channel: %s" % (channelName)

		sys.exit()

	if (video['type'] == 'video'):
		videoId = video['id']

		videoInfo = mixerApi.getVideoInfoByID(videoId)
		if (videoInfo):
			for vod in videoInfo['vods']:
				if (vod['format'] == 'hls'):
					uri = "%smanifest.m3u8" % (vod['baseUrl'])
					break

			if uri:		
				if cfg.verbose:
					print "%s" % (uri)
				if cfg.autoplay:
					# print "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs)
					if (userOS == 'os4'):
						amiga.system( "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs) )
			else:
				print "Not valid recording stream found"
		else:
			print "There is no video available with ID: %s" % (videoId)

		sys.exit()

	
	sys.exit()


if __name__ == "__main__":
	main(sys.argv[1:])
