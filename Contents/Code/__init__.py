NAME = 'South Park'
THUMB_URL = 'http://southparkstudios.mtvnimages.com/images/south_park/episode_thumbnails/s%se%s_480.jpg'

BASE_URL = 'http://www.southparkstudios.com'
GUIDE_URL = 'http://www.southparkstudios.com/guide/episodes/'
SEASONGUIDE_URL = 'http://www.southparkstudios.com/guide/episodes/season-%s'
RANDOM_URL = 'http://www.southparkstudios.com/full-episodes/random'

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'

###################################################################################################
@handler('/video/southpark', NAME)
def MainMenu():

	oc = ObjectContainer(no_cache=True)

	oc.add(VideoClipObject(
		url = RandomEpisode(),
		title = L('RANDOM_TITLE')
	))

	num_seasons = len(HTML.ElementFromURL(GUIDE_URL).xpath('//*[contains(@class,"pagination")]//li'))

	for season in range(1, num_seasons+1):
		title = F("SEASON", str(season))
		oc.add(DirectoryObject(
			key = Callback(Episodes, title=title, season=str(season)),
			title = title
		))

	return oc

####################################################################################################
@route('/video/southpark/episodes')
def Episodes(title, season):

	oc = ObjectContainer(title2=title)
	available_episodes = HTML.ElementFromURL(SEASONGUIDE_URL % season).xpath('//ul[@id="grid_index"]/li[@class="grid_item"]')

	for episode in available_episodes:
		if not episode.xpath('.//a[@class="watch_full_episode"]'):
			continue

		ep_number = episode.xpath('.//span[@class="epnumber"]')[0].text.replace('Episode: ', '')
		num_only = ep_number.replace(season, '', 1)
		num_only = num_only.lstrip('0')
		title = episode.xpath('.//span[@class="title eptitle"]')[0].text.strip()
		summary = episode.xpath('.//span[@class="epdesc"]')[0].text.strip()
		thumb = THUMB_URL % (season.zfill(2), num_only.zfill(2))
		url = unicode(episode.xpath('.//a[@class="watch_full_episode"]')[0].get('href'))

		if url[0:4] != 'http':
			url = '%s%s' % (BASE_URL, url)

		oc.add(EpisodeObject(
			url = url,
			title = title,
			show = NAME,
			season = int(season),
			index = int(num_only),
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(thumb)
		))

	if len(oc) < 1:
		return ObjectContainer(header="Empty", message="This season doesn't contain any episodes.")
	else:
		return oc

###################################################################################################
@route('/video/southpark/episodes/random')
def RandomEpisode():

	try:
		page = HTTP.Request(RANDOM_URL, follow_redirects=False).content
	except Ex.RedirectError, e:
		if 'Location' in e.headers:
			url = e.headers['Location']

			if url[0:4] != 'http':
				url = '%s%s' % (BASE_URL, url)

			return unicode(url)
