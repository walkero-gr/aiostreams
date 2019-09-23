#!/usr/bin/env python
# coding=utf-8
import cfg, cmn
import urllib, urllib2, sys, argparse, re, string
import simplem3u8 as sm3u8
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random

cmnHandler = cmn.cmnHandler()
clientId = "k5y7u3ntz5llxu22gstxyfxlwcz10v"

_url_re = re.compile(r"""
    http(s)?://
    (?:
        (?P<subdomain>[\w\-]+)
        \.
    )?
    twitch.tv/
    (?:
        videos/(?P<videos_id>\d+)|
        (?P<channel>[^/]+)
    )
    (?:
        /
        (?P<video_type>[bcv])(?:ideo)?
        /
        (?P<video_id>\d+)
    )?
    (?:
        /(?:clip/)?
        (?P<clip_name>[\w]+)
    )?
""", re.VERBOSE)

class twitchAPIHandler:
	def __init__(self):
		self.baseurl = 'https://api.twitch.tv'

		return

	def call(self, endpoint, query = None):
		queryArgs = None
		if (query):
			queryArgs = urllib.urlencode(query)
		url = "%s/%s?%s" % (self.baseurl, endpoint, queryArgs)
		
		request = urllib2.Request(url)
		request.add_header('Accept', 'application/vnd.twitchtv.v4+json')
		request.add_header('Client-ID', clientId)
		try:
			response = urllib2.urlopen(request)
			retData = json.load(response)
			response.close()
			return retData
		except URLError, e:
			print e
		
		return None

	def getChannelInfoByName(self, channelName):
		endpoint = "kraken/channels/%s.json" % (channelName)
		retData = self.call(endpoint)

		return retData

	def getStreamsByChannel(self, channelName):
		endpoint = "kraken/streams/%s.json" % (channelName)
		return self.call(endpoint)

	def getAccessTokenByChannel(self, channelName):
		endpoint = "api/channels/%s/access_token.json" % (channelName)
		return self.call(endpoint)

	def getVideoInfoByID(self, videoId):
		endpoint = "kraken/videos/%s.json" % (videoId)
		return self.call(endpoint)

	def getAccessTokenByVideo(self, videoId):
		endpoint = "api/vods/%s/access_token.json" % (videoId)
		return self.call(endpoint)

	def searchByGameTitle(self, title, offset = 0, limit = 50):
		endpoint = "kraken/search/streams"
		query = {
			"query": title,
			"limit": limit,
			"offset": offset
		}
		return self.call(endpoint, query)
	
	def getVideosByChannel(self, channelName):
		endpoint = "kraken/channels/%s/videos" % (channelName)
		query = {
			"limit": 50
		}
		return self.call(endpoint, query)

	def getTopStreams(self, offset = 0, limit = 50):
		endpoint = "kraken/streams"
		query = {
			"stream_type": "live",
			"limit": limit,
			"offset": offset
		}
		return self.call(endpoint, query)

	def getTopGames(self, offset = 0, limit = 50):
		endpoint = "kraken/games/top"
		query = {
			"limit": limit,
			"offset": offset
		}
		return self.call(endpoint, query)

class usherHandler:
	def __init__(self):
		# self.baseurl = 'https://usher.ttvnw.net'
		self.baseurl = 'https://usher.twitch.tv'

		return None

	def call(self, endpoint, query = None):
		queryArgs = None
		if (query):
			queryArgs = urllib.urlencode(query)
		url = "%s/%s?%s" % (self.baseurl, endpoint, queryArgs)
		request = urllib2.Request(url)

		try:
			response = urllib2.urlopen(request)
			retData = response.read()
			response.close()
			return retData
		except URLError, e:
			print e
		
		return None

	def getStreams(self, endpoint, sig, token):
		query = {
			"player": "twitchweb",
			"type": "any",
			"allow_source": "true",
			"allow_audio_only": "true",
			"allow_spectre": "false",
			"p": int(random() * 999999),
			"sig": sig,
			"token": token
		}
		return self.call(endpoint, query)

	def getChannelStreams(self, channelName, sig, token):
		endpoint = "api/channel/hls/%s" % (channelName)

		return self.getStreams(endpoint, sig, token)

	def getVideoStreams(self, videoId, sig, token):
		endpoint = "vod/%s" % (videoId)
		
		return self.getStreams(endpoint, sig, token)

class helpersHandler:
	def parseURL(self, url):
		return _url_re.match(url).groupdict()

	def getVideoType(self, url):
		types = self.parseURL(url)

		if (types['channel']):
			return {'type': 'channel', 'id': types['channel']}

		if (types['videos_id']):
			return {'type': 'video', 'id': types['videos_id']}

		return None

	def getPrefferedVideoURL(self, data):
		sm3u8Parser = sm3u8.parseHandler()
		playlists = sm3u8Parser.parse(data)
	
		for quality in cfg.twitchQualityWeight:
			for idx in playlists:
				if (playlists[idx]):
					if (quality == playlists[idx]['video']):
						return playlists[idx]['uri']
		
		return None

def main(argv):
	twitchApi = twitchAPIHandler()
	usherApi = usherHandler()
	helpers = helpersHandler()
	video = {'type': ''}
	playlists = dict()
	
	if len(argv) == 0:
		print "No arguments given. Use twitch.py -h for more info.\nThe script must be used from the shell."
		sys.exit()
		
	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that uses twitch.tv API to get information about channels/videos for AmigaOS 4.1 and above.')
	argParser.add_argument('-u', '--url', action='store', dest='url', help='The video/channel url from twitch.tv')
	argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
	argParser.add_argument('-ts', '--top-streams', action='store_true', default=False, dest='topstreams', help='Get a list of the current Top Live Streams, based on the number of viewers')
	argParser.add_argument('-tg', '--top-games', action='store_true', default=False, dest='topgames', help='Get a list of the current Top Games with live streams available, based on the number of viewers')
	argParser.add_argument('-sg', '--search-game', action='store', dest='searchgame', help='Search for available streams based on game title')
	argParser.add_argument('-cv', '--channel-videos', action='store_true', default=False, dest='channelvideos', help='Request the recorded videos of a channel. The -u argument is mandatory.')
	argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
	args = argParser.parse_args()
	
	if (args.silence != True):
		cmnHandler.showIntroText()
	if (args.url):
		twitchURL = args.url
		video = helpers.getVideoType(args.url)
	if (args.quality):
		cfg.twitchQualityWeight.insert(0, args.quality)

	if (args.topstreams):
		streamList = twitchApi.getTopStreams()
		print "%-36s\t %-10s\t %-6s\t %-50s\t %s" % ('URL', 'Viewers', "Lang", 'Game', 'Title')
		print "%s" % ('-'*200)
		for stream in streamList['streams']:
			print "%-36s\t %-10d\t %-6s\t %-50s\t %s" % (stream['channel']['url'], stream['viewers'], stream['channel']['language'], stream['game'], cmnHandler.uniStrip(stream['channel']['status']))

		sys.exit()

	if (args.topgames):
		gamesList = twitchApi.getTopGames()
		print "%-50s\t %-10s\t %-10s" % ('Game', 'Viewers', 'Channels')
		print "%s" % ('-'*200)
		for game in gamesList['top']:
			print "%-50s\t %-10d\t %-10d" % (cmnHandler.uniStrip(game['game']['name']), game['viewers'], game['channels'])

		sys.exit()

	if (args.channelvideos):
		channelName = video['id']
		streamList = twitchApi.getVideosByChannel(channelName)
		print "%-36s\t %-20s\t %-50s\t %s" % ('URL', 'Recorded at', 'Available resolutions', 'Title')
		print "%s" % ('-'*200)
		for stream in streamList['videos']:
			resolutions = ', '.join(stream['resolutions'])
			print "%-36s\t %-20s\t %-50s\t %s" % (stream['url'], stream['recorded_at'], resolutions, cmnHandler.uniStrip(stream['title']))

		sys.exit()

	if (args.searchgame):
		gameTitle = args.searchgame
		streamList = twitchApi.searchByGameTitle(gameTitle)
		print "%-30s\t %10s\t %-s\t %-6s\t %-50s\t %-s - %-s" % ("Channel name", "Viewers", "Type", "Lang", "Channel URL", "Game name", "Channel status")
		print "%s" % ('-'*200)
		for stream in streamList['streams']:
			channel = stream['channel']
			print "%-30s\t %10d\t %-s\t %-6s\t %-50s\t %-s - \"%-s\"" % (cmnHandler.uniStrip(channel['display_name']), stream['viewers'], stream['stream_type'], channel['language'], channel['url'], cmnHandler.uniStrip(stream['game']), cmnHandler.uniStrip(channel['status']))
		
		sys.exit()

	if (video['type'] == 'channel'):
		channelName = video['id']
			
		streams = twitchApi.getStreamsByChannel(channelName)
		if (streams):
			if (streams['stream']):
				if (streams['stream']['stream_type'] == 'live'):
					accessToken = twitchApi.getAccessTokenByChannel(channelName)
					m3u8Response = usherApi.getChannelStreams(channelName, accessToken['sig'], accessToken['token'])
					if (m3u8Response):
						uri = helpers.getPrefferedVideoURL(m3u8Response)
						if uri:
							if cfg.verbose and (args.silence != True):
								print "%s" % (uri)
							if cfg.autoplay:
								cmnHandler.videoAutoplay(uri, 'list')
						else:
							print "Not valid stream found"
					else:
						print "There was an error with the usherApi"
			else:
				print "There is no Live stream for the channel: %s" % (channelName)

		sys.exit()

	if (video['type'] == 'video'):
		videoId = video['id']

		streams = twitchApi.getVideoInfoByID(videoId)
		if (streams):
			if (streams['viewable'] == 'public'):
				accessToken = twitchApi.getAccessTokenByVideo(videoId)
				m3u8Response = usherApi.getVideoStreams(videoId, accessToken['sig'], accessToken['token'])
				if (m3u8Response):
					uri = helpers.getPrefferedVideoURL(m3u8Response)
					if uri:
						if cfg.verbose and (args.silence != True):
							print "%s" % (uri)
						if cfg.autoplay:
							cmnHandler.videoAutoplay(uri, 'video')
					else:
						print "Not valid video found"
				else:
					print "There was an error with the usherApi"
				
		else:
			print "There is no video available with ID: %s" % (videoId)

		sys.exit()
	
	sys.exit()


if __name__ == "__main__":
	main(sys.argv[1:])
