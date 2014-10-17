#!/usr/bin/env python

"""
Sources:

ElementTree
http://docs.python.org/2/library/xml.etree.elementtree.html#xml.etree.ElementTree.SubElement

trailers.apple.com root URL
http://trailers.apple.com/appletv/us/js/application.js
navigation pane
http://trailers.apple.com/appletv/us/nav.xml
->top trailers: http://trailers.apple.com/appletv/us/index.xml
->calendar:     http://trailers.apple.com/appletv/us/calendar.xml
->browse:       http://trailers.apple.com/appletv/us/browse.xml
"""

import re
import os
import sys
import traceback
import inspect 
import string, random
import copy  # deepcopy()

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import time, uuid, hmac, hashlib, base64
from urllib import quote_plus, unquote_plus
import urllib2
import urlparse

from Version import __VERSION__  # for {{EVAL()}}, display in settings page
import Settings, ATVSettings
import PlexAPI
from Debug import *  # dprint(), prettyXML()
import Localize



g_param = {}
def setParams(param):
    global g_param
    g_param = param

g_ATVSettings = None
def setATVSettings(cfg):
    global g_ATVSettings
    g_ATVSettings = cfg



"""
# aTV XML ErrorMessage - hardcoded XML File
"""
def XML_Error(title, desc):
    errorXML = '\
<?xml version="1.0" encoding="UTF-8"?>\n\
<atv>\n\
    <body>\n\
        <dialog id="com.sample.error-dialog">\n\
            <title>' + title + '</title>\n\
            <description>' + desc + '</description>\n\
        </dialog>\n\
    </body>\n\
</atv>\n\
';
    return errorXML



def XML_PlayVideo_ChannelsV1(baseURL, path):
    XML = '\
<atv>\n\
  <body>\n\
    <videoPlayer id="com.sample.video-player">\n\
      <httpFileVideoAsset id="' + path + '">\n\
        <mediaURL>' + baseURL + path + '</mediaURL>\n\
        <title>*title*</title>\n\
        <!--bookmarkTime>{{EVAL(int({{VAL(Video/viewOffset:0)}}/1000))}}</bookmarkTime-->\n\
        <videoPlayerSettings>\n\
          <!-- PMS, OSD settings, ... -->\n\
          <baseURL>' + baseURL + '</baseURL>\n\
          <accessToken></accessToken>\n\
          <showClock>False</showClock>\n\
          <timeFormat></timeFormat>\n\
          <clockPosition></clockPosition>\n\
          <overscanAdjust></overscanAdjust>\n\
          <showEndtime>False</showEndtime>\n\
          <subtitleSize></subtitleSize>\n\
        </videoPlayerSettings>\n\
        <myMetadata>\n\
          <key></key>\n\
          <ratingKey></ratingKey>\n\
          <duration></duration>\n\
          <subtitleURL></subtitleURL>\n\
        </myMetadata>\n\
      </httpFileVideoAsset>\n\
    </videoPlayer>\n\
  </body>\n\
</atv>\n\
';
    dprint(__name__,2 , XML)
    return XML



"""
global list of known aTVs - to look up UDID by IP if needed

parameters:
    udid - from options['PlexConnectUDID']
    ip - from client_address btw options['aTVAddress']
"""
g_ATVList = {}

def declareATV(udid, ip):
    global g_ATVList
    if udid in g_ATVList:
        g_ATVList[udid]['ip'] = ip
    else:
        g_ATVList[udid] = {'ip': ip}

def getATVFromIP(ip):
    # find aTV by IP, return UDID
    for udid in g_ATVList:
        if ip==g_ATVList[udid].get('ip', None):
            return udid
    return None  # IP not found



"""
# XML converter functions
# - translate aTV request and send to PMS
# - receive reply from PMS
# - select XML template
# - translate to aTV XML
"""
def XML_PMS2aTV(PMS_address, path, options):
    # double check aTV UDID, redo from client IP if needed/possible
    if not 'PlexConnectUDID' in options:
        UDID = getATVFromIP(options['aTVAddress'])
        if UDID:
            options['PlexConnectUDID'] = UDID
        else:
            # aTV unidentified, UDID not known    
            return XML_Error('PlexConnect','Unexpected error - unidentified ATV')
    else:
        declareATV(options['PlexConnectUDID'], options['aTVAddress'])  # update with latest info
    
    UDID = options['PlexConnectUDID']
    
    # determine PMS_uuid, PMSBaseURL from IP (PMS_mark)
    PMS_uuid = PlexAPI.getPMSFromAddress(UDID, PMS_address)
    PMS_baseURL = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'baseURL')
    
    # check cmd to work on
    cmd = ''
    channelsearchURL = ''
    if 'PlexConnect' in options:
        cmd = options['PlexConnect']
    
    if 'PlexConnectChannelsSearch' in options:
        channelsearchURL = options['PlexConnectChannelsSearch'].replace('+amp+', '&')
     
    dprint(__name__, 1, "PlexConnect Cmd: " + cmd)
    dprint(__name__, 1, "PlexConnectChannelsSearch: " + channelsearchURL)
    
    # check aTV language setting
    if not 'aTVLanguage' in options:
        dprint(__name__, 1, "no aTVLanguage - pick en")
        options['aTVLanguage'] = 'en'
    
    # XML Template selector
    # - PlexConnect command
    # - path
    # - PMS ViewGroup
    XMLtemplate = ''
    PMS = None
    PMSroot = None
    template = g_ATVSettings.getSetting(options['PlexConnectUDID'], 'template')

    # XML direct request or
    # XMLtemplate defined by solely PlexConnect Cmd
    if path.endswith(".xml"):
        XMLtemplate = path.lstrip('/')
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='ChannelsSearch':
        if template == "default":
          XMLtemplate = 'ChannelsSearch.xml'
        else:
          XMLtemplate = 'Channel/Search.xml'
        path = ''
    
    elif cmd.startswith('Play:'):
        opt = cmd[len('Play:'):]  # cut command:
        parts = opt.split(':',1)
        if len(parts)==2:
            options['PlexConnectPlayType'] = parts[0]  # Single, Continuous # decoded in PlayVideo.xml, COPY_PLAYLIST
            options['PlexConnectRatingKey'] = parts[1]  # ratingKey # decoded in PlayVideo.xml
        else:
            return XML_Error('PlexConnect','Unexpected "Play" command syntax')
        XMLtemplate = 'PlayVideo.xml'
    
    elif cmd.startswith('PlayAudio'):  # PlayAudio: or PlayAudio_plist:
        parts = cmd.split(':',3)
        if len(parts)==4:
            XMLtemplate = parts[0] + '.xml'
            options['PlexConnectPlayType'] = parts[1]  # Single, Continuous # decoded in PlayAudio.xml
            options['PlexConnectRatingKey'] = parts[2]  # ratingKey
            options['PlexConnectCopyIx'] = parts[3]  # copy_ix
        else:
            return XML_Error('PlexConnect','Unexpected "PlayAudio" command syntax')
    
    elif cmd=='PlayVideo_ChannelsV1':
        dprint(__name__, 1, "playing Channels XML Version 1: {0}".format(path))
        auth_token = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'accesstoken')
        path = PlexAPI.getDirectVideoPath(path, auth_token)
        return XML_PlayVideo_ChannelsV1(PMS_baseURL, path)  # direct link, no PMS XML available
    
    elif cmd=='PlayTrailer':
        trailerID = options['PlexConnectTrailerID']
        info = urllib2.urlopen("http://youtube.com/get_video_info?video_id=" + trailerID).read()
        parsed = urlparse.parse_qs(info)
        
        key = 'url_encoded_fmt_stream_map'
        if not key in parsed:
            return XML_Error('PlexConnect', 'Youtube: No Trailer Info available')
        streams = parsed[key][0].split(',')
        
        url = ''
        for i in range(len(streams)):
            stream = urlparse.parse_qs(streams[i])
            if stream['itag'][0] == '18':
                url = stream['url'][0]
        if url == '':
            return XML_Error('PlexConnect','Youtube: ATV compatible Trailer not available')
        
        return XML_PlayVideo_ChannelsV1('', url.replace('&','&amp;'))

    elif cmd=='Plex_Video_Files_Scanner':
        if template == "default":
          XMLtemplate = 'HomeVideoSectionTopLevel.xml'
        else:
          XMLtemplate = 'HomeVideo/SectionTopLevel.xml'

    elif cmd=='Plex_Movie_Scanner':
        if template == "default":
          XMLtemplate = 'MovieSectionTopLevel.xml'
        else:
          XMLtemplate = 'Movie/SectionTopLevel.xml'
    
    elif cmd=='Plex_Series_Scanner':
        if template == "default":
          XMLtemplate = 'TVSectionTopLevel.xml'
        else:
          XMLtemplate = 'TVShow/SectionTopLevel.xml'
        
    elif cmd=='Plex_Photo_Scanner':
        if template == "default":
          XMLtemplate = 'PhotoSectionTopLevel.xml'
        else:
          XMLtemplate = 'Photo/SectionTopLevel.xml'

    elif cmd=='Plex_Music_Scanner':
        if template == "default":
          XMLtemplate = 'MusicSectionTopLevel.xml'
        else:
          XMLtemplate = 'Music/SectionTopLevel.xml'
    
    elif cmd=='ScrobbleMenu':
        if template == "default":
          XMLtemplate = 'ScrobbleMenu.xml'
        else:
          XMLtemplate = 'ScrobbleMenu/ScrobbleMenu.xml'

    elif cmd=='ScrobbleMenuVideo':
        if template == "default":
          XMLtemplate = 'ScrobbleMenuVideo.xml'
        else:
          XMLtemplate = 'ScrobbleMenu/ScrobbleMenuVideo.xml'
          
    elif cmd=='ScrobbleMenuDirectory':
        if template == "default":
          XMLtemplate = 'ScrobbleMenuDirectory.xml'
        else:
          XMLtemplate = 'ScrobbleMenu/ScrobbleMenuDirectory.xml'

    elif cmd=='ScrobbleMenuTVOnDeck':
        if template == "default":
          XMLtemplate = 'ScrobbleMenuTVOnDeck.xml'
        else:
          XMLtemplate = 'ScrobbleMenu/ScrobbleMenuTVOnDeck.xml'
        
    elif cmd=='ChangeShowArtwork':
        if template == "default":
          XMLtemplate = 'ChangeShowArtwork.xml'
        else:
          XMLtemplate = 'Artwork/ChangeShowArtwork.xml'

    elif cmd=='ChangeSingleArtwork':
        if template == "default":
          XMLtemplate = 'ChangeSingleArtwork.xml'
        else:
          XMLtemplate = 'Artwork/ChangeSingleArtwork.xml'

    elif cmd=='ChangeSingleArtworkVideo':
        if template == "default":
          XMLtemplate = 'ChangeSingleArtworkVideo.xml'
        else:
          XMLtemplate = 'Artwork/ChangeSingleArtworkVideo.xml'
    
    elif cmd=='ChangeFanartShow':
          XMLtemplate = 'Artwork/ChangeFanartShow.xml'
    elif cmd=='ChangeFanartSeason':
          XMLtemplate = 'Artwork/ChangeFanartSeason.xml'
    elif cmd=='ChangeFanartEpisode':
          XMLtemplate = 'Artwork/ChangeFanartEpisode.xml'
    elif cmd=='ChangeFanartMovie':
          XMLtemplate = 'Artwork/ChangeFanartMovie.xml'
        
    elif cmd=='PhotoBrowser':
        if template == "default":
          XMLtemplate = 'Photo_Browser.xml'
        else:
          XMLtemplate = '/Photo/Browser.xml'
        
    elif cmd=='MoviePreview':
       if template == "default":
         XMLtemplate = 'MoviePreview.xml'
       else:
         XMLtemplate = 'Movie/Preview.xml'
    
    elif cmd=='HomeVideoPrePlay':
        if template == "default":
          XMLtemplate = 'HomeVideoPrePlay.xml'
        else:
          XMLtemplate = 'HomeVideo/PrePlay.xml'
        
    elif cmd=='MoviePrePlay':
       if template == "default":
         XMLtemplate = 'MoviePrePlay.xml'
       else:
         XMLtemplate = 'Movie/PrePlay.xml'

    elif cmd=='EpisodePrePlay':
        if template == "default":
          XMLtemplate = 'EpisodePrePlay.xml'
        else:
          XMLtemplate = 'TVShow/PrePlay.xml'
        
    elif cmd=='ChannelPrePlay':
        if template == "default":
          XMLtemplate = 'ChannelPrePlay.xml'
        else:
          XMLtemplate = 'Channel/PrePlay.xml'
    
    elif cmd=='ChannelsVideo':
        if template == "default":
          XMLtemplate = 'ChannelsVideo.xml'
        else:
          XMLtemplate = 'Channel/Video.xml'

    elif cmd=='ByFolder':
        XMLtemplate = 'ByFolder.xml'

    elif cmd=='HomeVideoByFolder':
        if template == "default":
          XMLtemplate = 'HomeVideoByFolder_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'homevideoview').replace(' ','')+'.xml'
        else:
          XMLtemplate = 'HomeVideo/ByFolder.xml'

    elif cmd == 'HomeVideoDirectory':
        if template == "default":
          XMLtemplate = 'HomeVideoDirectory.xml'
        else:
          XMLtemplate = 'HomeVideo/Directory.xml'

    elif cmd=='MovieByFolder':
       if template == "default":
         XMLtemplate = 'MovieByFolder.xml'
       else:
         XMLtemplate = 'Movie/ByFolder/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_movieview').replace(' ','')+'.xml'  

    elif cmd == 'MovieDirectory':
       if template == "default":
         XMLtemplate = 'MovieDirectory.xml'
       else:
         XMLtemplate = 'Movie/Directory/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_movieview').replace(' ','')+'.xml'       

    elif cmd == 'MovieSection':
       if template == "default":
         XMLtemplate = 'MovieSection.xml'
       else:
         XMLtemplate = 'Movie/Section/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_movieview').replace(' ','')+'.xml'
    
    elif cmd == 'HomeVideoSection':
       if template == "default":
         XMLtemplate = 'HomeVideoSection.xml'
       else:
         XMLtemplate = 'HomeVideo/Section/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_homevideoview').replace(' ','')+'.xml' 
        
    elif cmd == 'TVSection':
       if template == "default":
         XMLtemplate = 'TVSection.xml'
       else:
         XMLtemplate = 'TVShow/Section/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_showview').replace(' ','')+'.xml' 
        
    elif cmd == 'Extras':
         XMLtemplate = 'Extras/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_extraview').replace(' ','')+'.xml'
         
    elif cmd == 'MusicSecondary':
       if template == "default":
        XMLtemplate = 'MusicSecondary.xml'
       else:
        XMLtemplate = 'Music/Secondary.xml'
                 
    elif cmd=='Playlists':
       if template == "default":
        XMLtemplate = 'Playlists.xml'
       else:
        XMLtemplate = 'PlayLists/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_playlistview').replace(' ','')+'.xml'
         
    elif cmd=='Playlist_Video':
       if template == "default":
        XMLtemplate = 'Playlist_Video.xml'
       else:
        XMLtemplate = 'Playlists/Video.xml'

    elif cmd=='Playlist_Audio':
        XMLtemplate = 'Playlists/Audio.xml'

    
    elif cmd == 'LibraryOnDeck':
       if template == "default":
         XMLtemplate = 'Library_OnDeck.xml'
       else:
         XMLtemplate = 'Library/OnDeck.xml'
        
    elif cmd == 'LibraryRecentlyAdded':
       if template == "default":
         XMLtemplate = 'Library_RecentlyAdded.xml'
       else:
         XMLtemplate = 'Library/RecentlyAdded.xml'
    
    elif cmd.find('SectionPreview') != -1:
        if template == "default":
          XMLtemplate = cmd + '.xml'
        else:
          XMLtemplate = 'SectionPreviews/' + cmd + '.xml'
    
    elif cmd == 'AllMovies':
        if template == "default":
          XMLtemplate = 'Movie_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'movieview').replace(' ','')+'.xml'
        else:
          XMLtemplate = 'Movie/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_movieview').replace(' ','')+'.xml' 
    
    elif cmd == 'AllHomeVideos':
        if template == "default":
          XMLtemplate = 'HomeVideo_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'homevideoview').replace(' ','')+'.xml'
        else:
          XMLtemplate = 'HomeVideo/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_homevideoview').replace(' ','')+'.xml'  
        
    elif cmd == 'MovieSecondary':
        if template == "default":
         XMLtemplate = 'MovieSecondary.xml'
        else:
         XMLtemplate = 'Movie/Secondary.xml'
        
    elif cmd == 'AllShows':
        if template == "default":
          XMLtemplate = 'Show_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'showview').replace(' ','')+'.xml'  
        else:
          XMLtemplate = 'TVShow/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_showview').replace(' ','')+'.xml' 
          
    elif cmd == 'TVSecondary':
        if template == "default":
          XMLtemplate = 'TVSecondary.xml'  
        else:
          XMLtemplate = 'TVShow/Secondary.xml'
        
    elif cmd == 'PhotoSecondary':
        if template == "default":
          XMLtemplate = 'PhotoSecondary.xml'
        else:
          XMLtemplate = 'Photo/Secondary.xml'
        
    elif cmd == 'Directory':
        if template == "default":
          XMLtemplate = 'Directory.xml'
        else:
          XMLtemplate = 'Directory/Directory.xml'
    
    elif cmd == 'DirectoryWithPreview':
        if template == "default":
          XMLtemplate = 'DirectoryWithPreview.xml'
        else:
          XMLtemplate = 'Directory/WithPreview.xml'

    elif cmd == 'DirectoryWithPreviewActors':
        if template == "default":
          XMLtemplate = 'DirectoryWithPreviewActors.xml'
        else:
          XMLtemplate = 'Directory/WithPreviewActors.xml'
        
    elif cmd=='Settings':
        if template == "default":
          XMLtemplate = 'Settings.xml'
        else:
          XMLtemplate = 'Settings/Settings.xml'
        path = ''  # clear path - we don't need PMS-XML
        
    elif cmd=='SettingsPrecache':
        XMLtemplate = 'Settings/Precache.xml'
        path = ''  # clear path - we don't need PMS-XML
        
    elif cmd=='SettingsMusic':
       if template == "default":
        XMLtemplate = 'Settings_Music.xml'
       else:
        XMLtemplate = 'Settings/Music.xml' 
        path = ''  # clear path - we don't need PMS-XML    
        
    elif cmd=='SettingsTranscoder':
        XMLtemplate = 'Settings/Transcoder.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='SettingsTemplate':
        XMLtemplate = 'Settings/Template/Template.xml'
        path = ''  # clear path - we don't need PMS-XML   
    
    elif cmd=='SettingsTemplateBackground':
        XMLtemplate = 'Settings/Template/Background.xml'
        path = ''  # clear path - we don't need PMS-XML
        
    elif cmd=='SettingsTemplateText':
        XMLtemplate = 'Settings/Template/Text.xml'
        path = ''  # clear path - we don't need PMS-XML  
        
    elif cmd=='SettingsViews':
        XMLtemplate = 'Settings/Views.xml'
        path = ''  # clear path - we don't need PMS-XML
        
    elif cmd=='SettingsTopLevel':
        if template == "default":
          XMLtemplate = 'Settings_TopLevel.xml'
        else:
          XMLtemplate = 'Settings/TopLevel.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='SettingsVideoOSD':
        if template == "default":
          XMLtemplate = 'Settings_VideoOSD.xml'
        else:
          XMLtemplate = 'Settings/VideoOSD.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='SettingsLibrary':
        if template == "default":
          XMLtemplate = 'Settings_Library.xml'
        else:
          XMLtemplate = 'Settings/Library.xml'
        path = ''  # clear path - we don't need PMS-XML
        
    elif cmd=='SettingsMovies':
       if template == "default":
         XMLtemplate = 'Settings_Movies.xml'
       else:
         XMLtemplate = 'Settings/Movies.xml'
       path = ''  # clear path - we don't need PMS-XML
        
    elif cmd=='SettingsTVShows':
        if template == "default":
          XMLtemplate = 'Settings_TVShows.xml'
        else:
          XMLtemplate = 'Settings/TVShows.xml'
        path = ''  # clear path - we don't need PMS-XML
 
    elif cmd=='SettingsHomeVideos':
        if template == "default":
          XMLtemplate = 'Settings_HomeVideos.xml'
        else:
          XMLtemplate = 'Settings/HomeVideos.xml'
        path = ''  # clear path - we don't need PMS-XML

    elif cmd=='SettingsChannels':
        if template == "default":
          XMLtemplate = 'Settings_Channels.xml'
        else:
          XMLtemplate = 'Settings/Channels.xml'
        path = ''  # clear path - we don't need PMS-XML
        
    elif cmd=='SettingsNavigation':
          XMLtemplate = 'Settings/Navigation.xml'
        
    elif cmd.startswith('purgeFanart'):
        import PILBackgrounds
        PILBackgrounds.purgeFanart()  
        #opt = cmd[len('purgeFanart:'):]  # cut command:
        #parts = opt.split('+')
        #XMLtemplate = parts[1] + ".xml"
        dprint(__name__, 1, 'purging: {0}', "Fanart Cache")  # Debug 
        path = ''  # clear path - we don't need PMS-XML  
        
    elif cmd.startswith('SettingsToggle:'):
        opt = cmd[len('SettingsToggle:'):]  # cut command:
        parts = opt.split('+')
        g_ATVSettings.toggleSetting(options['PlexConnectUDID'], parts[0].lower())
        XMLtemplate = parts[1] + ".xml"
        dprint(__name__, 2, "ATVSettings->Toggle: {0} in template: {1}", parts[0], parts[1])
        
        path = ''  # clear path - we don't need PMS-XML
        
    elif cmd==('MyPlexLogin'):
        dprint(__name__, 2, "MyPlex->Logging In...")
        if not 'PlexConnectCredentials' in options:
            return XML_Error('PlexConnect', 'MyPlex Sign In called without Credentials.')
        
        parts = options['PlexConnectCredentials'].split(':',1)        
        (username, auth_token) = PlexAPI.MyPlexSignIn(parts[0], parts[1], options)
        
        g_ATVSettings.setSetting(UDID, 'myplex_user', username)
        g_ATVSettings.setSetting(UDID, 'myplex_auth', auth_token)
        
        if template == "default":
          XMLtemplate = 'Settings.xml'
        else:
          XMLtemplate = 'Settings/Settings.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='MyPlexLogout':
        dprint(__name__, 2, "MyPlex->Logging Out...")
        
        auth_token = g_ATVSettings.getSetting(UDID, 'myplex_auth')
        PlexAPI.MyPlexSignOut(auth_token)
        
        g_ATVSettings.setSetting(UDID, 'myplex_user', '')
        g_ATVSettings.setSetting(UDID, 'myplex_auth', '')
        
        if template == "default":
          XMLtemplate = 'Settings.xml'
        else:
          XMLtemplate = 'Settings/Settings.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd.startswith('Discover'):
        auth_token = g_ATVSettings.getSetting(UDID, 'myplex_auth')
        PlexAPI.discoverPMS(UDID, g_param['CSettings'], auth_token)
        
        return XML_Error('PlexConnect', 'Discover!')  # not an error - but aTV won't care anyways.
    
    elif path.startswith('/search?'):
        XMLtemplate = 'Search_Results.xml'
    
    elif path.find('serviceSearch') != -1 or (path.find('video') != -1 and path.lower().find('search') != -1):
        if template == "default":
          XMLtemplate = 'ChannelsVideoSearchResults.xml'
        else:
          XMLtemplate = 'Channel/VideoSearchResults.xml'
    
    elif path.find('SearchResults') != -1:
        if template == "default":
          XMLtemplate = 'ChannelsVideoSearchResults.xml'
        else:
          XMLtemplate = 'Channel/VideoSearchResults.xml'
    
    elif path=='/library/sections':
        if template == "default":
          XMLtemplate = 'Library.xml' 
        else:
          if PMS_address=='owned': 
            XMLtemplate = 'Library/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_libraryview').replace(' ','')+'.xml'
          else:
            XMLtemplate = 'Library/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_libraryview_remote').replace(' ','')+'.xml'
        
        
    elif path=='/channels/all':
        template = g_ATVSettings.getSetting(options['PlexConnectUDID'], 'template')
        if template == "default":
          XMLtemplate = 'Channel_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'channelview')+'.xml'
        else:
          XMLtemplate = 'Channel/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_channelview').replace(' ','')+'.xml'
        path = ''
    
    # request PMS XML
    if not path=='':
        if PMS_address[0].isalpha():  # owned, shared
            type = PMS_address
            PMS = PlexAPI.getXMLFromMultiplePMS(UDID, path, type, options)
        else:  # IP
            auth_token = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'accesstoken')
            PMS = PlexAPI.getXMLFromPMS(PMS_baseURL, path, options, authtoken=auth_token)
        
        if PMS==False:
            return XML_Error('PlexConnect', 'No Response from Plex Media Server')
        
        PMSroot = PMS.getroot()
        
        dprint(__name__, 1, "viewGroup: "+PMSroot.get('viewGroup','None'))
    
    # XMLtemplate defined by PMS XML content
    if path=='':
        pass  # nothing to load
    
    elif not XMLtemplate=='':
        pass  # template already selected


    elif PMSroot.get('viewGroup','')=="secondary" and (PMSroot.get('art','').find('video') != -1 or PMSroot.get('thumb','').find('video') != -1):
        if template == "default":
          XMLtemplate = 'HomeVideoSectionTopLevel.xml'
        else:
          XMLtemplate = 'HomeVideo/SectionTopLevel.xml'

    elif PMSroot.get('viewGroup','')=="secondary" and (PMSroot.get('art','').find('movie') != -1 or PMSroot.get('thumb','').find('movie') != -1):
        if template == "default":
          XMLtemplate = 'MovieSectionTopLevel.xml'
        else:
          XMLtemplate = 'Movie/SectionTopLevel.xml'
    
    elif PMSroot.get('viewGroup','')=="secondary" and (PMSroot.get('art','').find('show') != -1 or PMSroot.get('thumb','').find('show') != -1):
        if template == "default":
          XMLtemplate = 'TVSectionTopLevel.xml'
        else:
          XMLtemplate = 'TVShow/SectionTopLevel.xml'
        
    elif PMSroot.get('viewGroup','')=="secondary" and (PMSroot.get('art','').find('photo') != -1 or PMSroot.get('thumb','').find('photo') != -1):
        if template == "default":
          XMLtemplate = 'PhotoSectionTopLevel.xml'
        else:
          XMLtemplate = 'Photo/SectionTopLevel.xml'
        
        
    elif PMSroot.get('viewGroup','')=="secondary":
        if template == "default":
          XMLtemplate = 'Directory.xml'
        else:
          XMLtemplate = 'Directory/Directory.xml'
        
    
    elif PMSroot.get('viewGroup','')=='show':
        if PMSroot.get('title2')=='By Folder':
          # By Folder View
          XMLtemplate = 'ByFolder.xml'
        else:
          # TV Show grid view
           if template == "default":
            XMLtemplate = 'Show_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'showview')+'.xml'
           else:
            XMLtemplate = 'TVShow/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_showview').replace(' ','')+'.xml'
        
    elif PMSroot.get('viewGroup','')=='season':
        if template == "default":
          # TV Season view
          XMLtemplate = 'Season_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'seasonview')+'.xml'
        else:
          XMLtemplate = 'TVShow/Season/'+g_ATVSettings.getSetting(UDID, template+'_seasonview').replace(' ','')+'.xml'

    elif PMSroot.get('viewGroup','')=='movie' and PMSroot.get('thumb','').find('video') != -1:
        if PMSroot.get('title2')=='By Folder':
          # By Folder View
             if template == "default":
              XMLtemplate = 'HomeVideoByFolder.xml'
             else:
              XMLtemplate = 'HomeVideo/ByFolder.xml'          
        else:
          # Home Video listing
            if template == "default":
              XMLtemplate = 'HomeVideo_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'homevideoview').replace(' ','')+'.xml'
            else:
              XMLtemplate = 'HomeVideo/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_homevideoview').replace(' ','')+'.xml'
    
    elif PMSroot.get('viewGroup','')=='movie' and PMSroot.get('thumb','').find('movie') != -1:
        if PMSroot.get('title2')=='By Folder':
          # By Folder View
           if template == "default":
            XMLtemplate = 'MovieByFolder.xml'
           else:
            XMLtemplate = 'Movie/ByFolder.xml'          
        else:
          # Movie listing
           if template == "default":
            XMLtemplate = 'Movie_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'movieview').replace(' ','')+'.xml'
           else:
            XMLtemplate = 'Movie/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_movieview').replace(' ','')+'.xml'
   
    elif PMSroot.get('viewGroup','')=='episode':
        if PMSroot.get('title2')=='On Deck' or \
           PMSroot.get('title2')=='Recently Viewed Episodes' or \
           PMSroot.get('title2')=='Recently Aired' or \
           PMSroot.get('title2')=='Recently Added':
            # TV On Deck View
            
           if template == "default":
             XMLtemplate = 'TV_OnDeck.xml'  
           else:
             XMLtemplate = 'TVShow/OnDeck.xml'
            
        else:
            if template == "default":
              XMLtemplate = 'Episode.xml'  
            else:
              # TV Episode view
              XMLtemplate = 'TVShow/Episode/'+g_ATVSettings.getSetting(options['PlexConnectUDID'], template+'_episodeview').replace(' ','')+'.xml'
              
              
    
    elif PMSroot.get('viewGroup','')=='photo' or \
       path.startswith('/photos') or \
       PMSroot.find('Photo')!=None:
        if PMSroot.find('Directory')==None:
            # Photos only - directly show
            XMLtemplate = 'Photo_Browser.xml'
        else:
            # Photo listing / directory
            XMLtemplate = 'Photo_Directories.xml'
    
    elif PMSroot.get('viewGroup','')=='track':
        if template == "default":
          XMLtemplate = "Music_Track.xml"
        else:
          XMLtemplate = "Music/Track.xml"  
    else:
        if template == "default":
          XMLtemplate = 'Directory.xml'
        else:
          XMLtemplate = 'Directory/Directory.xml'
    
    dprint(__name__, 1, "XMLTemplate: "+XMLtemplate)

    # get XMLtemplate
    template = g_ATVSettings.getSetting(options['PlexConnectUDID'], 'template')
    if template == "default":
      aTVTree = etree.parse(sys.path[0]+'/assets/templates/default/xml/'+XMLtemplate)
    else:
      aTVTree = etree.parse(sys.path[0]+'/assets/templates/'+template+'/xml/'+XMLtemplate)

    aTVroot = aTVTree.getroot()
    
    # convert PMS XML to aTV XML using provided XMLtemplate
    CommandCollection = CCommandCollection(options, PMSroot, PMS_address, path)
    XML_ExpandTree(CommandCollection, aTVroot, PMSroot, 'main')
    XML_ExpandAllAttrib(CommandCollection, aTVroot, PMSroot, 'main')
    del CommandCollection
    
    if cmd=='ChannelsSearch':
        for bURL in aTVroot.iter('baseURL'):
            if channelsearchURL.find('?') == -1:
                bURL.text = channelsearchURL + '?query='
            else:
                bURL.text = channelsearchURL + '&query='
                
    dprint(__name__, 1, "====== generated aTV-XML ======")
    dprint(__name__, 1, aTVroot)
    dprint(__name__, 1, "====== aTV-XML finished ======")
    
    return etree.tostring(aTVroot)



def XML_ExpandTree(CommandCollection, elem, src, srcXML):
    # unpack template 'COPY'/'CUT' command in children
    res = False
    while True:
        if list(elem)==[]:  # no sub-elements, stop recursion
            break
        
        for child in elem:
            res = XML_ExpandNode(CommandCollection, elem, child, src, srcXML, 'TEXT')
            if res==True:  # tree modified: restart from 1st elem
                break  # "for child"
            
            # recurse into children
            XML_ExpandTree(CommandCollection, child, src, srcXML)
            
            res = XML_ExpandNode(CommandCollection, elem, child, src, srcXML, 'TAIL')
            if res==True:  # tree modified: restart from 1st elem
                break  # "for child"
        
        if res==False:  # complete tree parsed with no change, stop recursion
            break  # "while True"



def XML_ExpandNode(CommandCollection, elem, child, src, srcXML, text_tail):
    if text_tail=='TEXT':  # read line from text or tail
        line = child.text
    elif text_tail=='TAIL':
        line = child.tail
    else:
        dprint(__name__, 0, "XML_ExpandNode - text_tail badly specified: {0}", text_tail)
        return False
    
    pos = 0
    while line!=None:
        cmd_start = line.find('{{',pos)
        cmd_end   = line.find('}}',pos)
        next_start = line.find('{{',cmd_start+2)
        while next_start!=-1 and next_start<cmd_end:
            cmd_end = line.find('}}',cmd_end+2)
            next_start = line.find('{{',next_start+2)
        if cmd_start==-1 or cmd_end==-1 or cmd_start>cmd_end:
            return False  # tree not touched, line unchanged
        
        dprint(__name__, 2, "XML_ExpandNode: {0}", line)
        
        cmd = line[cmd_start+2:cmd_end]
        if cmd[-1]!=')':
            dprint(__name__, 0, "XML_ExpandNode - closing bracket missing: {0} ", line)
        
        parts = cmd.split('(',1)
        cmd = parts[0]
        param = parts[1].strip(')')  # remove ending bracket
        param = XML_ExpandLine(CommandCollection, src, srcXML, param)  # expand any attributes in the parameter
        
        res = False
        if hasattr(CCommandCollection, 'TREE_'+cmd):  # expand tree, work COPY, CUT
            line = line[:cmd_start] + line[cmd_end+2:]  # remove cmd from text and tail
            if text_tail=='TEXT':  
                child.text = line
            elif text_tail=='TAIL':
                child.tail = line
            
            try:
                res = getattr(CommandCollection, 'TREE_'+cmd)(elem, child, src, srcXML, param)
            except:
                dprint(__name__, 0, "XML_ExpandNode - Error in cmd {0}, line {1}\n{2}", cmd, line, traceback.format_exc())
            
            if res==True:
                return True  # tree modified, node added/removed: restart from 1st elem
        
        elif hasattr(CCommandCollection, 'ATTRIB_'+cmd):  # check other known cmds: VAL, EVAL...
            dprint(__name__, 2, "XML_ExpandNode - Stumbled over {0} in line {1}", cmd, line)
            pos = cmd_end
        else:
            dprint(__name__, 0, "XML_ExpandNode - Found unknown cmd {0} in line {1}", cmd, line)
            line = line[:cmd_start] + "((UNKNOWN:"+cmd+"))" + line[cmd_end+2:]  # mark unknown cmd in text or tail
            if text_tail=='TEXT':
                child.text = line
            elif text_tail=='TAIL':
                child.tail = line
    
    dprint(__name__, 2, "XML_ExpandNode: {0} - done", line)
    return False



def XML_ExpandAllAttrib(CommandCollection, elem, src, srcXML):
    # unpack template commands in elem.text
    line = elem.text
    if line!=None:
        elem.text = XML_ExpandLine(CommandCollection, src, srcXML, line.strip())
    
    # unpack template commands in elem.tail
    line = elem.tail
    if line!=None:
        elem.tail = XML_ExpandLine(CommandCollection, src, srcXML, line.strip())
    
    # unpack template commands in elem.attrib.value
    for attrib in elem.attrib:
        line = elem.get(attrib)
        elem.set(attrib, XML_ExpandLine(CommandCollection, src, srcXML, line.strip()))
    
    # recurse into children
    for el in elem:
        XML_ExpandAllAttrib(CommandCollection, el, src, srcXML)



def XML_ExpandLine(CommandCollection, src, srcXML, line):
    pos = 0
    while True:
        cmd_start = line.find('{{',pos)
        cmd_end   = line.find('}}',pos)
        next_start = line.find('{{',cmd_start+2)
        while next_start!=-1 and next_start<cmd_end:
            cmd_end = line.find('}}',cmd_end+2)
            next_start = line.find('{{',next_start+2)

        if cmd_start==-1 or cmd_end==-1 or cmd_start>cmd_end:
            break;
        
        dprint(__name__, 2, "XML_ExpandLine: {0}", line)
        
        cmd = line[cmd_start+2:cmd_end]
        if cmd[-1]!=')':
            dprint(__name__, 0, "XML_ExpandLine - closing bracket missing: {0} ", line)
        
        parts = cmd.split('(',1)
        cmd = parts[0]
        param = parts[1][:-1]  # remove ending bracket
        param = XML_ExpandLine(CommandCollection, src, srcXML, param)  # expand any attributes in the parameter
        
        if hasattr(CCommandCollection, 'ATTRIB_'+cmd):  # expand line, work VAL, EVAL...
            
            try:
                res = getattr(CommandCollection, 'ATTRIB_'+cmd)(src, srcXML, param)
                line = line[:cmd_start] + res + line[cmd_end+2:]
                pos = cmd_start+len(res)
            except:
                dprint(__name__, 0, "XML_ExpandLine - Error in {0}\n{1}", line, traceback.format_exc())
                line = line[:cmd_start] + "((ERROR:"+cmd+"))" + line[cmd_end+2:]
        
        elif hasattr(CCommandCollection, 'TREE_'+cmd):  # check other known cmds: COPY, CUT
            dprint(__name__, 2, "XML_ExpandLine - stumbled over {0} in line {1}", cmd, line)
            pos = cmd_end
        else:
            dprint(__name__, 0, "XML_ExpandLine - Found unknown cmd {0} in line {1}", cmd, line)
            line = line[:cmd_start] + "((UNKNOWN:"+cmd+"))" + line[cmd_end+2:]    
        
        dprint(__name__, 2, "XML_ExpandLine: {0} - done", line)
    return line



"""
# Command expander classes
# CCommandHelper():
#     base class to the following, provides basic parsing & evaluation functions
# CCommandCollection():
#     cmds to set up sources (ADDXML, VAR)
#     cmds with effect on the tree structure (COPY, CUT) - must be expanded first
#     cmds dealing with single node keys, text, tail only (VAL, EVAL, ADDR_PMS ,...)
"""
class CCommandHelper():
    def __init__(self, options, PMSroot, PMS_address, path):
        self.options = options
        self.PMSroot = {'main': PMSroot}
        self.PMS_address = PMS_address  # default PMS if nothing else specified
        self.path = {'main': path}
        
        self.ATV_udid = options['PlexConnectUDID']
        self.PMS_uuid = PlexAPI.getPMSFromAddress(self.ATV_udid, PMS_address)
        self.PMS_baseURL = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'baseURL')
        self.variables = {}
    
    # internal helper functions
    def getParam(self, src, param):
        parts = param.split(':',1)
        param = parts[0]
        leftover=''
        if len(parts)>1:
            leftover = parts[1]
        
        param = param.replace('&col;',':')  # colon  # replace XML_template special chars
        param = param.replace('&ocb;','{')  # opening curly brace
        param = param.replace('&ccb;','}')  # closinging curly brace
        
        param = param.replace('&quot;','"')  # replace XML special chars
        param = param.replace('&apos;',"'")
        param = param.replace('&lt;','<')
        param = param.replace('&gt;','>')
        param = param.replace('&amp;','&')  # must be last
        
        dprint(__name__, 2, "CCmds_getParam: {0}, {1}", param, leftover)
        return [param, leftover]
    
    def getKey(self, src, srcXML, param):
        attrib, leftover = self.getParam(src, param)
        default, leftover = self.getParam(src, leftover)
        
        el, srcXML, attrib = self.getBase(src, srcXML, attrib)         
        
        # walk the path if neccessary
        while '/' in attrib and el!=None:
            parts = attrib.split('/',1)
            if parts[0].startswith('#') and attrib[1:] in self.variables:  # internal variable in path
                el = el.find(self.variables[parts[0][1:]])
            elif parts[0].startswith('$'):  # setting
                el = el.find(g_ATVSettings.getSetting(self.ATV_udid, parts[0][1:]))
            elif parts[0].startswith('%'):  # PMS property
                el = el.find(PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, parts[0][1:]))
            else:
                el = el.find(parts[0])
            attrib = parts[1]
        
        # check element and get attribute
        if attrib.startswith('#') and attrib[1:] in self.variables:  # internal variable
            res = self.variables[attrib[1:]]
            dfltd = False
        elif attrib.startswith('$'):  # setting
            res = g_ATVSettings.getSetting(self.ATV_udid, attrib[1:])
            dfltd = False
        elif attrib.startswith('%'):  # PMS property
            res = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, attrib[1:])
            dfltd = False
        elif attrib.startswith('^') and attrib[1:] in self.options:  # aTV property, http request options
            res = self.options[attrib[1:]]
            dfltd = False
        elif el!=None and attrib in el.attrib:
            res = el.get(attrib)
            dfltd = False
        
        else:  # path/attribute not found
            res = default
            dfltd = True
        
        dprint(__name__, 2, "CCmds_getKey: {0},{1},{2}", res, leftover,dfltd)
        return [res,leftover,dfltd]
    
    def getElement(self, src, srcXML, param):
        tag, leftover = self.getParam(src, param)
        
        el, srcXML, tag = self.getBase(src, srcXML, tag)
        
        # walk the path if neccessary
        while len(tag)>0:
            parts = tag.split('/',1)
            el = el.find(parts[0])
            if not '/' in tag or el==None:
                break
            tag = parts[1]
        return [el, leftover]
    
    def getBase(self, src, srcXML, param):
        # get base element
        if param.startswith('@'):  # redirect to additional XML
            parts = param.split('/',1)
            srcXML = parts[0][1:]
            src = self.PMSroot[srcXML]
            leftover=''
            if len(parts)>1:
                leftover = parts[1]
        elif param.startswith('/'):  # start at root
            src = self.PMSroot['main']
            leftover = param[1:]
        else:
            leftover = param
        
        return [src, srcXML, leftover]
    
    def getConversion(self, src, param):
        conv, leftover = self.getParam(src, param)
        
        # build conversion "dictionary"
        convlist = []
        if conv!='':
            parts = conv.split('|')
            for part in parts:
                convstr = part.split('=')
                convlist.append((unquote_plus(convstr[0]), unquote_plus(convstr[1])))
        
        dprint(__name__, 2, "CCmds_getConversion: {0},{1}", convlist, leftover)
        return [convlist, leftover]
    
    def applyConversion(self, val, convlist):
        # apply string conversion            
        if convlist!=[]:
            for part in reversed(sorted(convlist)):
                if val>=part[0]:
                    val = part[1]
                    break
        
        dprint(__name__, 2, "CCmds_applyConversion: {0}", val)
        return val
    
    def applyMath(self, val, math, frmt):
        # apply math function - eval
        try:
            x = eval(val)
            if math!='':
                x = eval(math)
            val = ('{0'+frmt+'}').format(x)
        except:
            dprint(__name__, 0, "CCmds_applyMath: Error in math {0}, frmt {1}\n{2}", math, frmt, traceback.format_exc())
        # apply format specifier
        
        dprint(__name__, 2, "CCmds_applyMath: {0}", val)
        return val
    
    def _(self, msgid):
        return Localize.getTranslation(self.options['aTVLanguage']).ugettext(msgid)



class CCommandCollection(CCommandHelper):
    # XML TREE modifier commands
    # add new commands to this list!
    def TREE_COPY(self, elem, child, src, srcXML, param):
        
        # is MULTICOPY?
        tags=param.split(',')
        if len(tags) > 1:
            tag, param_enbl = self.getParam(src, tags[0])
        else:
            tag, param_enbl = self.getParam(src, param)
        src, srcXML, tag = self.getBase(src, srcXML, tag)        
        
        # walk the src path if neccessary
        while '/' in tag and src!=None:
            parts = tag.split('/',1)
            src = src.find(parts[0])
            tag = parts[1]
        
        # find index of child in elem - to keep consistent order
        for ix, el in enumerate(list(elem)):
            if el==child:
                break
        
        
        #get all requested tags
        itemrange = src.findall(tag)
        # is MULTICOPY?
        for i in range(len(tags)):
            if i > 0:
                itemrange=itemrange+src.findall(tags[i])
        
        # sort by addedAt (updatedAt?)
        if len(tags) > 1:
            itemrange = sorted(itemrange, key=lambda x: x.attrib.get('addedAt'), reverse=True)
        for elemSRC in itemrange:
            key = 'COPY'
            if param_enbl!='':
                key, leftover, dfltd = self.getKey(elemSRC, srcXML, param_enbl)
                conv, leftover = self.getConversion(elemSRC, leftover)
                if not dfltd:
                    key = self.applyConversion(key, conv)
            
            if key:
                self.PMSroot['copy_'+tag] = elemSRC
                el = copy.deepcopy(child)
                XML_ExpandTree(self, el, elemSRC, srcXML)
                XML_ExpandAllAttrib(self, el, elemSRC, srcXML)
                
                if el.tag=='__COPY__':
                    for el_child in list(el):
                        elem.insert(ix, el_child)
                        ix += 1
                else:
                    elem.insert(ix, el)
                    ix += 1


        
        # remove template child
        elem.remove(child)
        return True  # tree modified, nodes updated: restart from 1st elem
    
    #syntax: Video, playType (Single|Continuous), key to match (^PlexConnectRatingKey), ratingKey
    def TREE_COPY_PLAYLIST(self, elem, child, src, srcXML, param):
        tag, leftover  = self.getParam(src, param)
        playType, leftover, dfltd = self.getKey(src, srcXML, leftover)  # Single (default), Continuous
        key, leftover, dfltd = self.getKey(src, srcXML, leftover)
        param_key = leftover
        
        src, srcXML, tag = self.getBase(src, srcXML, tag)
        
        # walk the src path if neccessary
        while '/' in tag and src!=None:
            parts = tag.split('/',1)
            src = src.find(parts[0])
            tag = parts[1]
        
        # find index of child in elem - to keep consistent order
        for ix, el in enumerate(list(elem)):
            if el==child:
                break
        
        # filter elements to copy
        cnt = 0
        copy_enbl = False
        elemsSRC = []
        for elemSRC in src.findall(tag):
            child_key, leftover, dfltd = self.getKey(elemSRC, srcXML, param_key)
            if not key:
                copy_enbl = True                           # copy all
            elif playType == 'Continuous' or playType== 'Shuffle':
                copy_enbl = copy_enbl or (key==child_key)  # [0 0 1 1 1 1]
            else:  # 'Single' (default)
                copy_enbl = (key==child_key)               # [0 0 1 0 0 0]
            
            if copy_enbl:
                elemsSRC.append(elemSRC)
        
        # shuffle elements
        if playType == 'Shuffle':
            if not key:
                random.shuffle(elemsSRC)                   # shuffle all
            else:
                elems = elemsSRC[1:]                       # keep first element fix
                random.shuffle(elems)
                elemsSRC = [elemsSRC[0]] + elems
        
        # duplicate child and add to tree
        cnt = 0
        for elemSRC in elemsSRC:
                self.PMSroot['copy_'+tag] = elemSRC
                self.variables['copy_ix'] = str(cnt)
                cnt = cnt+1
                el = copy.deepcopy(child)
                XML_ExpandTree(self, el, elemSRC, srcXML)
                XML_ExpandAllAttrib(self, el, elemSRC, srcXML)
                
                if el.tag=='__COPY__':
                    for el_child in list(el):
                        elem.insert(ix, el_child)
                        ix += 1
                else:
                    elem.insert(ix, el)
                    ix += 1
        
        # remove template child
        elem.remove(child)
        return True  # tree modified, nodes updated: restart from 1st elem
    
    def TREE_PAGEDCOPY(self, elem, child, src, srcXML, param):
        
        # is MULTICOPY?
        tags=param.split(',')
        tag, param_enbl = self.getParam(src, tags[0])
        src, srcXML, tag = self.getBase(src, srcXML, tag)
        columncount=tags[1]
        rowcount=tags[2]
        
        
        
        
        # walk the src path if neccessary
        while '/' in tag and src!=None:
            parts = tag.split('/',1)
            src = src.find(parts[0])
            tag = parts[1]
        
        # find index of child in elem - to keep consistent order
        for ix, el in enumerate(list(elem)):
            if el==child:
                break
        
        #get all requested tags
        itemrange = src.findall(tag)
        # is MULTICOPY?
        for i in range(len(tags)):
            if i > 2:
                itemrange=itemrange+src.findall(tags[i])
        
        maxicons = int(columncount) * int(rowcount)
        pagecount = 0
        iconcount = 0
        
        if len(tags) > 3:
            itemrange = sorted(itemrange, key=lambda x: x.attrib.get('addedAt'), reverse=True)
        
        for elemSRC in itemrange:
            
            key = 'COPY'
            if param_enbl!='':
                key, leftover, dfltd = self.getKey(elemSRC, srcXML, param_enbl)
                conv, leftover = self.getConversion(elemSRC, leftover)
                if not dfltd:
                    key = self.applyConversion(key, conv)
            
            
            if key:
                
                if iconcount == 0:
                    pagecount += 1
                    currentgrid = etree.SubElement(elem, "grid")
                    currentgrid.set("id","grid_"+str(pagecount))
                    currentgrid.set("columnCount", columncount )
                    items = etree.SubElement(currentgrid, "items")
                elif iconcount % maxicons == 0:
                    pagecount += 1
                    currentgrid = etree.SubElement(elem, "grid")
                    currentgrid.set("id","grid_"+str(pagecount))
                    currentgrid.set("columnCount", columncount )
                    items = etree.SubElement(currentgrid, "items")
                
                
                el = copy.deepcopy(child)
                XML_ExpandTree(self, el, elemSRC, srcXML)
                XML_ExpandAllAttrib(self, el, elemSRC, srcXML)
                
                if el.tag=='__COPY__':
                    for el_child in list(el):
                        items.insert(ix, el_child)
                        ix += 1
                        iconcount += 1
                else:
                    items.insert(ix, el)
                    ix += 1
                    iconcount += 1
        
        
        
        
        
        # remove template child
        elem.remove(child)
        return True  # tree modified, nodes updated: restart from 1st elem
    
    
    def TREE_CUT(self, elem, child, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        conv, leftover = self.getConversion(src, leftover)
        if not dfltd:
            key = self.applyConversion(key, conv)
        if key:
            elem.remove(child)
            return True  # tree modified, node removed: restart from 1st elem
        else:
            return False  # tree unchanged
    
    def TREE_ADDXML(self, elem, child, src, srcXML, param):
        tag, leftover = self.getParam(src, param)
        key, leftover, dfltd = self.getKey(src, srcXML, leftover)
        
        PMS_address = self.PMS_address
        
        if key.startswith('//'):  # local servers signature
            pathstart = key.find('/',3)
            PMS_address= key[:pathstart]
            path = key[pathstart:]
        elif key.startswith('/'):  # internal full path.
            path = key
        #elif key.startswith('http://'):  # external address
        #    path = key
        elif key == '':  # internal path
            path = self.path[srcXML]
        else:  # internal path, add-on
            path = self.path[srcXML] + '/' + key
        
        if PMS_address[0].isalpha():  # owned, shared
            type = self.PMS_address
            PMS = PlexAPI.getXMLFromMultiplePMS(self.ATV_udid, path, type, self.options)
        else:  # IP
            auth_token = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'accesstoken')
            PMS = PlexAPI.getXMLFromPMS(self.PMS_baseURL, path, self.options, auth_token)
        
        self.PMSroot[tag] = PMS.getroot()  # store additional PMS XML
        self.path[tag] = path  # store base path
        
        return False  # tree unchanged (well, source tree yes. but that doesn't count...)
    
    def TREE_VAR(self, elem, child, src, srcXML, param):
        var, leftover = self.getParam(src, param)
        key, leftover, dfltd = self.getKey(src, srcXML, leftover)
        conv, leftover = self.getConversion(src, leftover)
        if not dfltd:
            key = self.applyConversion(key, conv)
        
        self.variables[var] = key
        return False  # tree unchanged
    
    
    # XML ATTRIB modifier commands
    # add new commands to this list!
    def ATTRIB_VAL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        conv, leftover = self.getConversion(src, leftover)
        if not dfltd:
            key = self.applyConversion(key, conv)
        return key
    
    def ATTRIB_EVAL(self, src, srcXML, param):
        return str(eval(param))
    
    def ATTRIB_VAL_QUOTED(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        conv, leftover = self.getConversion(src, leftover)
        if not dfltd:
            key = self.applyConversion(key, conv)
        return quote_plus(unicode(key).encode("utf-8"))
    
    def ATTRIB_SETTING(self, src, srcXML, param):
        opt, leftover = self.getParam(src, param)
        return g_ATVSettings.getSetting(self.ATV_udid, opt)
    
    def ATTRIB_ADDPATH(self, src, srcXML, param):
        addpath, leftover, dfltd = self.getKey(src, srcXML, param)
        if addpath.startswith('/'):
            res = addpath
        elif addpath == '':
            res = self.path[srcXML]
        else:
            res = self.path[srcXML]+'/'+addpath
        return res
    
    def ATTRIB_IMAGEURL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        width, leftover = self.getParam(src, leftover)
        height, leftover = self.getParam(src, leftover)
        if height=='':
            height = width
        
        PMS_uuid = self.PMS_uuid
        PMS_baseURL = self.PMS_baseURL
        cmd_start = key.find('PMS(')
        cmd_end = key.find(')', cmd_start)
        if cmd_start>-1 and cmd_end>-1 and cmd_end>cmd_start:
            PMS_address = key[cmd_start+4:cmd_end]
            PMS_uuid = PlexAPI.getPMSFromAddress(self.ATV_udid, PMS_address)
            PMS_baseURL = PlexAPI.getPMSProperty(self.ATV_udid, PMS_uuid, 'baseURL')
            key = key[cmd_end+1:]
        
        AuthToken = PlexAPI.getPMSProperty(self.ATV_udid, PMS_uuid, 'accesstoken')
        
        # transcoder action
        transcoderAction = g_ATVSettings.getSetting(self.ATV_udid, 'phototranscoderaction')
        
        # aTV native filetypes
        parts = key.rsplit('.',1)
        photoATVNative = parts[-1].lower() in ['jpg','jpeg','tif','tiff','gif','png']
        dprint(__name__, 2, "photo: ATVNative - {0}", photoATVNative)
        
        if width=='' and \
            transcoderAction=='Auto' and \
            photoATVNative:
                # direct play
                res = PlexAPI.getDirectImagePath(key, AuthToken)
        else:
            if width=='':
                width = 1920  # max for HDTV. Relate to aTV version? Increase for KenBurns effect?
            if height=='':
                height = 1080  # as above
            # request transcoding
            res = PlexAPI.getTranscodeImagePath(key, AuthToken, self.path[srcXML], width, height)
        
        if res.startswith('/'):  # internal full path.
            res = PMS_baseURL + res
        elif res.startswith('http://') or key.startswith('https://'):  # external address
            pass
        else:  # internal path, add-on
            res = PMS_baseURL + self.path[srcXML] + '/' + res
        
        dprint(__name__, 1, 'ImageURL: {0}', res)
        return res
    
    def ATTRIB_MUSICURL(self, src, srcXML, param):
        Track, leftover = self.getElement(src, srcXML, param)
        
        AuthToken = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'accesstoken')
        
        if not Track:
            # not a complete audio/track structure - take key directly and build direct-play path
            key, leftover, dfltd = self.getKey(src, srcXML, param)
            res = PlexAPI.getDirectAudioPath(key, AuthToken)
            res = PlexAPI.getURL(self.PMS_baseURL, self.path[srcXML], res)
            dprint(__name__, 1, 'MusicURL - direct: {0}', res)
            return res
        
        # complete track structure - request transcoding if needed
        Media = Track.find('Media')
        
        # check "Media" element and get key
        if Media!=None:
            # transcoder action setting?
            # transcoder bitrate setting [kbps] -  eg. 128, 256, 384, 512?
            maxAudioBitrate = '384'
            
            audioATVNative = \
                Media.get('audioCodec','-') in ("mp3", "aac", "ac3", "drms", "alac", "aiff", "wav")
            # check Media.get('container') as well - mp3, m4a, ...?
            
            dprint(__name__, 2, "audio: ATVNative - {0}", audioATVNative)
            
            if audioATVNative and\
                int(Media.get('bitrate','0')) < int(maxAudioBitrate):
                    # direct play
                    res, leftover, dfltd = self.getKey(Media, srcXML, 'Part/key')
                    res = PlexAPI.getDirectAudioPath(res, AuthToken)
            else:
                # request transcoding
                res, leftover, dfltd = self.getKey(Track, srcXML, 'key')
                res = PlexAPI.getTranscodeAudioPath(res, AuthToken, self.options, maxAudioBitrate)
        
        else:
            dprint(__name__, 0, "MEDIAPATH - element not found: {0}", param)
            res = 'FILE_NOT_FOUND'  # not found?
        
        res = PlexAPI.getURL(self.PMS_baseURL, self.path[srcXML], res)
        dprint(__name__, 1, 'MusicURL: {0}', res)
        return res
    
    def ATTRIB_URL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        
        # compare PMS_mark in PlexAPI/getXMLFromMultiplePMS()
        PMS_mark = '/PMS(' + PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'ip') + ')'
        
        # overwrite with URL embedded PMS address
        cmd_start = key.find('PMS(')
        cmd_end = key.find(')', cmd_start)
        if cmd_start>-1 and cmd_end>-1 and cmd_end>cmd_start:
            PMS_mark = '/'+key[cmd_start:cmd_end+1]
            key = key[cmd_end+1:]
        
        res = g_param['baseURL']  # base address to PlexConnect
        
        if key.endswith('.js'):  # link to PlexConnect owned .js stuff
            res = res + key
        elif key.startswith('http://') or key.startswith('https://'):  # external server
            res = key
            """
            parts = urlparse.urlsplit(key)  # (scheme, networklocation, path, ...)
            key = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))  # keep path only
            PMS_uuid = PlexAPI.getPMSFromIP(g_param['PMS_list'], parts.hostname)
            PMSaddress = PlexAPI.getAddress(g_param['PMS_list'], PMS_uuid)  # get PMS address (might be local as well!?!)
            res = res + '/PMS(' + quote_plus(PMSaddress) + ')' + key
            """
        elif key.startswith('/'):  # internal full path.
            res = res + PMS_mark + key
        elif key == '':  # internal path
            res = res + PMS_mark + self.path[srcXML]
        else:  # internal path, add-on
            res = res + PMS_mark + self.path[srcXML] + '/' + key
        
        return res

    def ATTRIB_stripChildrenURL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        key = str(key).replace('/children','')

        # compare PMS_mark in PlexAPI/getXMLFromMultiplePMS()
        PMS_mark = '/PMS(' + PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'ip') + ')'
        
        # overwrite with URL embedded PMS address
        cmd_start = key.find('PMS(')
        cmd_end = key.find(')', cmd_start)
        if cmd_start>-1 and cmd_end>-1 and cmd_end>cmd_start:
            PMS_mark = '/'+key[cmd_start:cmd_end+1]
            key = key[cmd_end+1:]
        
        res = g_param['baseURL']  # base address to PlexConnect
        
        if key.endswith('.js'):  # link to PlexConnect owned .js stuff
            res = res + key
        elif key.startswith('http://') or key.startswith('https://'):  # external server
            res = key
            """
            parts = urlparse.urlsplit(key)  # (scheme, networklocation, path, ...)
            key = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))  # keep path only
            PMS_uuid = PlexAPI.getPMSFromIP(g_param['PMS_list'], parts.hostname)
            PMSaddress = PlexAPI.getAddress(g_param['PMS_list'], PMS_uuid)  # get PMS address (might be local as well!?!)
            res = res + '/PMS(' + quote_plus(PMSaddress) + ')' + key
            """
        elif key.startswith('/'):  # internal full path.
            res = res + PMS_mark + key
        elif key == '':  # internal path
            res = res + PMS_mark + self.path[srcXML]
        else:  # internal path, add-on
            res = res + PMS_mark + self.path[srcXML] + '/' + key


        return res

    
    def ATTRIB_VIDEOURL(self, src, srcXML, param):
        Video, leftover = self.getElement(src, srcXML, param)
        partIndex, leftover, dfltd = self.getKey(src, srcXML, leftover)
        partIndex = int(partIndex) if partIndex else 0
    
        AuthToken = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'accesstoken')
        
        if not Video:
            dprint(__name__, 0, "VIDEOURL - VIDEO element not found: {0}", param)
            res = 'VIDEO_ELEMENT_NOT_FOUND'  # not found?
            return res
        
        # complete video structure - request transcoding if needed
        Media = Video.find('Media')
        
        # check "Media" element and get key
        if Media!=None:
            # transcoder action
            transcoderAction = g_ATVSettings.getSetting(self.ATV_udid, 'transcoderaction')
            
            # video format
            #    HTTP live stream
            # or native aTV media
            videoATVNative = \
                Media.get('protocol','-') in ("hls") \
                or \
                Media.get('container','-') in ("mov", "mp4") and \
                Media.get('videoCodec','-') in ("mpeg4", "h264", "drmi") and \
                Media.get('audioCodec','-') in ("aac", "ac3", "drms")
            
            for Stream in Media.find('Part').findall('Stream'):
                if Stream.get('streamType','') == '1' and\
                    Stream.get('codec','-') in ("mpeg4", "h264"):
                        if Stream.get('profile', '-') == 'high 10' or \
                            int(Stream.get('refFrames','0')) > 8:
                                videoATVNative = False
                        break
            
            dprint(__name__, 2, "video: ATVNative - {0}", videoATVNative)
            
            # quality limits: quality=(resolution, quality, bitrate)
            qLookup = { '480p 2.0Mbps' :('720x480', '60', '2000'), \
                '720p 3.0Mbps' :('1280x720', '75', '3000'), \
                '720p 4.0Mbps' :('1280x720', '100', '4000'), \
                '1080p 8.0Mbps' :('1920x1080', '60', '8000'), \
                '1080p 10.0Mbps' :('1920x1080', '75', '10000'), \
                '1080p 12.0Mbps' :('1920x1080', '90', '12000'), \
                '1080p 20.0Mbps' :('1920x1080', '100', '20000'), \
                '1080p 40.0Mbps' :('1920x1080', '100', '40000') }
            if PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'local')=='1':
                qLimits = qLookup[g_ATVSettings.getSetting(self.ATV_udid, 'transcodequality')]
            else:
                qLimits = qLookup[g_ATVSettings.getSetting(self.ATV_udid, 'remotebitrate')]
            
            # subtitle renderer, subtitle selection
            subtitleRenderer = g_ATVSettings.getSetting(self.ATV_udid, 'subtitlerenderer')
            
            subtitleId = ''
            subtitleKey = ''
            subtitleFormat = ''
            for Stream in Media.find('Part').findall('Stream'):  # Todo: check 'Part' existance, deal with multi part video
                if Stream.get('streamType','') == '3' and\
                    Stream.get('selected','0') == '1':
                        subtitleId = Stream.get('id','')
                        subtitleKey = Stream.get('key','')
                        subtitleFormat = Stream.get('format','')
                        break
            
            subtitleIOSNative = \
                subtitleKey=='' and subtitleFormat=="tx3g"  # embedded
            subtitlePlexConnect = \
                subtitleKey!='' and subtitleFormat=="srt"  # external
            
            # subtitle suitable for direct play?
            #    no subtitle
            # or 'Auto'    with subtitle by iOS or PlexConnect
            # or 'iOS,PMS' with subtitle by iOS
            subtitleDirectPlay = \
                subtitleId=='' \
                or \
                subtitleRenderer=='Auto' and \
                ( (videoATVNative and subtitleIOSNative) or subtitlePlexConnect ) \
                or \
                subtitleRenderer=='iOS, PMS' and \
                (videoATVNative and subtitleIOSNative)
            dprint(__name__, 2, "subtitle: IOSNative - {0}, PlexConnect - {1}, DirectPlay - {2}", subtitleIOSNative, subtitlePlexConnect, subtitleDirectPlay)
            
            # determine video URL
            if transcoderAction=='DirectPlay' \
                or \
                transcoderAction=='Auto' and \
                videoATVNative and \
                int(Media.get('bitrate','0')) < int(qLimits[2]) and \
                subtitleDirectPlay:
                    # direct play for...
                    #    force direct play
                    # or videoATVNative (HTTP live stream m4v/h264/aac...)
                    #    limited by quality setting
                    #    with aTV supported subtitle (iOS embedded tx3g, PlexConnext external srt)
                    res, leftover, dfltd = self.getKey(Media, srcXML, 'Part['+str(partIndex+1)+']/key')
                    
                    if Media.get('indirect', False):  # indirect... todo: select suitable resolution, today we just take first Media
                        PMS = PlexAPI.getXMLFromPMS(self.PMS_baseURL, res, self.options, AuthToken)  # todo... check key for trailing '/' or even 'http'
                        res, leftover, dfltd = self.getKey(PMS.getroot(), srcXML, 'Video/Media/Part['+str(partIndex+1)+']/key')
                    
                    res = PlexAPI.getDirectVideoPath(res, AuthToken)
            else:
                # request transcoding
                res = Video.get('key','')
                
                # misc settings: subtitlesize, audioboost
                subtitle = { 'selected': '1' if subtitleId else '0', \
                    'dontBurnIn': '1' if subtitleDirectPlay else '0', \
                    'size': g_ATVSettings.getSetting(self.ATV_udid, 'subtitlesize') }
                audio = { 'boost': g_ATVSettings.getSetting(self.ATV_udid, 'audioboost') }
                res = PlexAPI.getTranscodeVideoPath(res, AuthToken, self.options, transcoderAction, qLimits, subtitle, audio, partIndex)
        
        else:
            dprint(__name__, 0, "VIDEOURL - MEDIA element not found: {0}", param)
            res = 'MEDIA_ELEMENT_NOT_FOUND'  # not found?
        
        if res.startswith('/'):  # internal full path.
            res = self.PMS_baseURL + res
        elif res.startswith('http://') or res.startswith('https://'):  # external address
            pass
        else:  # internal path, add-on
            res = self.PMS_baseURL + self.path[srcXML] + res
        
        dprint(__name__, 1, 'VideoURL: {0}', res)
        return res
    
    def ATTRIB_episodestring(self, src, srcXML, param):
        parentIndex, leftover, dfltd = self.getKey(src, srcXML, param)  # getKey "defaults" if nothing found.
        index, leftover, dfltd = self.getKey(src, srcXML, leftover)
        title, leftover, dfltd = self.getKey(src, srcXML, leftover)
        out = self._("{0:0d}x{1:02d} {2}").format(int(parentIndex), int(index), title)
        return out
    
    def ATTRIB_durationToString(self, src, srcXML, param):
        type, leftover, dfltd = self.getKey(src, srcXML, param)
        duration, leftover, dfltd = self.getKey(src, srcXML, leftover)
        if type == 'Video':
            min = int(duration)/1000/60
            if g_ATVSettings.getSetting(self.ATV_udid, 'durationformat') == 'Minutes':
                return self._("{0:d} Minutes").format(min)
            else:
                if len(duration) > 0:
                    hour = min/60
                    min = min%60
                    if hour == 0: return self._("{0:d} Minutes").format(min)
                    else: return self._("{0:d}hr {1:d}min").format(hour, min)
        
        if type == 'Audio':
            secs = int(duration)/1000
            if len(duration) > 0:
                mins = secs/60
                secs = secs%60
                return self._("{0:d}:{1:0>2d}").format(mins, secs)
        
        return ""
    
    def ATTRIB_contentRating(self, src, srcXML, param):
        rating, leftover, dfltd = self.getKey(src, srcXML, param)
        if rating.find('/') != -1:
            parts = rating.split('/')
            return parts[1]
        else:
            return rating
    
    def ATTRIB_unwatchedCountGrid(self, src, srcXML, param):
        total, leftover, dfltd = self.getKey(src, srcXML, param)
        viewed, leftover, dfltd = self.getKey(src, srcXML, leftover)
        unwatched = int(total) - int(viewed)
        return str(unwatched)
    
    def ATTRIB_unwatchedCountList(self, src, srcXML, param):
        total, leftover, dfltd = self.getKey(src, srcXML, param)
        viewed, leftover, dfltd = self.getKey(src, srcXML, leftover)
        unwatched = int(total) - int(viewed)
        if unwatched > 0: return self._("{0} unwatched").format(unwatched)
        else: return ""
    
    def ATTRIB_TEXT(self, src, srcXML, param):
        return self._(param)
    
    def ATTRIB_PMSCOUNT(self, src, srcXML, param):
        return str(PlexAPI.getPMSCount(self.ATV_udid))
    
    def ATTRIB_PMSNAME(self, src, srcXML, param):
        PMS_name = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'name')
        if PMS_name=='':
            return "No Server in Proximity"
        else:
            return PMS_name
    def ATTRIB_LFBG(self, src, srcXML, param):
        import PILBackgrounds
        res = ""
        res = PILBackgrounds.generate(self, src, srcXML, param)
        if res == "":
            res = sys.path[0]+'/assets/fanart/bg.jpg'
        dprint(__name__, 1, 'serving: {0}', res+".png")  # Debug
        return res
          
    def ATTRIB_getBackground(self, src, srcXML, param):
        import PILBackgrounds
        conf = PILBackgrounds.ImageBackground(eval(param))
        res = conf.generate()
        return res

    def ATTRIB_FanartCOUNT(self, src, srcXML, param):
        isfile = os.path.isfile
        join = os.path.join
        
        directory = sys.path[0]+"/assets/fanartcache" 
        res = sum(1 for item in os.listdir(directory) if isfile(join(directory, item)))
        
        return str(res)
        
    
    
    



if __name__=="__main__":
    cfg = Settings.CSettings()
    param = {}
    param['CSettings'] = cfg
    
    param['HostToIntercept'] = 'trailers.apple.com'
    setParams(param)
    
    cfg = ATVSettings.CATVSettings()
    setATVSettings(cfg)
    
    print "load PMS XML"
    _XML = '<PMS number="1" string="Hello"> \
    <DATA number="42" string="World"></DATA> \
    <DATA string="Sun"></DATA> \
    </PMS>'
    PMSroot = etree.fromstring(_XML)
    PMSTree = etree.ElementTree(PMSroot)
    print prettyXML(PMSTree)
    
    print
    print "load aTV XML template"
    _XML = '<aTV> \
    <INFO num="{{VAL(number)}}" str="{{VAL(string)}}">Info</INFO> \
    <FILE str="{{VAL(string)}}" strconv="{{VAL(string::World=big|Moon=small|Sun=huge)}}" num="{{VAL(number:5)}}" numfunc="{{EVAL(int({{VAL(number:5)}}/10))}}"> \
    File{{COPY(DATA)}} \
    </FILE> \
    <PATH path="{{ADDPATH(file:unknown)}}" /> \
    <accessories> \
    <cut />{{CUT(number::0=cut|1=)}} \
    <dontcut />{{CUT(attribnotfound)}} \
    </accessories> \
    <ADDPATH>{{ADDPATH(string)}}</ADDPATH> \
    <COPY2>={{COPY(DATA)}}=</COPY2> \
    </aTV>'
    aTVroot = etree.fromstring(_XML)
    aTVTree = etree.ElementTree(aTVroot)
    print prettyXML(aTVTree)
    
    print
    print "unpack PlexConnect COPY/CUT commands"
    options = {}
    options['PlexConnectUDID'] = '007'
    PMS_address = 'PMS_IP'
    CommandCollection = CCommandCollection(options, PMSroot, PMS_address, '/library/sections')
    XML_ExpandTree(CommandCollection, aTVroot, PMSroot, 'main')
    XML_ExpandAllAttrib(CommandCollection, aTVroot, PMSroot, 'main')
    del CommandCollection
    
    print
    print "resulting aTV XML"
    print prettyXML(aTVTree)
    
    print
    #print "store aTV XML"
    #str = prettyXML(aTVTree)
    #f=open(sys.path[0]+'/XML/aTV_fromTmpl.xml', 'w')
    #f.write(str)
    #f.close()
    
    del cfg
