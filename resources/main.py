# -*- coding: utf-8 -*-
from resources.lib.skyitalia import SkyItalia
from phate89lib import kodiutils, staticutils


class SkyVideoItalia(object):

    def __init__(self):
        self.skyit = SkyItalia()

    def addItems(self, items):
        for item in items:
            kodiutils.addListItem(
                label=item.get('label'),
                params=item.get('params'),
                videoInfo=item.get('videoInfo'),
                arts=item.get('arts'),
                isFolder=False if item.get('isPlayable') else True,
            )

    def main(self):
        params = staticutils.getParams()
        if 'asset_id' in params:
            # PLAY VIDEO
            url = self.skyit.getVideo(params['asset_id'])
            if url:
                self.skyit.log('Media URL:  %s' % url)
                kodiutils.setResolvedUrl(url)
            else:
                kodiutils.setResolvedUrl(solved=False)

        elif 'playlist_id' in params:
            # PLAYLIST CONTENT
            playlist_content = self.skyit.getPlaylistContent(params['playlist_id'])
            self.addItems(playlist_content)

        elif all(x in params for x in ['playlist', 'section', 'subsection']):
            # PLAYLIST SECTION
            playlist = self.skyit.getPlaylists(
                params['section'], params['subsection'])
            self.addItems(playlist)

        elif all(x in params for x in ['title', 'section', 'subsection']):
            # SUBSECTION MENU
            subsection_content = self.skyit.getSubSection(
                params['section'], params['subsection'], params['title'])
            self.addItems(subsection_content)

        elif 'section' in params:
            # SECTION MENU
            section_content = self.skyit.getSection(params['section'])
            self.addItems(section_content)

        else:
            # MAIN MENU
            menu = self.skyit.getMainMenu()
            self.addItems(menu)

        kodiutils.endScript()
