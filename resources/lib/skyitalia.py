# -*- coding: utf-8 -*-
import json, re, datetime, socket
import urllib.request as urllib2
from simplecache import SimpleCache
from . import addonutils


class SkyItalia:
    HOME = 'https://video.sky.it/'
    GET_VIDEO_SEARCH = 'https://video.sky.it/be/getVideoDataSearch?token={token}&section={section}&subsection={subsection}&page={page}&count=30'  # noqa: E501
    GET_PLAYLISTS = 'https://video.sky.it/be/getPlaylistInfo?token={token}&section={section}&subsection={subsection}&start=0&limit=31'  # noqa: E501
    GET_PLAYLIST_VIDEO = 'https://video.sky.it/be/getPlaylistVideoData?token={token}&id={id}'  # noqa: E501
    GET_VIDEO_DATA = 'https://apid.sky.it/vdp/v1/getVideoData?token={token}&caller=sky&rendition=web&id={id}'  # noqa: E501
    TOKEN = 'F96WlOd8yoFmLQgiqv6fNQRvHZcsWk5jDaYnDvhbiJk'
    TIMEOUT = 15
    LOGLEVEL = int(addonutils.getSetting('LogLevel'))
    QUALITY = addonutils.getSetting('Quality')
    QUALITIES = ['web_low_url', 'web_med_url', 'web_high_url', 'web_hd_url']
    LOGOSDIR = '%sresources\\logos\\' % addonutils.PATH_T
    FANART = addonutils.FANART

    def __init__(self):
        socket.setdefaulttimeout(self.TIMEOUT)
        self.cache = SimpleCache()

    def log(self, msg, level=0):
        if level >= self.LOGLEVEL:
            addonutils.log(msg, level)

    def openURL(self, url):
        self.log('openURL, url = %s' % url, 1)
        try:
            cacheresponse = self.cache.get(
                '%s.openURL, url = %s' % (addonutils.NAME, url))
            if not cacheresponse:
                self.log('openURL, no cache found')
                request = urllib2.Request(url)              
                response = urllib2.urlopen(request, timeout=self.TIMEOUT).read()
                self.cache.set(
                    '%s.openURL, url = %s' % (addonutils.NAME, url),
                    response,
                    expiration=datetime.timedelta(days=1))
            return self.cache.get('%s.openURL, url = %s' % (addonutils.NAME, url))
        except Exception as e:
            self.cache = None
            self.log("openURL Failed! " + str(e), 3)
            addonutils.notify(addonutils.LANGUAGE(31000))
            addonutils.endScript()

    def cleanTitle(self, title):
        import html
        title = html.unescape(title)
        title = re.sub(r'^VIDEO:*\s+', '', title)
        return title

    def loadData(self, url):
        self.log('loadData, url = %s' % url, 1)
        response = self.openURL(url)
        if len(response) == 0:
            addonutils.notify(addonutils.LANGUAGE(31000))
            self.log('loadData: "%s" not available' % url, 3)
            return
        response = response.decode('utf-8')

        try:
            # try if the file is json
            items = json.loads(response)
        except:
            # file is html
            self.log('loadData, html page found')
            try:
                # section page, search for subsections
                subs = re.findall(
                    r'menu-entry-sub[^"]*"><a href="%s/(.+?)">(.+?)</a>' % url,
                    response, re.S)
                if len(subs) > 0:
                    self.log('loadData, subsections menu found')
                    return subs

                # search the main menu
                main = re.search(
                    r'"content":([\s\S]+?),\s*"highlights"', response).group(1)
                items = json.loads(main)
                self.log('loadData, main menu found')
            except Exception as e:
                addonutils.notify(addonutils.LANGUAGE(31001))
                self.log('loadJsonData, NO JSON DATA FOUND' + str(e), 3)
                addonutils.endScript()

        return items

    def getAssets(self, data):
        self.log('getAssets, assets = %d' % len(data['assets']), 1)
        for item in data['assets']:
            label = self.cleanTitle(item['title'])
            yield {
                'label': label,
                'params': {
                    'asset_id': item['asset_id']
                },
                'arts': {
                    'thumb': item.get('video_still') or item.get('thumb'),
                    'fanart': self.FANART,
                },
                'videoInfo': {
                    'mediatype': 'video',
                    'title': label,
                },
                'isPlayable': True,
            }

    def getMainMenu(self):
        self.log('getMainMenu, items = %d' % len(self.HOME), 1)
        menu = self.loadData(self.HOME)
        for item in menu:
            # yield only active menu elements
            if menu[item]['active'] == 'Y':
                section = item.strip('/')
                yield {
                    'label': menu[item]['label'],
                    'params': {
                        'section': section
                    },
                    'arts': {
                        'icon': '%s%s.png' % (self.LOGOSDIR, section),
                        'fanart': self.FANART,
                    },
                }
    
    def getSection(self, section):
        self.log('getSection, section = %s' % section, 1)
        subsections = self.loadData('%s%s' % (self.HOME, section))
        for s, t in subsections:
            label = self.cleanTitle(t)
            yield {
                'label': label,
                'params': {
                    'section': section,
                    'subsection': s,
                    'title': label,
                },
                'arts': {
                    'icon': '%s%s\\%s.png' % (
                        self.LOGOSDIR, section, s),
                    'fanart': self.FANART,
                },
            }

    def getSubSection(self, section, subsection, title, page=0):
        self.log('getSubSection, section/subsection = %s/%s' % (section, subsection), 1)
        yield {
            'label': addonutils.LANGUAGE(32001) % title,
            'params': {
                'section': section,
                'subsection': subsection,
                'playlist': title,
            },
            'arts': {
                'icon': '%s%s\\%s.png' % (
                    self.LOGOSDIR, section, subsection),
                'fanart': self.FANART,
            },
        }

        url = self.GET_VIDEO_SEARCH
        url = url.replace('{token}', self.TOKEN)
        url = url.replace('{section}', section)
        url = url.replace('{subsection}', subsection)
        url = url.replace('{page}', str(page))
        data = self.loadData(url)
        yield from self.getAssets(data)

    def getPlaylists(self, section, subsection):
        self.log('getPlaylists, section/subsection = %s/%s' % (section, subsection), 1)
        url = self.GET_PLAYLISTS
        url = url.replace('{token}', self.TOKEN)
        url = url.replace('{section}', section)
        url = url.replace('{subsection}', subsection)
        data = self.loadData(url)

        for item in data:
            yield {
                'label': self.cleanTitle(item['title']),
                'params': {
                    'playlist_id': item['playlist_id'],
                },
                'arts': {
                    'thumb': item['thumb'],
                    'fanart': self.FANART,
                },
            }

    def getPlaylistContent(self, playlist_id):
        self.log('getPlaylistContent, playlist_id = %s' % playlist_id, 1)
        url = self.GET_PLAYLIST_VIDEO
        url = url.replace('{token}', self.TOKEN)
        url = url.replace('{id}', playlist_id)
        data = self.loadData(url)
        yield from self.getAssets(data)

    def getVideo(self, asset_id):
        self.log('getVideo, asset_id = %s' % asset_id, 1)
        url = self.GET_VIDEO_DATA
        url = url.replace('{token}', self.TOKEN)
        url = url.replace('{id}', asset_id)
        data = self.loadData(url)

        url = None
        self.log('getPlaylistContent, quality_selected = %s' % self.QUALITIES[int(self.QUALITY)])
        for i in range(int(self.QUALITY), 0, -1):
            if self.QUALITIES[i] in data:
                self.log('getPlaylistContent, quality_found = %s' % self.QUALITIES[i])
                url = data[self.QUALITIES[i]]
                break

        return url
