NAME = 'South Park'
BASE_URL = 'http://southpark.cc.com'
GUIDE_URL = BASE_URL + '/full-episodes'
RANDOM_URL = BASE_URL + '/full-episodes/random'

RE_SEASON_EPISODE = Regex('full-episodes\/s([0-9]+)e([0-9]+)')
RE_IMAGE_URL = Regex("background-image:url\('(.*\.jpg)")

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'

###################################################################################################
@handler('/video/southpark', NAME)
def MainMenu():

	oc = ObjectContainer(no_cache=True)

	oc.add(
		VideoClipObject(
			url = RandomEpisode(),
			title = L('RANDOM_TITLE')
		)
	)

	num_seasons = int(HTML.ElementFromURL(GUIDE_URL).xpath('//span[contains(@class, "active seasonFilter")]/@data-value')[0])

	for season in range(1, num_seasons+1):
		title = F("SEASON", str(season))
		oc.add(
			DirectoryObject(
				key = Callback(Episodes, title=title, season=str(season)),
				title = title
			)
		)

	oc.add(
		SearchDirectoryObject(identifier='com.plexapp.plugins.southpark', title=L('Search'), prompt=L('Search Episodes'), term=L('videos'))
	)

	return oc

####################################################################################################
@route('/video/southpark/episodes')
def Episodes(title, season):

	oc = ObjectContainer(title2=title)

	pageElement = HTML.ElementFromURL(GUIDE_URL)
	
	for episode_data in pageElement.xpath("//*[@data-view='carousel']//*[@data-sort-value=" + season + "]//*[@class='thumb ']"):
		url = episode_data.xpath(".//a/@href")[0]

		try:
			index = int(RE_SEASON_EPISODE.search(url).groups()[1])
		except:
			continue
			
		title = episode_data.xpath(".//*[@class='title']/text()")[0].strip()
		summary = episode_data.xpath(".//*[@class='episode']/text()")[0].strip()
		thumb = RE_IMAGE_URL.search(episode_data.xpath(".//a/@style")[0]).groups()[0]
		
		oc.add(
			EpisodeObject(
				url = url,
				title = title,
				summary = summary,
				index = index,
				season = int(season),
				thumb = thumb
			)
		)

	if len(oc) < 1:
		return ObjectContainer(header="Empty", message="This season doesn't contain any episodes.")
	else:
		oc.objects.sort(key = lambda obj: obj.index)
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
