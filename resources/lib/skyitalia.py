# -*- coding: utf-8 -*-
import json, re, datetime, socket
import xbmc
import urllib.request as urllib2
from simplecache import SimpleCache
from phate89lib import kodiutils


class SkyItalia:
    HOME = 'https://video.sky.it/'
    GET_VIDEO_SEARCH = 'https://video.sky.it/be/getVideoDataSearch?token={token}&section={section}&subsection={subsection}&page={page}&count=30'  # noqa: E501
    GET_PLAYLISTS = 'https://video.sky.it/be/getPlaylistInfo?token={token}&section={section}&subsection={subsection}&start=0&limit=31'  # noqa: E501
    GET_PLAYLIST_VIDEO = 'https://video.sky.it/be/getPlaylistVideoData?token={token}&id={id}'  # noqa: E501
    GET_VIDEO_DATA = 'https://apid.sky.it/vdp/v1/getVideoData?token={token}&caller=sky&rendition=web&id={id}'  # noqa: E501
    TOKEN = 'F96WlOd8yoFmLQgiqv6fNQRvHZcsWk5jDaYnDvhbiJk'
    TIMEOUT = 15
    DEBUG = kodiutils.getSetting('Debug') == 'true'
    QUALITY = kodiutils.getSetting('Quality')
    QUALITIES = ['web_low_url', 'web_med_url', 'web_high_url', 'web_hd_url']
    LOGOSDIR = '%sresources\\logos\\' % kodiutils.PATH_T
    FANART = '%sresources\\fanart.png' % kodiutils.PATH_T

    def __init__(self):
        socket.setdefaulttimeout(self.TIMEOUT)
        self.cache = SimpleCache()

    def log(self, msg, level=xbmc.LOGDEBUG):
        import traceback
        if self.DEBUG is False and level != xbmc.LOGERROR:
            return
        if level == xbmc.LOGERROR:
            msg += ' ,' + traceback.format_exc()
        xbmc.log('%s - %s - %s' % (kodiutils.ID, kodiutils.VERSION, msg), level)

    def openURL(self, url):
        self.log('openURL, url = %s' % url)
        try:
            cacheresponse = self.cache.get(
                '%s.openURL, url = %s' % (kodiutils.NAME, url))
            if not cacheresponse:
                request = urllib2.Request(url)              
                response = urllib2.urlopen(request, timeout=self.TIMEOUT).read()
                self.cache.set(
                    '%s.openURL, url = %s' % (kodiutils.NAME, url),
                    response,
                    expiration=datetime.timedelta(days=1))
            return self.cache.get('%s.openURL, url = %s' % (kodiutils.NAME, url))
        except Exception as e:
            self.log("openURL Failed! " + str(e), xbmc.LOGERROR)
            kodiutils.notify(kodiutils.LANGUAGE(31000))
            kodiutils.endScript()

    def cleanTitle(self, title):
        import html
        title = html.unescape(title)
        title = re.sub(r'^VIDEO:*\s+', '', title)
        return title

    def loadData(self, url):
        self.log('loadData, url = %s' % url)
        response = self.openURL(url)
        if len(response) == 0:
            kodiutils.notify(kodiutils.LANGUAGE(31000))
            self.log('loadData: "%s" not available' % url, xbmc.LOGERROR)
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
                kodiutils.notify(kodiutils.LANGUAGE(31001))
                self.log('loadJsonData, NO JSON DATA FOUND' + str(e), xbmc.LOGERROR)
                kodiutils.endScript()

        return items

    def getAssets(self, data):
        self.log('%d assets found' % len(data['assets']))
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
        yield {
            'label': kodiutils.LANGUAGE(32001) % title,
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
        url = self.GET_PLAYLIST_VIDEO
        url = url.replace('{token}', self.TOKEN)
        url = url.replace('{id}', playlist_id)
        data = self.loadData(url)
        yield from self.getAssets(data)

    def getVideo(self, asset_id):
        url = self.GET_VIDEO_DATA
        url = url.replace('{token}', self.TOKEN)
        url = url.replace('{id}', asset_id)
        data = self.loadData(url)

        url = None
        for i in range(int(self.QUALITY), 0, -1):
            if self.QUALITIES[i] in data:
                url = data[self.QUALITIES[i]]
                break

        return url
