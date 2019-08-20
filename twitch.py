#!python
try:
	import amiga
	amigaMode = True
except:
	pass
import urllib, urllib2, sys, argparse, re, string
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random
#from pprint import pprint
import cfg

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

ATTRIBUTELISTPATTERN = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')

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

	def searchByGameTitle(self, title):
		endpoint = "kraken/search/streams"
		query = {
			"query": title
		}
		retData = self.call(endpoint, query)

		return retData

class usherHandler:
	def __init__(self):
		self.baseurl = 'https://usher.ttvnw.net'

		return None

	def call(self, endpoint, query = None):
		queryArgs = None
		if (query):
			queryArgs = urllib.urlencode(query)
		url = "%s/%s?%s" % (self.baseurl, endpoint, queryArgs)
		#print(url)
		request = urllib2.Request(url)

		try:
			response = urllib2.urlopen(request)
			retData = response.read()
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
		#print retData

		return retData

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
		#print retData

		return retData


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
		print "Find preffered URL"
		#playlists = self.m3u8GetPlaylists(data)
		playlists = self.simpleM3U8Parser(data)
		
		#pprint(playlists)
		weightCnt = 0
		for quality in cfg.twitchQualityWeight:
			for idx in playlists:
				if (quality == playlists[idx]['video']):
					#print quality
					#print playlists[idx]['video']
					# print playlist['uri']
					# print "---------------------------"
					# break
					return playlists[idx]['uri']
		
		return None

	def encodeToken(self, token):
		encToken = string.replace(token, '"', "%22")
		encToken = string.replace(encToken, "{", "%7B")
		encToken = string.replace(encToken, "}", "%7D")

		return encToken
	
	# TODO: split to smaller methods
	def simpleM3U8Parser(self, m3u8Data):
		lineNum = 0
		listCnt = None
		retList = {}
		listDict = dict()
		#print m3u8Data
		#print "###########################################################"
		
		for line in m3u8Data.splitlines():
			#print "%d - %s" % (lineNum, line)

			if (line.startswith("#EXT-X-MEDIA:")):
				extMedia = line.replace("#EXT-X-MEDIA:", "")
				extMedia = extMedia.replace("\n", "")
				extMedia = extMedia.replace("'", "")
				extMedia = extMedia.replace('"', "")
			
			
				#print extMedia
				param, value = line.split(":", 1)
				params = ATTRIBUTELISTPATTERN.split(extMedia)[1::2]
				#print "PARAM: %s \nVALUE: %s" % (param, value)
				#print params
				#extMediaDict = dict(item.split("=") for item in extMedia.split(","))
				if (listCnt == None):
					listCnt = 0
					#retList[listCnt] = {}
				else:
					#print "-------------------------"
					#print listCnt
					#print listDict
					#pprint(retList)
					#retList[listCnt] = listDict
					#retData.append(listDict)
					#retData.update({ listCnt: listDict })
					#pprint(retData)
					#listDict.clear()
					#pprint(listDict)
					listCnt += 1
					#retList[listCnt] = {}
				
				retList[listCnt] = {}
				
				for attribute in params:
					attr, val = attribute.split("=")
					#print "%d -> %s - %s" % (listCnt, attr.lower(), val.lower())
					#listDict[attr.lower()] = val.lower()
					retList[listCnt][attr.lower()] = val.lower()
					
				#playlists[listCnt] = extMediaDict
				#print extMediaDict

			if (line.startswith("#EXT-X-STREAM-INF:")):
				#print "%d - %s" % (lineNum, line)
				extStream = line.replace("#EXT-X-STREAM-INF:", "")
				extStream = extStream.replace("\n", "")
				#extStream = extStream.replace("'", "")
				#extStream = extStream.replace('"', "")
			
				params = ATTRIBUTELISTPATTERN.split(extStream)[1::2]
			
				for attribute in params:
					#print attribute
					attr, val = attribute.split("=")
					val = val.replace('"', "")
					#print "%d -> %s - %s" % (listCnt, attr.lower(), val.lower())
					#listDict[attr.lower()] = val.lower()
					retList[listCnt][attr.lower()] = val.lower()
			
				#print extStream
				#print params
				#extStreamDict = dict(item.split("=") for item in extStream.split(","))
				#for item in extStream.split(","):
				#	print item.split("=")
					#playlists[listCnt].append(item.split("="))
				#playlists[listCnt] = extStreamDict
		
			if (line.startswith(('https://', 'http://'))):
				#listDict['uri'] = line
				retList[listCnt]['uri'] = line
		
			lineNum += 1
		#print "--------------------------------------------------"
		#print "--------------------------------------------------"
		#pprint(retList)
		return retList

def main(argv):
	twitchApi = twitchAPIHandler()
	usherApi = usherHandler()
	helpers = helpersHandler()
	video = {'type': ''}
	searchMode = False
	playlists = dict()

	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that uses twitch.tv API to get information about channels/videos for AmigaOS 4.1 and above.')
	argParser.add_argument('-u', '--url', action='store', dest='url', help='The video/channel url from twitch.tv')
	argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
	argParser.add_argument('-s', '--search', action='store', dest='search', help='Search for available streams based on game title')
	args = argParser.parse_args()

	if (args.url):
		twitchURL = args.url
		video = helpers.getVideoType(args.url)
	if (args.quality):
		cfg.twitchQualityWeight.insert(0, args.quality)
	if (args.search):
		gameTitle = args.search
		searchMode = True

	if (video['type'] == 'channel'):
		channelName = video['id']
			
		streams = twitchApi.getStreamsByChannel(channelName)
		if (streams):
			if (streams['stream']):
				if (streams['stream']['stream_type'] == 'live'):
					accessToken = twitchApi.getAccessTokenByChannel(channelName)
					m3u8Response = usherApi.getChannelStreams(channelName, accessToken['sig'], accessToken['token'])
					uri = helpers.getPrefferedVideoURL(m3u8Response)
					if uri and cfg.autoplay:
						print "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs)
						amiga.system( "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs) )
			else:
				print "There is no Live stream for the channel: %s" % (channelName)


	if (video['type'] == 'video'):
		videoId = video['id']

		streams = twitchApi.getVideoInfoByID(videoId)
		if (streams):
			if (streams['viewable'] == 'public'):
				accessToken = twitchApi.getAccessTokenByVideo(videoId)
				m3u8Response = usherApi.getVideoStreams(videoId, accessToken['sig'], accessToken['token'])
				uri = helpers.getPrefferedVideoURL(m3u8Response)
				if uri and cfg.autoplay:
					print "%s %s %s" % (cfg.vPlayer, uri, cfg.vPlayerArgs)
					amiga.system( "%s %s %s" % (cfg.vPlayer, uri, cfg.vPlayerArgs) )
				
		else:
			print "There is no video available with ID: %s" % (videoId)

	if (searchMode):
		streamList = twitchApi.searchByGameTitle(gameTitle)
		for stream in streamList['streams']:
			channel = stream['channel']
			print "%-20s\t %10s\t %-s\t %-10s\t %-50s\t %-s - \"%-s\"" % (channel['display_name'].encode('unicode_escape'), stream['viewers'], stream['stream_type'], channel['language'], channel['url'], stream['game'].encode('unicode_escape'), channel['status'].encode('unicode_escape'))
			#print "%-20s\t %10s\t %-s\t %-10s\t %-50s\t " % (channel['display_name'].encode('unicode_escape'), stream['viewers'], stream['stream_type'], channel['language'], channel['url'])

	# TODO: The following code is for testing the m3u8 parser with the demo files
	#f = open("demoLives.m3u8", "r")
	#playlists = helpers.simpleM3U8Parser(f)
	#print(f.readline())
	#uri = helpers.getPrefferedVideoURL(f.read())
	#f.close()
	#print playlists

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
