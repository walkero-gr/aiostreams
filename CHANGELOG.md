# Changelog
All notable changes to this project will be documented in this file.


## [unreleased]
### Added

### Changed

### Fixed


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