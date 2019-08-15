#!python

import urllib2, sys, subprocess, textwrap, datetime, time, argparse
from pprint import pprint
import simplejson as json
#import m3u8

clientId = "pwkzresl8kj2rdj6g7bvxl9ys1wly3j"


def apiGetChannelInfoByName(channelName):
	#url = "https://%(te)s.teamwork.com/tasks/%(cid)s.json" % {'te': "api", 'cid': clientId}
	#url = "https://%s.teamwork.com/tasks/%s.json" % ("api", clientId)
	url = "https://api.twitch.tv/kraken/channels/%s.json" % (channelName)
	print(url)
	#headers = urllib3.util.make_headers(basic_auth=key + ":xxx")
	#request = http.request('GET', url, headers=headers)
	request = urllib2.Request(url)
	request.add_header('Accept', 'application/vnd.twitchtv.v4+json')
	request.add_header('Client-ID', clientId)
	response = urllib2.urlopen(request)
	
	#print(response.read())
	#response = request.status
	retData = json.load(response)
	print(retData['status'])
	return 0 #retData

def apiGetStreamsByChannel(channelName):
	url = "https://api.twitch.tv/kraken/streams/%s.json" % (channelName)
	print(url)
	request = urllib2.Request(url)
	request.add_header('Accept', 'application/vnd.twitchtv.v4+json')
	request.add_header('Client-ID', clientId)
	response = urllib2.urlopen(request)
	
	retData = json.load(response)
	print(retData)
	return 0 #retData

def apiGetAccessTokenByChannel(channelName):
	url = "https://api.twitch.tv/api/channels/%s/access_token.json" % (channelName)
	print(url)
	request = urllib2.Request(url)
	request.add_header('Accept', 'application/vnd.twitchtv.v4+json')
	request.add_header('Client-ID', clientId)
	response = urllib2.urlopen(request)
	
	retData = json.load(response)
	# print(retData['token'])
	# print(retData['sig'])
	return retData

def usherGetChannelStreams(channelName, sig, token):
	url = "https://usher.ttvnw.net/api/channel/hls/%s?player=twitchweb&type=any&allow_source=true&allow_audio_only=true&allow_spectre=false&p=100&nauthsig=%s&&nauth=%s" % (channelName, sig, token)
	print(url)
	request = urllib2.Request(url)
	request.add_header('Accept', 'application/vnd.twitchtv.v4+json')
	request.add_header('Client-ID', clientId)
	response = urllib2.urlopen(request)
	
	#retData = json.load(response)
	print(response.read())
	# print(retData['sig'])
	return 0 # retData

def main(argv):
	channelName = "hayesmaker64"
	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that can be used to get information from Teamwork Projects Management. You can find more info at https://github.com/walkero-gr/tw')
	#argParser.add_argument('-p', '--project', action='store', dest='project_name', help='set the project name')
	args = argParser.parse_args()
	
	# print(json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}]))
	accessToken = apiGetAccessTokenByChannel(channelName)
	usherGetChannelStreams(channelName, accessToken['sig'], accessToken['token'])
	
	sys.exit()


if __name__ == "__main__":
	main(sys.argv[1:])
