NAME = 'South Park'
THUMB_URL = 'http://southparkstudios.mtvnimages.com/images/south_park/episode_thumbnails/s%se%s_480.jpg'

URLS = {
	'Denmark': {
		'base_url':			'http://www.southparkstudios.dk',
		'guide_url':		'http://www.southparkstudios.dk/guide/episodes/',
		'seasonguide_url':	'http://www.southparkstudios.dk/guide/episodes/season-%s',
		'random_url':		'http://www.southparkstudios.dk/full-episodes/random'
	},
	'Finland': {
		'base_url':			'http://www.southparkstudios.fi',
		'guide_url':		'http://www.southparkstudios.fi/guide/episodes/',
		'seasonguide_url':	'http://www.southparkstudios.fi/guide/episodes/season-%s',
		'random_url':		'http://www.southparkstudios.fi/full-episodes/random'
	},
	'Germany': {
		'base_url':			'http://www.southpark.de',
		'guide_url':		'http://www.southpark.de/guide/episoden/',
		'seasonguide_url':	'http://www.southpark.de/guide/episoden/staffel-%s',
		'random_url':		'http://www.southpark.de/alle-episoden/random'
	},
	'Germany (with original audio)': {
		'base_url':			'http://www.southpark.de',
		'guide_url':		'http://www.southpark.de/guide/episoden/',
		'seasonguide_url':	'http://www.southpark.de/guide/episoden/staffel-%s',
		'random_url':		'http://www.southpark.de/alle-episoden/random'
	},
	'The Netherlands': {
		'base_url':			'http://www.southpark.nl',
		'guide_url':		'http://www.southpark.nl/guide/episodes/',
		'seasonguide_url':	'http://www.southpark.nl/guide/episodes/season-%s',
		'random_url':		'http://www.southpark.nl/full-episodes/random'
	},
	'Norway': {
		'base_url':			'http://www.southparkstudios.no',
		'guide_url':		'http://www.southparkstudios.no/guide/episodes/',
		'seasonguide_url':	'http://www.southparkstudios.no/guide/episodes/season-%s',
		'random_url':		'http://www.southparkstudios.no/full-episodes/random'
	},
	'Sweden': {
		'base_url':			'http://www.southparkstudios.se',
		'guide_url':		'http://www.southparkstudios.se/guide/episodes/',
		'seasonguide_url':	'http://www.southparkstudios.se/guide/episodes/season-%s',
		'random_url':		'http://www.southparkstudios.se/full-episodes/random'
	},
	'United States': {
		'base_url':			'http://www.southparkstudios.com',
		'guide_url':		'http://www.southparkstudios.com/guide/episodes/',
		'seasonguide_url':	'http://www.southparkstudios.com/guide/episodes/season-%s',
		'random_url':		'http://www.southparkstudios.com/full-episodes/random'
	}
}

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:19.0) Gecko/20100101 Firefox/19.0'

###################################################################################################
@handler('/video/southpark', NAME)
def MainMenu():

	oc = ObjectContainer(no_cache=True)

	if Prefs['country'] != "" and Prefs['country'] is not None:
		key = Prefs['country']

		oc.add(VideoClipObject(
			url = RandomEpisode(),
			title = L('RANDOM_TITLE')
		))

		guide_url = HTML.ElementFromURL(URLS[key]['guide_url'])
		num_seasons = len(guide_url.xpath('//*[contains(@class,"pagination")]//li'))

		for season in range(1, num_seasons+1):
			title = F("SEASON", str(season))
			oc.add(DirectoryObject(
				key = Callback(Episodes, title=title, season=str(season)),
				title = title
			))

	oc.add(PrefsObject(title=L("PREFERENCES")))

	return oc

####################################################################################################
@route('/video/southpark/episodes')
def Episodes(title, season):

	oc = ObjectContainer(title2=title)

	key = Prefs['country']
	seasonguide_url = URLS[key]['seasonguide_url']
	available_episodes = HTML.ElementFromURL(seasonguide_url % season).xpath('//ul[@id="grid_index"]/li[@class="grid_item"]')

	for episode in available_episodes:
		if episode.xpath('.//a[@class="watch_full_episode"]') and ('/coming-soon-' not in episode.xpath('.//img')[0].get('src')):
			ep_number = episode.xpath('.//span[@class="epnumber"]')[0].text.replace('Episode: ', '')
			num_only = ep_number.replace(season, '', 1)
			num_only = num_only.lstrip('0')
			title = episode.xpath('.//span[@class="title eptitle"]')[0].text.strip()
			summary = episode.xpath('.//span[@class="epdesc"]')[0].text.strip()
			thumb = THUMB_URL % (season.zfill(2), num_only.zfill(2))
			url = unicode(episode.xpath('.//a[@class="watch_full_episode"]')[0].get('href'))

			if url[0:4] != 'http':
				url = '%s%s' % (URLS[key]['base_url'], url)

		# Language option for the German website
		if Prefs['country'] == 'Germany (with original audio)':
			url = '%s%s' % (url, '?lang=en')

		oc.add(EpisodeObject(
			url = url,
			title = title,
			show = NAME,
			season = int(season),
			index = int(num_only),
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(thumb)
		))

	return oc

###################################################################################################
@route('/video/southpark/episodes/random')
def RandomEpisode():

	key = Prefs['country']
	random_url = URLS[key]['random_url']

	try:
		page = HTTP.Request(random_url, follow_redirects=False).content
	except Ex.RedirectError, e:
		if 'Location' in e.headers:
			url = e.headers['Location']

			if url[0:4] != 'http':
				url = '%s%s' % (URLS[key]['base_url'], url)

			return unicode(url)
