# coding=utf-8
import sys, re

aioVer = "1.3"
aioReleaseDate = "2019-09-15"
userOS = sys.platform

try:
	import amiga
	userOS = "os4"
except:
	pass

class cmnHandler:
	def showIntroText(self):
		print "aiostreams v%s (%s) - Developed by George Sokianos\n" % (aioVer, aioReleaseDate)

	def getUserOS(self):
		return userOS
		
	def uniStrip(self, text):
		if (userOS == 'os4'):
			return re.sub(r'[^\x00-\x7f]',r'', text)
		return text
