from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
import re

####################################################################################################

PLUGIN_TITLE = 'South Park'
PLUGIN_PREFIX = '/video/southpark'

URLS = [
  ['Denmark', 'DK', 'http://www.southparkstudios.dk', '%s/guide/', '%s/guide/season/%%s/'],
  ['Finland', 'FI', 'http://www.southparkstudios.fi', '%s/guide/', '%s/guide/season/%%s/'],
  ['Germany', 'DE', 'http://www.southpark.de', '%s/episodenguide/', '%s/episodenguide/staffel/%%s/'],
  ['The Netherlands', 'NL', 'http://www.southpark.nl', '%s/guide/', '%s/guide/season/%%s/'],
  ['Norway', 'NO', 'http://www.southparkstudios.no', '%s/guide/', '%s/guide/season/%%s/'],
  ['Sweden', 'SE', 'http://www.southparkstudios.se', '%s/guide/', '%s/guide/season/%%s/'],
  ['United States', 'US', 'http://www.southparkstudios.com', '%s/guide/', '%s/guide/?season=%%s']]

THUMB_URL = 'http://southparkstudios-intl.mtvnimages.com/shared/sps/images/south_park/episode_thumbnails/s%se%s_480.jpg'
CACHE_INTERVAL = 3600

# Default artwork and icon(s)
PLUGIN_ARTWORK = 'art-default.png'
PLUGIN_ICON_DEFAULT = 'icon-default.png'
PLUGIN_ICON_PREFS = 'icon-prefs.png'

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE)

  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')

  # Set the default MediaContainer attributes
  MediaContainer.title1 = PLUGIN_TITLE
  MediaContainer.viewGroup = 'List'
  MediaContainer.art = R(PLUGIN_ARTWORK)

  # Set the default cache time
  HTTP.SetCacheTime(CACHE_INTERVAL)

###################################################################################################

def CreatePrefs():
  countries = ''
  for country, geo, base_url, guide_url, seasonguide_url in URLS:
    countries += country + '|'
  Prefs.Add(id='country', type='enum', default=geolocate(), label=L("COUNTRY"), values=countries[:-1])
  if geolocate() == 'Germany':
    Prefs.Add(id='lang', type='enum', default='Deutsch', label='Sprache', values='Deutsch|Englisch')

####################################################################################################

def MainMenu():
  dir = MediaContainer(noCache=True)

  if Prefs.Get('country'):
    site = XML.ElementFromURL(getURLs()[1], isHTML=True, errors='ignore')
    numSeasons = len( site.xpath('//ol[@class="pagination"]/li') )

    for season in range(1, numSeasons+1):
      title = F("SEASON", str(season))
      dir.Append(Function(DirectoryItem(Episodes, title=title, thumb=R(PLUGIN_ICON_DEFAULT)), title=title, season=str(season)))

  dir.Append(PrefsItem(L("PREFERENCES"), thumb=R(PLUGIN_ICON_PREFS)))
  return dir

####################################################################################################

def Episodes(sender, title, season):
  dir = MediaContainer(title2=title, viewGroup='Details')

  availableEpisodes = XML.ElementFromURL(getURLs()[2] % season, isHTML=True, errors='ignore').xpath('//ul[@id="grid_index"]/li[@class="grid_item"]')

  for episode in availableEpisodes:
    epnumber = episode.xpath('.//span[@class="epnumber"]/text()')[0].replace('Episode: ', '')
    numOnly = epnumber.replace(season, '', 1)
    numOnly = numOnly.lstrip('0')
    title = episode.xpath('.//span[@class="title eptitle"]/text()')[0].strip()
    summary = episode.xpath('.//span[@class="epdesc"]/text()')[0].strip()
    thumb = THUMB_URL % (season.zfill(2), numOnly.zfill(2))
    videopage = getURLs()[0] + episode.xpath('.//a[@class="watch_full_episode"]')[0].get('href')

    # Language option for the German website
    if geolocate() == 'Germany' and Prefs.Get('lang') == 'Englisch':
      videopage += '?lang=en'

    dir.Append(WebVideoItem(videopage, title=title, subtitle=F("EPISODE", numOnly), summary=summary, thumb=thumb))

  return dir

####################################################################################################

def getURLs():
  c = Prefs.Get('country')
  for country, geo, base_url, guide_url, seasonguide_url in URLS:
    if c == country:
      return [base_url, (guide_url % base_url), (seasonguide_url % base_url)]

####################################################################################################

def geolocate():
  g = Locale.Geolocation()
  for country, geo, base_url, guide_url, seasonguide_url in URLS:
    if g == geo:
      return country
  return 'United States'
