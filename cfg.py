#!python
autoplay = True
verbose = True

# AmigaOS 4.1 FE players
vPlayer = "APPDIR:mplayer"
vPlayerArgs = "-quiet -really-quiet -forceidx -framedrop -cache 8192"
sPlayer = "APPDIR:ffplay"
sPlayerArgs = "-loglevel quiet -infbuf -skip_loop_filter all -skip_frame noref"

# MacOS X players
# vPlayer = "~/Applications/VLC.app/Contents/MacOS/VLC"
# vPlayerArgs = "-f --no-video-title-show 2> /dev/null"
# sPlayer = "~/Applications/VLC.app/Contents/MacOS/VLC"
# sPlayerArgs = "-f --no-video-title-show 2> /dev/null"

# Linux players
# vPlayer = "/usr/bin/vlc"
# vPlayerArgs = "-f --no-video-title-show 2> /dev/null"
# sPlayer = "/usr/bin/vlc"
# sPlayerArgs = "-f --no-video-title-show 2> /dev/null"

twitchQualityWeight = [
	"480p30",
	"360p30",
	"160p30",
	"720p60",
	"720p30",
	"chunked",
	"audio_only"
]

mixerQualityWeight = [
	"480p",
	"320p",
	"160p",
	"720p",
	"1080p"
]

vimeoQualityWeight = [
	"360p",
	"240p",
	"480p",
	"540p",
	"720p",
	"1080p"
]

dailymotionQualityWeight = [
	"480",
	"380",
	"240",
	"144",
	"720",
	"1080"
]

ytQualityWeight = [
	43,			# 360p mp4, audio quality medium
	18,			# 360p mp4, audio quality low
	22,			# 720p mp4, audio quality medium
	# 135,		# 480p mp4
	# 244,		# 480p webm
	# 134,		# 360p mp4
	# 243,		# 360p webm
	# 242,		# 240p mp4
	# 136,		# 240p webm
	# 160,		# 144p mp4
	# 278,		# 144p webm
	# 136,		# 720p mp4
	# 247,		# 720p webm
	# 137,		# 1080p mp4
	# 248,		# 1080p webm
	# 140,		# mp4, audio only, 44100, medium
	# 249,		# webm, audio only, 48000, low
	# 250,		# webm, audio only, 48000, low
	# 251,		# webm, audio only, 48000, medium
]

ytLiveQualityWeight = [
	480,		# 480p mp4
	360,		# 360p mp4
	240,		# 240p mp4
	144,		# 144p mp4
	720,		# 720p mp4
	1080		# 1080p mp4
]

dliveQualityWeight = [
	"480p",
	"360p",
	"720p",
	"src"
]

peertubeQualityWeight = [
	"480p",
	"360p",
	"240p",
	"720p",
	"768p",
	"1080p"
]
