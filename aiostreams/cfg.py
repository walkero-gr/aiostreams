# Configuration
# At this file you can change the behaviour of the scripts, by setting
# various parameteres, and most important the preferred video players
#

# Set this to True to enable autoplay of the video with your preffered video player. Set it to False to disable it.
autoplay = True

# Set this to True to get more info from the script during the execution. Set it to False to disable it.
verbose = False

# Set the path to your preffered video player. This is going to be used on recorded streams only. 
# This is used only if autoplay is set to True.
vPlayer = "APPDIR:mplayer"
# Set the arguments that are going to be used with your preffered video player.
vPlayerArgs = "-quiet -really-quiet -forceidx -framedrop -cache 8192"

# Set the path to your preffered video player. This is going to be used mostly on live streams, 
# but depending the network, might be used on recorder streams as well.
# This is used only if autoplay is set to True.
sPlayer = "APPDIR:ffplay"
# Set the arguments that are going to be used with your preffered streaming player.
sPlayerArgs = "-loglevel quiet -infbuf -skip_loop_filter all -skip_frame noref"
