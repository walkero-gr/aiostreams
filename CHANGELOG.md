# Changelog
All notable changes to this project will be documented in this file.

## [VERSION_TAG] - RELEASE_DATE

## [v1.7.7] - 2023-12-20

### Added
- The youtube script supports now the urls of shorts videos
- Added video resolutions at the youtube script, when the `-x` argument is used
- Added more resolutions selection in the `vqw.py` for Vimeo and twitch

### Changed
- The youtube script supports more urls, to cover more Invidious servers

## [1.7.6] - 2022-12-04

### Added
- Added some extra info in the amigaguide file for the youtube script
- Added pagination to youtube script with the new argument -p/--page

### Changed
- Updated the scripts to work with python3
- Now the -x argument in youtube and twitch script prints out the extra info but
  doesn't start the video playback

### Removed
- Removed the skaitv, lbry and dlive scripts as they are not working and they
  need a rewrite

## [1.7.5] - 2022-08-23

### Added
- Added -sc argument to the youtube script which can be used to search for
  YouTube channels based on the given description. This returns a list of
  channels titles and their feed URLs
- Added support for https://yewtu.be invidious server in YouTube script

### Fixed
- Fixed dlive script
- Fixed peertube script
- Fixed lbrytv script to support odysee.com videos as well
- Fixed vimeo script
  
## [1.7.4] - 2022-07-26

### Fixed
- Did a fix in YouTube script to avoid SB videos. This was breaking the video selection
- Fixed the video throttle in YouTube videos. So now the videos seem to play smoothly

## [1.7.3] - 2022-02-14

### Added
- Added a new argument on Youtube script, the -x, that enables extra info on search results and videos

### Changed
- Updated the Twitch script to use AIO API to get all the data. AIO API works with the latest Twitch API

## [1.7.2] - 2021-10-13

### Fixed
- A lot of changes to make YouTube work again. There were changes to vqw.py file, so first backup the one you use

## [1.7.1] - 2021-03-19

### Added
- Added radio.py script

### Changed
- Changes on skaitv script to use aiostreams api site

## [1.7] - 2021-01-15

### Fixed
- Fixed skaitv live script

### Removed
- Removed Mixer.com script as it shut down

## [1.6.2] - 2020-07-27

### Added
- Added automated release process to OS4Depot and Aminet

## [1.6.1] - 2020-07-15

### Fixed
- Fixed Lbry.tv under AmigaOS 4 to use ffplay and not mplayer on video playback

## [1.6] - 2020-07-13

### Added
- Lbry.tv script added

### Changed
- Cleared unused variables from scripts

### Fixed
- Fixed Vimeo script to support Videos with GUID

## [1.5] - 2020-01-01

### Added
- Wasd.tv script added
- PeerTube script added
- Added a full changelog file

### Changed
- Changed the place of the video qualities lists by separating them from the configuration file to a new file named vqw.py
- Changed the scripts' descriptions on help request

### Fixed
- Fixed skaitv.py script to support the latest changes of the website

## [1.4.2] - 2019-11-14

### Changed
- Twitch script uses Twitch API v5
- Twitch script uses aiostreams API as a workaround fix of streams that were not working before because of unicode channel names.

## [1.4.1] - 2019-10-09

### Changed
- Changes on dlive script to support AmigaOS 4 and MorphOS. Now you can watch streams and videos on your beloved systems
- A change on twitch script to be usable with Emotion player under AmigaOS 4

## [1.4] - 2019-09-30

### Added
- Dlive.tv script added. (Not working under AmigaOS 4 because of some SSL handshake error)
- MorphOS 3.x, MacOS X and Linux systems are now supported with autoplay

### Changed
- Various fixes

## [1.3] - 2019-09-20

### Added
- YouTube.com script added

### Changed
- If the running system is not AmigaOS 4, the returned texts show unicode characters. Otherwise they are stripped
- Skaitv.gr script updated to support some archived videos and live stream
- Fixed a config file bug
- Fixed a bug in Twitch script
  ```
    File "twitch.py", line 192, in getPrefferedVideoURL
    if (quality == playlists[idx]['video']):
  ```

## [1.2] - 2019-09-04

### Added
- Vimeo.com script added
- Dailymotion.com script added
- Skaitv.gr script added
- Added links in the AmigaGuide file, that use URLOpen
- Added the silence parameter, that prevents the script to output anything, except the errors or the results of a search
- Added Top Games list in twitch.py script. This returns the 50 Top Games based on the number of viewers.
- Added Top Streams list in twitch.py script. This returns the 50 Top Streams based on the number of viewers.

### Changed
- simplem3u8 parser updated to support URLs starting with "../"
- Documentation updated
- Increased game search results list to 50 items in twitch.py script.

### Removed
- Removed version per script

## [1.1] - 2019-08-26

### Added
- Mixer.com script added

### Changed
- Cleared a lot of code in twitch.py script
- Documentation updated

## [1.0] - 2019-08-23

### Added
- Initial release
- Twitch.tv script added
- Simple m3u8 parser created





The format of this changelog file is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
