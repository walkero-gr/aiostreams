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
    22,			# 720p, mp4, audio quality medium
    43,			# 360p, mp4, audio quality medium
    18,			# 360p, mp4, audio quality low
    135,		# 480p, mp4, no audio
    91,         # 144p, avc1.42c00b, mp4a.40.5
    92,         # 240p, avc1.4d4015, mp4a.40.5
    93,         # 360p, avc1.4d401e, mp4a.40.2
    94,         # 480p, avc1.4d401f, mp4a.40.2
    95,         # 720p, avc1.4d401f, mp4a.40.2
    96,         # 1080p, avc1.640028, mp4a.40.2
    # 244,		# 480p, webm, no audio
    # 134,		# 360p, mp4, no audio
    # 243,		# 360p, webm, no audio
    # 133,		# 240p, mp4, no audio
    # 242,		# 240p, webm, no audio
    # 160,		# 144p, mp4, no audio
    # 278,		# 144p, webm, no audio
    # 136,		# 720p, mp4, no audio
    # 247,		# 720p, webm, no audio
    # 137,		# 1080p, mp4, no audio
    # 248,		# 1080p, webm, no audio
    # 140,		# mp4, audio only, 44100, medium
    # 249,		# webm, audio only, 48000, low
    # 250,		# webm, audio only, 48000, low
    # 251,		# webm, audio only, 48000, medium
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

skaiVQW = [
    "2000K",
    "1200K",
    "600K"
]
