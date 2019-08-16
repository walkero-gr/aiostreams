# aiostreams
All In One streams is a pack of Python scripts that help users to stream video from various sources on AmigaOS 4.1 systems.

Currently there is only a script for Twitch.tv but more will be added in the future.


#### Docker
To run the script in a docker container with Python 2.7 installed, use the following on different shells, from the script folder.

```bash
docker run -it --rm --name aiostreams -v "$PWD":/usr/src/myapp -w /usr/src/myapp python:2
```
```bash
docker exec -it aiostreams bash
python twitch.py
```