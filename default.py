import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

import urllib.parse as urlparse
from urllib.parse import urlencode

from resources.lib.skyitalia import SkyItalia

import web_pdb

addonid = 'plugin.video.skyvideoitalia'
addon = xbmcaddon.Addon(id=addonid)
# addonname = addon.getAddonInfo('name')
addondir = xbmcvfs.translatePath(addon.getAddonInfo('path')) 
logosdir = '%sresources\\logos\\' % addondir


def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = dict(urlparse.parse_qsl(parameters[1:]))
    return paramDict


def addDirectoryItem(parameters, li):
    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(
        handle=handle, url=url, listitem=li, isFolder=True)


def addLinkItem(parameters, li, url=''):
    if url == '':
        url = sys.argv[0] + '?' + urlencode(parameters)
    li.setProperty('IsPlayable', 'true')
    return xbmcplugin.addDirectoryItem(
        handle=handle, url=url, listitem=li, isFolder=False)


def addPlayItems(items):
    for item in items:
        title = skyit.clean_title(item['title'])
        liStyle = xbmcgui.ListItem(title)
        liStyle.setArt({"thumb": item['video_still']})
        liStyle.setInfo("video", {})
        addLinkItem({
            'asset_id': item['asset_id'],
            }, liStyle)


handle = int(sys.argv[1])
params = parameters_string_to_dict(sys.argv[2])
skyit = SkyItalia()
section = str(params.get('section', ''))
subsection = str(params.get('subsection', ''))
playlist = str(params.get('playlist', ''))
title = str(params.get('title', ''))
playlist_id = str(params.get('playlist_id', ''))
asset_id = str(params.get('asset_id', ''))

if asset_id != '':
    # PLAY VIDEO
    url = skyit.get_video(asset_id)
    xbmc.log('Media URL:  %s' % url)
    item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=item)

elif playlist_id != '':
    # PLAYLIST CONTENT
    playlist = skyit.get_playlist_content(playlist_id)
    addPlayItems(playlist)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)  

elif playlist != '' and subsection != '' and section != '':
    # PLAYLIST SECTION
    playlist = skyit.get_playlist(section, subsection)
    for item in playlist:
        title = skyit.clean_title(item['title'])
        liStyle = xbmcgui.ListItem(title)
        liStyle.setArt({"thumb": item['thumb']})
        addDirectoryItem({
            'playlist_id': item['playlist_id'],
            }, liStyle)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)  

elif title != '' and subsection != '' and section != '':
    # SUBSECTION MENU
    menu = skyit.get_subsection(section, subsection)
    # web_pdb.set_trace()
    thumb = '%s%s\\%s.png' % (logosdir, section, subsection)
    liStyle = xbmcgui.ListItem('Playlist di %s' % title)
    liStyle.setArt({"thumb": thumb})
    addDirectoryItem({
        'section': section,
        'subsection': subsection,
        'playlist': title,
        }, liStyle)
    addPlayItems(menu)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)  

elif section != '':
    # SECTION MENU
    menu = skyit.get_section(section)
    # web_pdb.set_trace()
    for item in menu:
        thumb = '%s%s\\%s.png' % (logosdir, section, item['link'])
        title = skyit.clean_title(item['label'])
        liStyle = xbmcgui.ListItem(title)
        # liStyle = xbmcgui.ListItem('%s - %s' % (title, item['link']))
        liStyle.setArt({"thumb": thumb})
        addDirectoryItem({
            'section': section,
            'subsection': item['link'],
            'title': title,
            }, liStyle)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

else:
    # MAIN MENU
    menu = skyit.get_main()
    # web_pdb.set_trace()
    for item in menu:
        section = item['link'].strip('/')
        thumb = '%s%s.png' % (logosdir, section)
        liStyle = xbmcgui.ListItem(item['label'])
        # liStyle = xbmcgui.ListItem('%s - %s' % (item['label'], section))
        liStyle.setArt({"thumb": thumb})
        addDirectoryItem({'section': section}, liStyle)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
