#!python
# coding=utf-8
import cfg, cmn, vqw
import sys, argparse, re, string
import simplejson as json
from random import random

if sys.version_info[0] == 2:
    import urllib
    import urllib2
    from urllib2 import Request as urlReq, urlopen as urlOpn, URLError as urlErr

if sys.version_info[0] == 3:
    import urllib.parse as urllib
    import urllib3
    from urllib.request import Request as urlReq, urlopen as urlOpn
    from urllib.error import URLError as urlErr

cmnHandler = cmn.cmnHandler()

class radioAPIHandler:
    def __init__(self):
        self.baseurl = 'http://de1.api.radio-browser.info/json'

        return None

    def getURL(self, url):
        request = urlReq(url)
        request.add_header('User-Agent', cmnHandler.spoofAs('CHROME'))
        try:
            response = urlOpn(request)
            retData = response.read()
            response.close()
            return retData
        except (urlErr, e):
            print (e)
        
        return None

    def call(self, endpoint, query = None):
        url = "%s/%s" % (self.baseurl, endpoint)
        if (query):
            queryArgs = urllib.urlencode(query)
            url = "%s/%s?%s" % (self.baseurl, endpoint, queryArgs)

        return self.getURL(url)

    def getCountries(self):
        endpoint = "countries"
        query = {
            # "order": "stationcount",
            # "reverse": "true"
        }
        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def getStations(self, query = {}):
        endpoint = "stations/search"
        # query = {
            # "order": "stationcount",
            # "reverse": "true"
        # }
        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None

    def getStationByID(self, uuid):
        endpoint = "stations/byuuid"
        query = {
            "uuids": uuid
        }
        responseData = self.call(endpoint, query)
        if responseData:
            return json.loads(responseData)
        return None


def main(argv):
    radioApi = radioAPIHandler()

    if len(argv) == 0:
        print ("No arguments given. Use radio.py -h for more info.\nThe script must be used from the shell.")
        sys.exit()
        
    # Parse the arguments
    argParser = argparse.ArgumentParser(description=cmnHandler.getScriptDescription('radio stations'), epilog=cmnHandler.getScriptEpilog(),
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    argParser.add_argument('-lc', '--list-countries', action='store_true', default=False, dest='listCountries', help='List the available countries')
    argParser.add_argument('-src', '--search', action='store_true', default=False, dest='search', help='Initiate search for radio stations')
    argParser.add_argument('-pl', '--play', action='store_true', default=False, dest='play', help='Automatically play a radio station. Use --uuid to set the station.')
    argParser.add_argument('-sn', '--station-name', action='store', dest='stationName', help='Filter stations based on name. This is used with --search argument.')
    argParser.add_argument('-sg', '--station-genre', action='store', dest='stationGenre', help='Filter stations based on genre. This is used with --search argument.')
    argParser.add_argument('-sc', '--station-country', action='store', dest='stationCountry', help='Filter stations based on country. This is used with --search argument.')
    argParser.add_argument('-sl', '--station-language', action='store', dest='stationLanguage', help='Filter stations based on language. This is used with --search argument.')
    argParser.add_argument('-id', '--uuid', action='store', dest='stationUUID', help='Autoplay the station based on the UUID. This is used with --play argument.')
    argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
    args = argParser.parse_args()

    if (args.silence != True):
        cmnHandler.showIntroText()

    if (args.listCountries):
        countriesData = radioApi.getCountries()
        if countriesData:
            print ("%s\t %s" % ('Stations', 'Country'))
            print ("%s" % ('-'*100))
            for country in countriesData:
                print ("%d\t\t %s" % (country['stationcount'], country['name']))
        
        sys.exit()

    if (args.search):
        params = {}
        if args.stationName:
            params.update({'name': args.stationName})
        if args.stationGenre:
            params.update({'tag': args.stationGenre})
        if args.stationCountry:
            params.update({'country': args.stationCountry})
        if args.stationLanguage:
            params.update({'language': args.stationLanguage})

        if len(params) == 0:
            print ("Use at least on of the available filters on station search (name, language, country, genre)")
            sys.exit()

        stations = radioApi.getStations(params)
        if stations:
            print ("%-24s %-24s %-5s %-7s %-40s %s" % ('Name', 'Country', 'Codec', 'Bitrate', '  ID', 'URL'))
            print ("%s" % ('-'*180))
            for station in stations:
                print ("%-24s %-24s %-5s %-7d %-40s %s" % (
                    cmnHandler.uniStrip(station['name'])[:22],
                    cmnHandler.uniStrip(station['country'])[:22],
                    station['codec'],
                    station['bitrate'],
                    station['stationuuid'],
                    station['url_resolved']
                ))

        sys.exit()

    if (args.play):
        if not args.stationUUID:
            print ("Please define which station to autoplay by setting the UUID (--uuid) argument.")
            sys.exit()
        

        stationData = radioApi.getStationByID(args.stationUUID)
        if stationData:
            uri = stationData[0]['url_resolved']
            if (args.silence != True):
                print ("%s\nCountry: %s\nLanguage: %s\nGenre tags: %s\nWebsite: %s" % (
                    cmnHandler.uniStrip(stationData[0]['name']),
                    stationData[0]['country'],
                    cmnHandler.uniStrip(stationData[0]['language']),
                    stationData[0]['tags'],
                    stationData[0]['homepage']
                ))

            if (uri):
                if cfg.verbose and (args.silence != True):
                    print ("\n%s" % (uri))
                if cfg.autoplay:
                    cmnHandler.audioAutoplay(uri)
        
        sys.exit()

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
