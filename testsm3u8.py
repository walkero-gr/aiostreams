#!python
# This is just a testing script for the simplem3u8.py and it is not necessary
# for the rest of the scripts
import sys
import simpleM3U8 as sm3u8

def main(argv):
    f = open("demoLives.m3u8", "r")
    # print f.read()
    sm3u8Parser = sm3u8.parseHandler()
    playlists = sm3u8Parser.parse(f.read())
    f.close()
    print playlists


if __name__ == "__main__":
	main(sys.argv[1:])