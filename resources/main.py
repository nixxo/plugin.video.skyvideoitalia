# -*- coding: utf-8 -*-
from resources.lib.skyitalia import SkyItalia
from phate89lib import kodiutils, staticutils


class SkyVideoItalia(object):

    def __init__(self):
        self.skyit = SkyItalia()
        self.skyit.log = kodiutils.log
        self.logosdir = '%sresources\\logos\\' % kodiutils.PATH

    def addPlayItems(self, items):
        for item in items:
            kodiutils.addListItem(
                self.skyit.clean_title(item['title']),
                {'asset_id': item['asset_id']},
                videoInfo={'mediatype': 'video'},
                arts={'thumb': item['video_still']}, isFolder=False)        

    def main(self):
        params = staticutils.getParams()
        if 'asset_id' in params:
            # PLAY VIDEO
            url = self.skyit.get_video(params['asset_id'])
            if url:
                kodiutils.log('Media URL:  %s' % url)
                kodiutils.setResolvedUrl(url)
            else:
                kodiutils.setResolvedUrl(solved=False)

        elif 'playlist_id' in params:
            # PLAYLIST CONTENT
            playlist_content = self.skyit.get_playlist_content(params['playlist_id'])
            self.addPlayItems(playlist_content)

        elif all(x in params for x in ['playlist', 'section', 'subsection']):
            # PLAYLIST SECTION
            playlist = self.skyit.get_playlist(
                params['section'], params['subsection'])
            for item in playlist:
                kodiutils.addListItem(
                    self.skyit.clean_title(item['title']),
                    {'playlist_id': item['playlist_id']},
                    arts={'thumb': item['thumb']}, isFolder=True)

        elif all(x in params for x in ['title', 'section', 'subsection']):
            # SUBSECTION MENU
            subsection_content = self.skyit.get_subsection(
                params['section'], params['subsection'])
            thumb = '%s%s\\%s.png' % (
                self.logosdir, params['section'], params['subsection'])
            kodiutils.addListItem(
                'Playlist di %s' % params['title'],
                {'section': params['section'],
                 'subsection': params['subsection'],
                 'playlist': params['title']},
                arts={"thumb": thumb}, isFolder=True)
            self.addPlayItems(subsection_content)

        elif 'section' in params:
            # SECTION MENU
            section_content = self.skyit.get_section(params['section'])
            for item in section_content:
                title = self.skyit.clean_title(item['label'])
                thumb = '%s%s\\%s.png' % (
                    self.logosdir, params['section'], item['link'])
                kodiutils.addListItem(
                    self.skyit.clean_title(item['label']),
                    {'section': params['section'],
                     'subsection': item['link'],
                     'title': title},
                    arts={'thumb': thumb}, isFolder=True)

        else:
            # MAIN MENU
            menu = self.skyit.get_main()
            for item in menu:
                section = item['link'].strip('/')
                thumb = '%s%s.png' % (self.logosdir, section)
                kodiutils.addListItem(
                    item['label'], {'section': section},
                    arts={'thumb': thumb}, isFolder=True)
        kodiutils.endScript()
