# -*- coding: utf-8 -*-
import json, re
import urllib.request as urllib2


class SkyItalia:
    HOME = 'https://video.sky.it/'
    GET_VIDEO_SEARCH = 'https://video.sky.it/be/getVideoDataSearch?token={token}&section={section}&subsection={subsection}&page={page}&count=30'  # noqa: E501
    GET_PLAYLISTS = 'https://video.sky.it/be/getPlaylistInfo?token={token}&section={section}&subsection={subsection}&start=0&limit=31'  # noqa: E501
    GET_PLAYLIST_VIDEO = 'https://video.sky.it/be/getPlaylistVideoData?token={token}&id={id}'  # noqa: E501
    GET_VIDEO_DATA = 'https://apid.sky.it/vdp/v1/getVideoData?token={token}&caller=sky&rendition=web&id={id}'  # noqa: E501
    GET_VOD_ACCESS_TOKEN = 'https://apid.sky.it/vdp/v1/getVodAccessToken?token={token}&url={url}&dec=0'  # noqa: E501
    TOKEN = 'F96WlOd8yoFmLQgiqv6fNQRvHZcsWk5jDaYnDvhbiJk'

    def __init__(self):
        opener = urllib2.build_opener()
        urllib2.install_opener(opener)

    def clean_title(self, title):
        import html
        title = html.unescape(title)
        title = re.sub('^VIDEO:* ', '', title)
        return title

    def get_main(self):
        try:
            page = urllib2.urlopen(self.HOME).read().decode('utf-8')
        except :
            self.log('get_main error: "%s" not available' % self.HOME)
            return
        m = re.search('"content":([\\s\\S]+?),\\s*"highlights"', page, re.S)
        if not m:
            self.log('get_main error: JSON not found in webpage')
            return
        try:
            menu = json.loads(m.group(1))
            clean_menu = []
            # remove deactivated menu items
            for item in menu:
                if menu[item]['active'] == 'Y':
                    clean_menu.append(menu[item])
        except :
            self.log('get_main error: JSON decode error')
            return
        return clean_menu
    
    def get_section(self, section):
        try:
            url = '%s%s' % (self.HOME, section)
            page = urllib2.urlopen(url).read().decode('utf-8')
        except :
            self.log('get_section error with section: "%s"' % section)
            return

        section = []
        for match in re.finditer(
                'menu-entry-sub[^"]*"><a href="%s/(.+?)">(.+?)</a>' % url,
                page, re.S):
            section.append({
                'link': match[1],
                'label': match[2],
                })
        return section

    def get_subsection(self, section, subsection, page=0):
        url = self.GET_VIDEO_SEARCH
        url = url.replace('{token}', self.TOKEN)
        url = url.replace('{section}', section)
        url = url.replace('{subsection}', subsection)
        url = url.replace('{page}', str(page))
        try:
            subsection = json.loads(urllib2.urlopen(url).read().decode('utf-8'))
        except :
            self.log('get_subsection error with sec/subsec: "%s/%s"' % [section, subsection])
            return
        return subsection['assets']

    def get_playlist(self, section, subsection):
        # web_pdb.set_trace()
        url = self.GET_PLAYLISTS
        url = url.replace('{token}', self.TOKEN)
        url = url.replace('{section}', section)
        url = url.replace('{subsection}', subsection)
        try:
            playlist = json.loads(urllib2.urlopen(url).read().decode('utf-8'))
        except :
            self.log('get_playlist error with sec/subsec: "%s/%s"' % [section, subsection])
            return
        return playlist

    def get_playlist_content(self, playlist_id):
        url = self.GET_PLAYLIST_VIDEO
        url = url.replace('{token}', self.TOKEN)
        url = url.replace('{id}', playlist_id)
        try:
            playlist = json.loads(urllib2.urlopen(url).read().decode('utf-8'))
        except :
            self.log('get_playlist_content with playlist_id: "%s"' % playlist_id)
            return
        return playlist['assets']

    def get_access_token_url(self, url, token):
        url = self.GET_VOD_ACCESS_TOKEN
        url = url.replace('{token}', token)
        url = url.replace('{url}', url)
        try:
            video = json.loads(urllib2.urlopen(url).read().decode('utf-8'))
        except :
            self.log('get_access_token_url error with url: "%s" and token: "%s"' % [url, token])
            return
        return video['url']

    def get_video(self, asset_id):
        url = self.GET_VIDEO_DATA
        url = url.replace('{token}', self.TOKEN)
        url = url.replace('{id}', asset_id)
        try:
            video = json.loads(urllib2.urlopen(url).read().decode('utf-8'))
        except :
            self.log('get_video error with asset_id: "%s"' % asset_id)
            return

        url = video.get('web_hd_url')
        if not url:
            url = video.get('web_high_url')
        if not url:
            url = video.get('web_med_url')
        if not url:
            url = video.get('web_low_url')

        return url
