
[![ko-fi](https://img.shields.io/badge/Buy%20me%20a%20Ko--fi-F16061?style=flat&logo=ko-fi&logoColor=white)](https://ko-fi.com/walkero)

# aiostreams
All In One streams (aiostreams) is a pack of scripts, written in Python, that can be used to stream and watch videos from different online networks, like Twitch.tv and Lbry.tv.

All the scripts should be used from the shell, as well as from any web browser that support execution of scripts. It is really easy to configure a link context menu and open the URL with the script. And if "Autoplay" is enabled, then the video will start automatically using the configured default players.

Some of these networks have a search API, and you can use them to find available streams and videos, without the need to visit the website. This is a fast way to find what you want, without waiting huge amount of Javascript to be executed on your machine. Especially useful when your computer doesn't have the necessary horse power to support those websites.

All the scripts are developed and fully tested under AmigaOS 4.1 FE and MorphOS 3.x. There will be support for other systems in the future, like AmigaOS 3 and AROS, as long as Python is supported. The scripts work just fine under Linux and MacOS X, but those systems are not the target of this project. There are other solutions that might do a better job.

### Supported networks:
* [Twitch.tv](https://www.twitch.tv/)
* [YouTube.com](https://youtube.com/)
* [Vimeo.com](https://vimeo.com/)
* [Dailymotion.com](https://www.dailymotion.com)
* [Skaitv.gr](http://www.skaitv.gr/)
* [Dlive.tv](https://dlive.tv/)
* [PeerTube](https://joinpeertube.org/)
* [Wasd.tv](https://wasd.tv/)
* [Lbry.tv](https://lbry.tv/)

### A full list of requirements per OS:
#### AmigaOS 4.1
* [AmigaOS 4.1 FE upd1][amigaos]
* Python 2.5
* [Pythonssl][pythonssl]
* The Python modules: urllib, urllib2, sys, re, string, random. Usually they are part of the python Installation
* [ffplay][ffmpeg], [mplayer][mplayer], [emotion][emotion] for the live and recorded video playback or something equivalent
* Internet access

#### MorphOS 3.x
* MorphOS 3.10 and above
* Python 2.5 and above
* Suitable video player that can support video streaming
* Internet access

Help me persuade my wife that what I am doing matters
-----------------------------------------------------------
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/walkero)

### Docker for development
This is not necessary for using these scripts. It just provides a good development environment for other systems.
To run the script in a docker container with Python 2.7 installed, use the following on different shells, from the script folder.

```bash
docker run -it --rm --name aiostreams -v "$PWD":/usr/src/myapp -w /usr/src/myapp python:2
```
```bash
docker exec -it aiostreams bash
python twitch.py
```

[pythonssl]: http://os4depot.net/?function=showfile&file=library/misc/pythonssl.lha
[ffmpeg]: http://os4depot.net/?function=showfile&file=video/convert/ffmpeg.lha
[mplayer]: http://os4depot.net/index.php?function=search&tool=simple&f_fields=mplayer
[emotion]: https://entwickler-x.de/emotion
[amigaos]: http://amigaos.net
[blog]: https://walkero.gr