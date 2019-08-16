#!python

import urllib, urllib2, sys, subprocess, textwrap, datetime, time, argparse
import simplejson as json
# from pprint import pprint
from urllib2 import Request, urlopen, URLError
from random import random
# import m3u8

clientId = "k5y7u3ntz5llxu22gstxyfxlwcz10v"


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
		
		return

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

class usherHandler:
	def __init__(self):
		self.baseurl = 'https://usher.ttvnw.net'

		return

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
		
		return

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

def main(argv):
	twitchApi = twitchAPIHandler()
	usherApi = usherHandler()

	# TODO: Replace this with code to parse a twitch url 
	channelName = "riotgamesoce"

	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that uses twitch.tv API to get information about channels/videos for AmigaOS 4.1 and above.')
	#argParser.add_argument('-p', '--project', action='store', dest='project_name', help='set the project name')
	args = argParser.parse_args()
	
	# twitchApi.getStreamsByChannel(channelName)
	accessToken = twitchApi.getAccessTokenByChannel(channelName)
	usherApi.getChannelStreams(channelName, accessToken['sig'], accessToken['token'])
	
	sys.exit()


if __name__ == "__main__":
	main(sys.argv[1:])
