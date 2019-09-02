# aiostreams
All In One streams (aiostreams) is a pack of scripts, written in Python, that can be used to stream and watch videos from different online networks, like Twitch.tv and Mixer.com.

These can be used from the shell, as well as from any web browser that support execution of scripts. It is really easy to configure a link context menu and open the URL with the script. And if "Autoplay" is enabled, then the video will start automatically.

Some of these networks support search, where you can find available streams and videos.

The scripts are based on Python v2.5, so this is absolutely necessary to be installed at your system.

They are developed and fully tested under AmigaOS 4.1 FE. There will be support for other systems in the future, like MorphOS, AmigaOS 3 and AROS, as long as Python is supported. 

The scripts might work under Linux and MacOS X, but those systems are not the target of this project. There are other solution that might work better.

A full list:
* Python 2.5
* [Pythonssl][1]
* The Python modules: urllib, urllib2, sys, re, string, random. Usually they are part of the python Installation
* [ffplay][2] for the online live streaming videos, or something equivalent
* [mplayer][3] for the online recorded videos, or something equivalent
* internet access

#### Docker
To run the script in a docker container with Python 2.7 installed, use the following on different shells, from the script folder.

```bash
docker run -it --rm --name aiostreams -v "$PWD":/usr/src/myapp -w /usr/src/myapp python:2
```
```bash
docker exec -it aiostreams bash
python twitch.py
```

[1]: http://os4depot.net/?function=showfile&file=library/misc/pythonssl.lha
[2]: http://os4depot.net/?function=showfile&file=video/convert/ffmpeg.lha
[3]: http://os4depot.net/index.php?function=search&tool=simple&f_fields=mplayer
[blog]: https://walkero.gr