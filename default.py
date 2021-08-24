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


handle = int(sys.argv[1])
params = parameters_string_to_dict(sys.argv[2])
skyit = SkyItalia()
section = str(params.get('section', ''))
subsection = str(params.get('subsection', ''))
asset_id = str(params.get('asset_id', ''))

if asset_id != '':
    # PLAY VIDEO
    # web_pdb.set_trace()
    xbmc.log('Media asset_id: %s' % asset_id)
    url = skyit.get_video(asset_id)
    xbmc.log('Media URL:  %s' % url)
    item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=item)

elif subsection != '' and section != '':
    # SUBSECTION MENU
    menu = skyit.get_subsection(section, subsection)
    # web_pdb.set_trace()
    for item in menu:
        title = skyit.clean_title(item['title'])
        liStyle = xbmcgui.ListItem(title)
        liStyle.setArt({"thumb": item['video_still']})
        liStyle.setInfo("video", {})
        addLinkItem({
            'asset_id': item['asset_id']},
            liStyle)
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
            'subsection': item['link']},
            liStyle)
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
