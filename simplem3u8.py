#!python
import re
ATTRIBUTELISTPATTERN = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')

class parseHandler:
    def parse(self, m3u8Data):
        listCnt = 0
        retList = {}
        retList[listCnt] = {}

        for line in m3u8Data.splitlines():
            if (line.startswith("#EXT-X-MEDIA:")):
                params = self.parseXMedia(line)
                
                for attribute in params:
                    attr, val = attribute.split("=")
                    retList[listCnt][attr.lower()] = val.lower()

            if (line.startswith("#EXT-X-STREAM-INF:")):
                params = self.parseXStreamInf(line)

                for attribute in params:
                    attr, val = attribute.split("=")
                    val = val.replace('"', "")
                    retList[listCnt][attr.lower()] = val.lower()

            if (line.startswith(('https://', 'http://', '../'))):
                retList[listCnt]['uri'] = line
                listCnt += 1
                retList[listCnt] = {}

        return retList
    
    def parseXMedia(self, line):
        extMedia = line.replace("#EXT-X-MEDIA:", "")
        extMedia = extMedia.replace("\n", "")
        extMedia = extMedia.replace("'", "")
        extMedia = extMedia.replace('"', "")

        params = ATTRIBUTELISTPATTERN.split(extMedia)[1::2]

        return params
    
    def parseXStreamInf(self, line):
        extStream = line.replace("#EXT-X-STREAM-INF:", "")
        extStream = extStream.replace("\n", "")

        params = ATTRIBUTELISTPATTERN.split(extStream)[1::2]

        return params
