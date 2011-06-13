import re

PLUGIN_TITLE = 'South Park'
PLUGIN_PREFIX = '/video/southpark'

URLS = [
  ['Denmark', 'http://www.southparkstudios.dk', '%s/guide/', '%s/guide/season/%%s/'],
  ['Finland', 'http://www.southparkstudios.fi', '%s/guide/', '%s/guide/season/%%s/'],
  ['Germany', 'http://www.southpark.de', '%s/episodenguide/', '%s/episodenguide/staffel/%%s/'],
  ['Germany (with original audio)', 'http://www.southpark.de', '%s/episodenguide/', '%s/episodenguide/staffel/%%s/'],
  ['The Netherlands', 'http://www.southpark.nl', '%s/guide/', '%s/guide/season/%%s/'],
  ['Norway', 'http://www.southparkstudios.no', '%s/guide/', '%s/guide/season/%%s/'],
  ['Sweden', 'http://www.southparkstudios.se', '%s/guide/', '%s/guide/season/%%s/'],
  ['United States', 'http://www.southparkstudios.com', '%s/guide/episodes', '%s/guide/episodes/season-%%s']]

THUMB_URL = 'http://southparkstudios-intl.mtvnimages.com/shared/sps/images/south_park/episode_thumbnails/s%se%s_480.jpg'

PLUGIN_ARTWORK = 'art-default.jpg'
PLUGIN_ICON_DEFAULT = 'icon-default.png'
PLUGIN_ICON_PREFS = 'icon-prefs.png'

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)

  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')

  MediaContainer.title1 = PLUGIN_TITLE
  MediaContainer.viewGroup = 'List'
  MediaContainer.art = R(PLUGIN_ARTWORK)

  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'

  SetVolume()

###################################################################################################
def MainMenu():
  dir = MediaContainer(noCache=True)

  if Prefs['country'] != "" and Prefs['country'] != None:
    site = HTML.ElementFromURL(getURLs()[1], errors='ignore')

    if Prefs['country'] == 'United States':
      numSeasons = len( site.xpath('//span[contains(@class,"pagination")]/ol/li') )
    else:
      numSeasons = len( site.xpath('//ol[@class="pagination"]/li') )

    for season in range(1, numSeasons+1):
      title = F("SEASON", str(season))
      dir.Append(Function(DirectoryItem(Episodes, title=title, thumb=R(PLUGIN_ICON_DEFAULT)), title=title, season=str(season)))

  dir.Append(PrefsItem(L("PREFERENCES"), thumb=R(PLUGIN_ICON_PREFS)))
  return dir

####################################################################################################
def Episodes(sender, title, season):
  dir = MediaContainer(title2=title, viewGroup='Details')

  availableEpisodes = HTML.ElementFromURL(getURLs()[2] % season, errors='ignore').xpath('//ul[@id="grid_index"]/li[@class="grid_item"]')

  for episode in availableEpisodes:
    if episode.xpath('.//a[@class="watch_full_episode"]') and episode.xpath('.//span[@class="title eptitle"]/text()[not(contains(.,"To Be Announced"))]'):
      epnumber = episode.xpath('.//span[@class="epnumber"]')[0].text.replace('Episode: ', '')
      numOnly = epnumber.replace(season, '', 1)
      numOnly = numOnly.lstrip('0')
      title = episode.xpath('.//span[@class="title eptitle"]')[0].text.strip()
      summary = episode.xpath('.//span[@class="epdesc"]')[0].text.strip()
      thumb = THUMB_URL % (season.zfill(2), numOnly.zfill(2))
      url = episode.xpath('.//a[@class="watch_full_episode"]')[0].get('href')
      if url[0:4] != 'http':
        url = getURLs()[0] + url

      # Language option for the German website
      if Prefs['country'] == 'Germany (with original audio)':
        url += '?lang=en'

      dir.Append(WebVideoItem(url, title=title, subtitle=F("EPISODE", numOnly), summary=summary, thumb=thumb))

  return dir

####################################################################################################
def getURLs():
  for country, base_url, guide_url, seasonguide_url in URLS:
    if Prefs['country'] == country:
      return [base_url, (guide_url % base_url), (seasonguide_url % base_url)]

###################################################################################################
def SetVolume():
  # Set Flash cookie with volume at max and mute turned off
  try:
    sol = AMF.SOL('media.mtvnservices.com', 'userPrefs4')
    sol.setdefault(u'userPrefs4', {})
    sol[u'userPrefs4']['volume'] = 1
    sol[u'userPrefs4']['isMute'] = False
    sol.save()
  except:
    Log("Shared Objects folder or Flash cookie 'userPrefs4' does not (yet) exist")
