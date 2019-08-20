#!python
autoplay = True
vPlayer = "Applications:Video/MickJT-Mplayer/mplayer"
vPlayerArgs = "-quiet -really-quiet -forceidx -framedrop -cache 8192"
sPlayer = "APPDIR:ffplay"
sPlayerArgs = "-loglevel quiet -infbuf -skip_loop_filter all -skip_frame noref"

twitchQualityWeight = [
	"480p30",
	"360p30",
	"160p30",
	"audio_only",
	"chunked",
	"720p60",
	"720p30"
]