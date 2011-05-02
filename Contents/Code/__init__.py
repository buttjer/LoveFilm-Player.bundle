####################################################################################################

VIDEO_PREFIX = "/video/blinkbox"

NAME = L('Title')

ART = 'art-default.png'
ICON = 'icon-default.png'
ICON_COMPUTER = 'icon-movie.png'
ICON_USER = 'icon-user.png'
ICON_SEARCH = 'icon-search.png'

MOVIES_FREE = 'http://www.blinkbox.com/Movies/Free'
TV_FREE = 'http://www.blinkbox.com/TV/Free'

ERROR = MessageContainer('Network Error','A Network error has occurred')

####################################################################################################

# This function is initially called by the PMS framework to initialize the plugin. This includes
# setting up the Plugin static instance along with the displayed artwork.
def Start():
    
    # Initialize the plugin
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, Locale.LocalString('Title'), ICON, ART)
    Plugin.AddViewGroup("Basic", viewMode = "InfoList", mediaType = "items")
    Plugin.AddViewGroup("Basic", viewMode = "List", mediaType = "items")
    
    # Setup the artwork associated with the plugin
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

# This main function will setup the displayed items. This will depend if the user is currently
# logged in.
def MainMenu():
    dir = MediaContainer(disabledViewModes=["Coverflow"], title1 = Locale.LocalString('Title'))
    
    # Movies
    dir.Append(Function(
        DirectoryItem(
            MovieMenu,
            "Movies")))
    
    # TV Shows
    dir.Append(Function(
        DirectoryItem(
            TVMenu,
            "TV Shows")))
    
    return dir

####################################################################################################
# Movies
####################################################################################################

# This is the main function for displaying all available free movies. 
def MovieMenu(sender):
    dir = MediaContainer(disabledViewModes=["Coverflow"], title1="Movies")

    movies = HTTP.Request(MOVIES_FREE)
    movies_free = HTML.ElementFromString(movies)
    
    movie_assets = movies_free.xpath("//div[@class='movieAsset']")
    for movie_asset in movie_assets:
		
        # Parse the movie details to determine all associated content.
        title_details = parseMovieTitle(movie_asset)
        
        dir.Append(WebVideoItem(
            title_details['url'],
            title = title_details['name'],
            subtitle = title_details['subtitle'],
            summary = title_details['description'],
            thumb = title_details['image']))

    return dir

# This function will parse a specific 'movieAsset' to determine the associated information about
# the title.
def parseMovieTitle(item):
    summary_node = item.xpath(".//div[@class='summary']/a")[0]
    
    # Attempt to locate the title's name.
    name = ''
    try:
        name = summary_node.xpath(".//span/text()")[0]
        name = name.lstrip().rstrip()
    except:
        pass
    
    # Attempt to locate the url to the title.
    url = ''
    try:
        url = summary_node.get('href')
    except:
        pass
    
    # Attempt to locate the associated image.
    image = ''
    try:
        image = item.xpath(".//img")[0].get('src')
    except:
        pass
	
    subtitle = ''
    try:
        subtitle = item.xpath(".//div[@class='message']/p/span/text()")[0]
    except:
        pass
    
    description = ''
    try:
        description = item.xpath(".//span[@class='msg']/text()")[0]
    except:
        pass
    
    parsed = {}
    parsed['name'] = name
    parsed['url'] = url
    parsed['image'] = image
    parsed['subtitle'] = subtitle
    parsed['description'] = description
    
    return parsed

####################################################################################################
# TV Shows
####################################################################################################

# This function displays the top level menu for all availabe TV shows. When selected, it will then
# display the available series.
def TVMenu(sender):
    dir = MediaContainer(disabledViewModes=["Coverflow"], title1="TV Shows")

    movies = HTTP.Request(TV_FREE)
    movies_free = HTML.ElementFromString(movies)
    
    movie_assets = movies_free.xpath("//div[@class='movieAsset']")
    for movie_asset in movie_assets:
		
        title_details = parseTvTitle(movie_asset)
        
        dir.Append(Function(
            DirectoryItem(
                TVSeriesMenu,
                title_details['name'],
                subtitle = title_details['subtitle'],
                summary = title_details['description'],
                thumb = title_details['image']),
            name = title_details['name'],
            url = title_details['url']))

    return dir

# This function will parse a specific 'movieAsset' to determine the associated information about
# the title.
def parseTvTitle(item):
    summary_node = item.xpath(".//div[@class='summary']/a")[0]
    
    # Attempt to locate the title's name.
    name = ''
    try:
        name = summary_node.xpath(".//span/text()")[0]
    except:
        pass
    
    # Attempt to locate the url to the title.
    url = ''
    try:
        url = summary_node.get('href')
    except:
        pass
    
    # Attempt to locate the associated image.
    image = ''
    try:
        image = item.xpath(".//img")[0].get('src')
    except:
        pass
	
    subtitle = ''
    try:
        subtitle = item.xpath(".//div[@class='message']/p/text()")[0]
    except:
        pass
    
    description = ''
    try:
        description = item.xpath(".//span[@class='msg']/text()")[0]
    except:
        pass
    
    parsed = {}
    parsed['name'] = name
    parsed['url'] = url
    parsed['image'] = image
    parsed['subtitle'] = subtitle
    parsed['description'] = description
    
    return parsed

# This function displays the individual series available for a specified tv show.
def TVSeriesMenu(sender, name = '', url = ''):
    dir = MediaContainer(disabledViewModes = ["Coverflow"], title1 = sender.title1, title2 = name)

    tv_series_string = HTTP.Request(url)
    tv_series = HTML.ElementFromString(tv_series_string)

    assets = tv_series.xpath("//div[@class='assetDetailed c']")
    for asset in assets:
		
        title_details = parseTvEpisodeTitle(asset)
        
        dir.Append(WebVideoItem(
            title_details['url'],
            title = title_details['name'],
            subtitle = title_details['subtitle'],
            summary = title_details['description'],
            thumb = title_details['image']))
    
    return dir

# This function will parse a specific 'assetDetailed c' to determine the associated information about
# the title.
def parseTvEpisodeTitle(item):
    
    # Attempt to locate the title's name.
    name = ''
    try:
        name = item.xpath(".//p[@class='title']/a/text()")[0]
    except:
        pass
    
    # Attempt to locate the url to the title.
    url = ''
    try:
        node = item.xpath(".//p[@class='title']/a")[0]
        url = node.get('href')
    except:
        pass
    
    # Attempt to locate the associated image.
    image = ''
    try:
        image = item.xpath(".//img")[0].get('src')
    except:
        pass
	
    subtitle = ''
    try:
        subtitle = item.xpath(".//p[@class='header']/text()")[0]
    except:
        pass
    
    description = ''
    try:
        description = item.xpath(".//p[@class='info']/text()")[0]
    except:
        pass
    
    parsed = {}
    parsed['name'] = name
    parsed['url'] = url
    parsed['image'] = image
    parsed['subtitle'] = subtitle
    parsed['description'] = description
    
    return parsed