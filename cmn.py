# coding=utf-8
import sys, re, os
import cfg
import unicodedata
try:
    import amiga
except ImportError:
    pass

aioVer = "1.7"
aioReleaseDate = "2021-01-15"
userOS = sys.platform

class cmnHandler:
    def getIntroVersionText(self):
        return "aiostreams v%s (%s) - Developed by George Sokianos\n" % (aioVer, aioReleaseDate)

    def showIntroText(self):
        print self.getIntroVersionText()

    def getUserOS(self):
        return userOS
        
    def uniStrip(self, text):
        if (userOS == 'ppc-amiga' or userOS == 'morphos'):
            return re.sub(r'[^\x00-\x7f]',r'', text)
            # text = unicodedata.normalize('NFKD', text).encode('ascii', 'xmlcharrefreplace')
        return text

    def spoofAs(self, agent):
        agents = {
            'CHROME': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'FIREFOX': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'ANDROID': 'Mozilla/5.0 (Linux; Android 7.1.1; SM-J510FN Build/NMF26X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36',
            'EDGE': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
        }

        try:
            return agents[agent]
        except KeyError:
            return None

    def videoAutoplay(self, uri, videoType = 'list'):
        player = cfg.vPlayer
        playerArgs = cfg.vPlayerArgs
        
        if (videoType == 'list'):
            player = cfg.sPlayer
            playerArgs = cfg.sPlayerArgs

        if (userOS == 'ppc-amiga'):
            amiga.system( "Run <>NIL: %s %s %s" % (player, uri, playerArgs) )
        else:
            os.system( '%s "%s" %s' % (player, uri, playerArgs) )

    def audioAutoplay(self, uri):
        player = cfg.aPlayer
        playerArgs = cfg.aPlayerArgs

        if (userOS == 'ppc-amiga'):
            amiga.system( "Run <>NIL: %s %s %s" % (player, uri, playerArgs) )
        else:
            os.system( '%s "%s" %s' % (player, uri, playerArgs) )

    def getScriptDescription(self, networkName):
        descr = "%s\
(https://github.com/walkero-gr/aiostreams)\n\n\
This is a python script for %s online streaming platform.\n\
You can use this to discover and watch a streaming, using your beloved video player." % (self.getIntroVersionText(), networkName)

        return descr
    
    def getScriptEpilog(self):
        descr = "\
aiostreams is DONATIONWARE.\n\
If you find this project useful, please consider to donate at https://www.paypal.me/gsokianos\n\
Your support is much appreciated."
        return descr