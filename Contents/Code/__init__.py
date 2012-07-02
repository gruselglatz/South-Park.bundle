
PLUGIN_TITLE = 'South Park'
URLS = [
    ['Denmark',				'http://www.southparkstudios.dk',	'%s/guide/episodes/',	  '%s/guide/episodes/season-%%s'],
    ['Finland',				'http://www.southparkstudios.fi',	'%s/guide/episodes/',	  '%s/guide/episodes/season-%%s'],
    ['Germany',				'http://www.southpark.de',	  	'%s/guide/episoden/',	  '%s/guide/episoden/staffel/%%s/'],
    ['Germany (with original audio)',	'http://www.southpark.de',	  	'%s/guide/episoden/',	  '%s/guide/episoden/staffel/%%s/'],
    ['The Netherlands',			'http://www.southpark.nl',	  	'%s/guide/episodes/',	  '%s/guide/episodes/season/%%s/'],
    ['Norway',				'http://www.southparkstudios.no',	'%s/guide/episodes/',	  '%s/guide/episodes/season-%%s'],
    ['Sweden',				'http://www.southparkstudios.se',	'%s/guide/episodes/',	  '%s/guide/episodes/season-%%s'],
    ['United States',			'http://www.southparkstudios.com',  	'%s/guide/episodes/',	  '%s/guide/episodes/season-%%s']
]

THUMB_URL = 'http://southparkstudios-intl.mtvnimages.com/shared/sps/images/south_park/episode_thumbnails/s%se%s_480.jpg'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_PREFS = 'icon-prefs.png'

####################################################################################################
def Start():
    Plugin.AddPrefixHandler('/video/southpark', MainMenu, PLUGIN_TITLE, ICON, ART)

    ObjectContainer.title1 = PLUGIN_TITLE
    ObjectContainer.art = R(ART)
    DirectoryObject.thumb = R(ICON)

    #SetVolume()

###################################################################################################
def MainMenu():
    oc = ObjectContainer(no_cache=True)

    if Prefs['country'] != "" and Prefs['country'] != None:
	site = HTML.ElementFromURL(getURLs()[1], errors='ignore')
	numSeasons = len( site.xpath('//*[contains(@class,"pagination")]//li') )
	url = GetRandom()
	oc.add(VideoClipObject(url=url, title=L('RANDOM_TITLE'), thumb=R(ICON)))
	
	for season in range(1, numSeasons+1):
	    title = F("SEASON", str(season))
	    oc.add(DirectoryObject(key=Callback(Episodes, title=title, season=str(season)), title=title))

    oc.add(PrefsObject(title=L("PREFERENCES"), thumb=R(ICON_PREFS)))
    return oc

####################################################################################################
def Episodes(title, season):
    oc = ObjectContainer(title2=title)

    availableEpisodes = HTML.ElementFromURL(getURLs()[2] % season, errors='ignore').xpath('//ul[@id="grid_index"]/li[@class="grid_item"]')

    for episode in availableEpisodes:
	if episode.xpath('.//a[@class="watch_full_episode"]') and ('/coming-soon-' not in episode.xpath('.//img')[0].get('src')):
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

	    oc.add(EpisodeObject(url=url, title=title, show=PLUGIN_TITLE, season=int(season), index=int(numOnly), summary=summary, thumb=thumb))
    return oc

####################################################################################################
def getURLs():
    for country, base_url, guide_url, seasonguide_url in URLS:
	if Prefs['country'] == country:
	    return [base_url, (guide_url % base_url), (seasonguide_url % base_url)]

###################################################################################################
def GetRandom():
    try:
	content = HTTP.Request(getURLs()[0]+'/full-episodes/random', follow_redirects=False, cacheTime=0).content
    except Ex.RedirectError, e:
	if e.headers.has_key('Location'):
	    redirect_url = e.headers['Location']
    return redirect_url

###################################################################################################
#def SetVolume():
## Set Flash cookie with volume at max and mute turned off
#  try:
#    sol = AMF.SOL('media.mtvnservices.com', 'userPrefs4')
#    sol.setdefault(u'userPrefs4', {})
#    sol[u'userPrefs4']['volume'] = 1
    #sol[u'userPrefs4']['isMute'] = False
#    sol.save()
#  except:
#    Log("Shared Objects folder or Flash cookie 'userPrefs4' does not (yet) exist")
