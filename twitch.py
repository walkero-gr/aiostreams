#!python

import urllib, urllib2, sys, subprocess, textwrap, datetime, time, argparse, re
import simplejson as json
# from pprint import pprint
from urllib2 import Request, urlopen, URLError
from random import random
import m3u8

clientId = "k5y7u3ntz5llxu22gstxyfxlwcz10v"

videoPlayer = "APPDIR:ffmpeg"
streamPlayer = "APPDIR:ffplay"

qualityWeight = [
	"480p30",
	"360p30",
	"160p30",
	"audio_only",
	"chunked",
	"720p60",
	"720p30"
]

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

	def call(self, endpoint):
		url = "%s/%s" % (self.baseurl, endpoint)
		request = urllib2.Request(url)
		request.add_header('Accept', 'application/vnd.twitchtv.v4+json')
		request.add_header('Client-ID', clientId)
		try:
			response = urllib2.urlopen(request)
			retData = json.load(response)
			response.close()
			return retData
		except URLError, e:
			print e.reason
		
		return None

	def getChannelInfoByName(self, channelName):
		endpoint = "kraken/channels/%s.json" % (channelName)
		retData = self.call(endpoint)
		# print retData

		return retData

	def getStreamsByChannel(self, channelName):
		endpoint = "kraken/streams/%s.json" % (channelName)
		retData = self.call(endpoint)
		# print retData

		return retData

	def getAccessTokenByChannel(self, channelName):
		endpoint = "api/channels/%s/access_token.json" % (channelName)
		retData = self.call(endpoint)
		# print retData

		return retData

	def getVideoInfoByID(self, videoId):
		endpoint = "kraken/videos/%s.json" % (videoId)
		retData = self.call(endpoint)
		# print retData

		return retData

	def getAccessTokenByVideo(self, videoId):
		endpoint = "api/vods/%s/access_token.json" % (videoId)
		retData = self.call(endpoint)
		# print retData

		return retData

class usherHandler:
	def __init__(self):
		self.baseurl = 'https://usher.ttvnw.net'

		return None

	def call(self, endpoint, query):
		query_args = urllib.urlencode(query)
		url = "%s/%s" % (self.baseurl, endpoint)
		print(url)
		request = urllib2.Request(url, query_args)

		try:
			response = urllib2.urlopen(request)
			retData = json.load(response)
			response.close()
			return retData
		except URLError, e:
			print e.reason
		
		return None

	def getChannelStreams(self, channelName, sig, token):
		endpoint = "api/channel/hls/%s" % (channelName)
		query = {
			"player": "twitchweb",
			"type": "any",
			"allow_source": "true",
			"allow_audio_only": "true",
			"allow_spectre": "false",
			"p": int(random() * 999999),
			"nauthsig": sig,
			"nauth": token
		}
		retData = self.call(endpoint, query)
		print retData

		return # retData

	def getVideoStreams(self, videoId, sig, token):
		endpoint = "vod/%s" % (videoId)
		query = {
			"player": "twitchweb",
			"type": "any",
			"allow_source": "true",
			"allow_audio_only": "true",
			"allow_spectre": "false",
			"p": int(random() * 999999),
			"nauthsig": sig,
			"nauth": token
		}
		retData = self.call(endpoint, query)
		print retData

		return # retData


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

	def m3u8GetModel(self, data):
		m3u8Data = m3u8.loads(data)
		return m3u8Data.data
	
	def m3u8GetPlaylists(self, data):
		m3u8Model = self.m3u8GetModel(data)
		# print m3u8Model['playlists']
		return m3u8Model['playlists']
	
	def m3u8GetMedia(self, data):
		m3u8Model = self.m3u8GetModel(data)
		# print m3u8Model['media']
		return m3u8Model['media']

	def getPrefferedVideoURL(self, data):
		playlists = self.m3u8GetPlaylists(data)

		weightCnt = 0
		for quality in qualityWeight:
			for playlist in playlists:
				if (quality == playlist['stream_info']['video']):
					# print quality
					# print playlist['stream_info']['video']
					# print playlist['uri']
					# print "---------------------------"
					# break
					return playlist['uri']


def main(argv):
	twitchApi = twitchAPIHandler()
	usherApi = usherHandler()
	helpers = helpersHandler()
	video = {'type': ''}

	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that uses twitch.tv API to get information about channels/videos for AmigaOS 4.1 and above.')
	argParser.add_argument('-u', '--url', action='store', dest='url', help='The video/channel url from twitch.tv')
	argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
	args = argParser.parse_args()

	if (args.url):
		twitchURL = args.url
		video = helpers.getVideoType(args.url)
	if (args.quality):
		qualityWeight.insert(0, args.quality)


	if (video['type'] == 'channel'):
		channelName = video['id']
			
		streams = twitchApi.getStreamsByChannel(channelName)
		if (streams):
			if (streams['stream']):
				if (streams['stream']['stream_type'] == 'live'):
					accessToken = twitchApi.getAccessTokenByChannel(channelName)
					usherApi.getChannelStreams(channelName, accessToken['sig'], accessToken['token'])
			else:
				print "There is no Live stream for the channel: %s" % (channelName)


	if (video['type'] == 'video'):
		videoId = video['id']

		streams = twitchApi.getVideoInfoByID(videoId)
		if (streams):
			if (streams['viewable'] == 'public'):
				accessToken = twitchApi.getAccessTokenByVideo(videoId)
				# usherApi.getVideoStreams(videoId, accessToken['sig'], accessToken['token'])
		else:
			print "There is no video available with ID: %s" % (videoId)


	# TODO: The following code is for testing the m3u8 parser with the demo files
	# f = open("demoLives.m3u8", "r")
	# print(f.read()) 
	# uri = helpers.getPrefferedVideoURL(f.read())
	# f.close()
	# print uri


	# TODO: The following list is temporary for tests. This will be removed
	# https://www.twitch.tv/bnepac
	# https://www.twitch.tv/videos/464055415
	# channels = [
	# 	"riotgamesoce",
	# 	"amigabill",
	# 	"haysmaker64",
	# 	"overwatchleague"
	# ]
	# channelName = channels[1]


	
	sys.exit()


if __name__ == "__main__":
	main(sys.argv[1:])
