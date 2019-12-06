# Video Quality Weights (vqw)
# At this file you can set the weighted order of the quality
# of the streams you prefer. This means that the first available will be served.
#

twitchVQW = [
    "480p30",
    "360p30",
    "160p30",
    "720p60",
    "720p30",
    "chunked",
    "audio_only"
]

mixerVQW = [
    "480p",
    "320p",
    "160p",
    "720p",
    "1080p"
]

vimeoVQW = [
    "360p",
    "240p",
    "480p",
    "540p",
    "720p",
    "1080p"
]

dailymotionVQW = [
    "480",
    "380",
    "240",
    "144",
    "720",
    "1080"
]

ytVQW = [
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

ytLiveVQW = [
    480,		# 480p mp4
    360,		# 360p mp4
    240,		# 240p mp4
    144,		# 144p mp4
    720,		# 720p mp4
    1080		# 1080p mp4
]

dliveVQW = [
    "480p",
    "360p",
    "720p",
    "src"
]

peertubeVQW = [
    "480p",
    "360p",
    "240p",
    "720p",
    "768p",
    "1080p"
]

wasdVQW = [
    "480",
    "360",
    "240",
    "144",
    "720",
    "900",
    "1080",
    "1200"
]