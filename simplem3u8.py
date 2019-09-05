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
				params = self.parseExt(line, "#EXT-X-MEDIA:")

				for attribute in params:
					attr, val = attribute.split("=")
					retList[listCnt][attr.lower()] = val.lower()

            if (line.startswith("#EXT-X-STREAM-INF:")):
                params = self.parseExt(line, "#EXT-X-STREAM-INF:")

                for attribute in params:
                    attr, val = attribute.split("=")
                    val = val.replace('"', "")
                    retList[listCnt][attr.lower()] = val.lower()

            if (line.startswith(('https://', 'http://', '../'))):
                retList[listCnt]['uri'] = line
                listCnt += 1
                retList[listCnt] = {}

        return retList
    
    def parseExt(self, line, tag):
        extMedia = line.replace(tag, "")
        extMedia = extMedia.replace("\n", "")

        return ATTRIBUTELISTPATTERN.split(extMedia)[1::2]
