VIDEO_PREFIX = "/video/lovefilm-player"

NAME = "LoveFilm Player"

ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_SEARCH = 'icon-search.png'

ACTION_URL = 'http://www.lovefilm.com/browse/film/watch-online/subscription/action/?rows=50'
CHILDREN_URL = 'http://www.lovefilm.com/browse/film/watch-online/subscription/childrens/?rows=50'
COMEDY_URL = 'http://www.lovefilm.com/browse/film/watch-online/subscription/comedy/?rows=50'
DRAMA_URL = 'http://www.lovefilm.com/browse/film/watch-online/subscription/drama/?rows=50'
HORROR_URL = 'http://www.lovefilm.com/browse/film/watch-online/subscription/horror/?rows=50'
THRILLER_URL = 'http://www.lovefilm.com/browse/film/watch-online/subscription/thriller/?rows=50'
TV_URL = 'http://www.lovefilm.com/browse/film/watch-online/subscription/television/?rows=50'

SEARCH_URL = 'http://www.lovefilm.com/browse/film/watch-online/subscription/?query=%s'

####################################################################################################
def Start():
    
    # Initialize the plugin
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode = "InfoList", mediaType = "items")
    
    # Setup the artwork associated with the plugin
    MediaContainer.title1 = NAME
    MediaContainer.art = R(ART)
    MediaContainer.content = 'Items'

####################################################################################################

def MainMenu():
    dir = MediaContainer(viewGroup='InfoList')
    
    dir.Append(Function(DirectoryItem(ListItems, "Action", thumb = R(ICON)), url = ACTION_URL))
    dir.Append(Function(DirectoryItem(ListItems, "Children", thumb = R(ICON)), url = CHILDREN_URL))
    dir.Append(Function(DirectoryItem(ListItems, "Comedy", thumb = R(ICON)), url = COMEDY_URL))
    dir.Append(Function(DirectoryItem(ListItems, "Drama", thumb = R(ICON)), url = DRAMA_URL))
    dir.Append(Function(DirectoryItem(ListItems, "Horror", thumb = R(ICON)), url = HORROR_URL))
    dir.Append(Function(DirectoryItem(ListItems, "Thriller", thumb = R(ICON)), url = THRILLER_URL))
    dir.Append(Function(DirectoryItem(ListItems, "TV", thumb = R(ICON)), url = TV_URL))
    dir.Append(Function(InputDirectoryItem(SearchMenu, "Search", "Please enter the name of the title to search...", thumb=R(ICON_SEARCH))))
    
    # Preferences
    dir.Append(PrefsItem(L('Preferences'), thumb=R('icon-prefs.png')))
    
    return dir

####################################################################################################

def SearchMenu(sender, query=None):
    return ListItems(sender, SEARCH_URL % String.Quote(query))

####################################################################################################

def ListItems(sender, url, replaceParent = False):
    dir = MediaContainer(viewGroup = 'InfoList', title2 = sender.itemTitle, thumb = R(ICON), replaceParent = replaceParent)
    
    # Iterate over the film items located within the page...
    page = HTML.ElementFromURL(url)
    for pageItem in page.xpath("//div[@id='film_listings']//div[@class='film_listing sd open fl_detail ']"):
    
        # Determine the URL and Title from the page.
        url = pageItem.xpath(".//h2/a")[0].get('href')
        title = pageItem.xpath(".//h2/a/text()")[0]

        # [Optional]
        summary = None
        try: summary = pageItem.xpath(".//div[@class='read_more']/text()")[0]
        except: pass

        # [Optional]
        release_decade = None
        try: release_decade = pageItem.xpath(".//h2//span/text()")[0]
        except: pass

        # [Optional]
        rating = None
        try: rating = float(pageItem.xpath(".//li[@property='v:rating']")[0].get('content')) * 2
        except: pass

        # [Optional]
        cover_art = None
        try: cover_art = pageItem.xpath(".//img")[0].get('src')
        except: pass
        
        # [Optional]
        directors = None
        try: directors = [item.strip() for item in pageItem.xpath(".//div[contains(text(), 'Director: ')]/a/text()") ]
        except: pass
        
        summary_format = "%s \n\n%s%s"
        if directors != None:
            summary = summary_format % (summary, "Director(s): ", ", ".join(directors))
        
        # [Optional]
        staring = None
        try: staring = [item.strip() for item in pageItem.xpath(".//div[contains(text(), 'Starring: ')]/a/text()") ]
        except: pass

        if staring != None:
            summary = summary_format % (summary, "Staring: ", ", ".join(staring))
    
        # [Optional]
        certificate = None
        try: certificate = pageItem.xpath(".//div[@class='certif']/img")[0].get('alt')
        except: pass
                
        if certificate != None:
            summary = summary_format % (summary, "Certificate: ", certificate)
        
        dir.Append(WebVideoItem(
            url.replace('http://','https://'),
            title = title,
            subtitle = release_decade,
            summary = summary,
            userRating = rating,
            thumb = cover_art)) 
    
    # If we can find the list item associated with the "Next" url, then we should display an additional option to allow
    # the user navigate further. The next results will replace the current DirectoryItem.
    next = page.xpath("//li/a[contains(text(), 'Next >')]")
    if len(next) > 0:
        next_url = next[0].get('href')
        dir.Append(Function(DirectoryItem(ListItems, "Next...", thumb = R(ICON)), url = next_url, replaceParent = True))
    
    # Check to see if we've found anything
    if len(dir) == 0:
        return MessageContainer("Error", "No titles were found!")

    return dir