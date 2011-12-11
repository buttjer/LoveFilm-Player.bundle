import re

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

TV = "^[^-]* - Series \d+.*"
TV_BASIC = "^(?P<series_name>[^-]*) - Series (?P<series_number>\d+) - (?P<episode_name>.*)$"
TV_PARTIAL = "^(?P<series_name>[^-]*) - Series (?P<series_number>\d+), Episode (?P<episode_number>\d+)$"
TV_FULL = "^(?P<series_name>[^-]*) - Series (?P<series_number>\d+), Episode (?P<episode_number>\d+) - (?P<episode_name>.*)$"

####################################################################################################
def Start():
    
    # Initialize the plugin
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode = "InfoList", mediaType = "items")
    
    # Setup the artwork associated with the plugin
    ObjectContainer.title1 = NAME
    ObjectContainer.art = R(ART)
    ObjectContainer.view_group = 'InfoList'
    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)

    # Cache HTTP requests for up to a day
    HTTP.CacheTime = CACHE_1DAY

####################################################################################################

def MainMenu():
    oc = ObjectContainer()
    
    oc.add(DirectoryObject(key = Callback(ListItems, url = ACTION_URL, container_title = "Action"), title = "Action"))
    oc.add(DirectoryObject(key = Callback(ListItems, url = CHILDREN_URL, container_title = "Children"), title = "Children"))
    oc.add(DirectoryObject(key = Callback(ListItems, url = COMEDY_URL, container_title = "Comedy"), title = "Comedy"))
    oc.add(DirectoryObject(key = Callback(ListItems, url = DRAMA_URL, container_title = "Drama"), title = "Drama"))
    oc.add(DirectoryObject(key = Callback(ListItems, url = HORROR_URL, container_title = "Horror"), title = "Horror"))
    oc.add(DirectoryObject(key = Callback(ListItems, url = THRILLER_URL, container_title = "Thriller"), title = "Thriller"))
    oc.add(DirectoryObject(key = Callback(ListItems, url = TV_URL, container_title = "TV"), title = "TV"))
    oc.add(SearchDirectoryObject(identifier="com.plexapp.search.lovefilm-player", title = "Search", prompt = "Please enter the name of the title to search..."))
    
    # Preferences
    oc.add(PrefsObject(title = L('Preferences')))
    
    return oc

####################################################################################################

def ListItems(url, container_title, replace_parent = False):
    oc = ObjectContainer(title2 = container_title, replace_parent = replace_parent)
    
    # Iterate over the film items located within the page...
    page = HTML.ElementFromURL(url)
    for pageItem in page.xpath("//div[@id='film_listings']//div[@class='film_listing sd open fl_detail ']"):
    
        details = ParseItem(pageItem)
        originalTitle = details['title']
        Log("IABI: " + originalTitle)
        
        if re.match(TV, originalTitle) == None:
            oc.add(MovieObject(
                url = details['url'],
                title = details['title'],
                summary = details['summary'],
                year = details['release_decade'],
                rating = details['rating'],
                thumb = Callback(GetThumb, thumb_url = details['thumb']),
                content_rating = details['certificate'],
                directors = details['directors']))
    
        else:

            # There are currently two known formats for TV episode titles seen available on the LoveFilm-Player. Examples of
            # these are as follows:
            #  - "Cracker - Series 03, Episode 06 - True Romance, Part 1"
            #  - "Peep Show - Series 01, Episode 01"
            #  - "Cracker - Series 05 - Nine Eleven"
            title = originalTitle
            show = None
            season = None
            index = None
            index_name = None

            try:
                # We attempt to identify the longer, more detail instance first. If that fails, then we drop back to the more
                # basic.
                more_detailed = re.match(TV_FULL, originalTitle)
                if more_detailed != None:
                    more_detailed_dict = more_detailed.groupdict()
                    if len(more_detailed_dict) > 0:
                        show = more_detailed_dict['series_name']
                        season = int(more_detailed_dict['series_number'])
                        index = int(more_detailed_dict['episode_number'])
                        index_name = more_detailed_dict['episode_name']
                else:
                    # We've failed to match the more detailed version of the title. We should try the partial one now.
                    partial = re.match(TV_PARTIAL, originalTitle)
                    if partial != None:
                        partial_dict = partial.groupdict()
                        if len(partial_dict) > 0:
                            show = partial_dict['series_name']
                            season = int(partial_dict['series_number'])
                            index = int(partial_dict['episode_number'])
                    else:
                        # We've failed AGAIN, so we will try the last known format.
                        basic = re.match(TV_BASIC, originalTitle)
                        if basic != None:
                            basic_dict = basic.groupdict()
                            if len(basic_dict) > 0:
                                show = basic_dict['series_name']
                                season = int(basic_dict['series_number'])
                                index_name = basic_dict['episode_name']
            except:
                # An error has occurred while attempting to extract the details of the episode. To be safe, we will just use
                # the default values
                Log.Exception("Error determining TV episode details")
                pass
                
            oc.add(EpisodeObject(
                url = details['url'],
                title = title,
                show = show,
                season = season,
                index = index,
                summary = details['summary'],
                thumb = Callback(GetThumb, thumb_url = details['thumb']),
                rating = details['rating'],
                directors = details['directors']))
                    
    # If we can find the list item associated with the "Next" url, then we should display an additional option to allow
    # the user navigate further. The next results will replace the current DirectoryItem.
    next = page.xpath("//li/a[contains(text(), 'Next >')]")
    if len(next) > 0:
        next_url = next[0].get('href')
        oc.add(DirectoryObject(key = Callback(ListItems, url = next_url, container_title = container_title, replace_parent = True), title = "Next..."))
    
    # Check to see if we've found anything
    if len(oc) == 0:
        return MessageContainer("Error", "No titles were found!")

    return oc

####################################################################################################

def ParseItem(item):
    details = {}

    details['url'] = item.xpath(".//h2/a")[0].get('href').replace('http://','https://')
    details['title'] = item.xpath(".//h2/a/text()")[0]

    # [Optional]
    details['summary'] = None
    try: details['summary'] = item.xpath(".//div[@class='read_more']/text()")[0]
    except: pass

    # [Optional]
    details['release_decade'] = None
    try: 
        release_decade_text = item.xpath(".//h2//span/text()")[0]
        details['release_decade'] = int(re.match("\((?P<year>[0-9]+)\)", release_decade_text).groupdict()['year'])
    except: pass

    # [Optional]
    details['rating'] = None
    try: details['rating'] = float(item.xpath(".//li[@property='v:rating']")[0].get('content')) * 2
    except: pass

    # [Optional]
    details['thumb'] = None
    try: details['thumb'] = item.xpath(".//img")[0].get('src')
    except: pass

    # [Optional]
    details['directors'] = []
    try: details['directors'] = [item.strip() for item in item.xpath(".//div[contains(text(), 'Director: ')]/a/text()") ]
    except: pass

    # [Optional]
    details['certificate'] = None
    try: details['certificate'] = pageItem.xpath(".//div[@class='certif']/img")[0].get('alt')
    except: pass

    return details

####################################################################################################

def GetThumb(thumb_url):
    try:
        large_thumb = thumb_url[:thumb_url.rfind('-') + 1] + 'large.jpg'
        data = HTTP.Request(large_thumb, cacheTime = CACHE_1MONTH).content
        return DataObject(data, 'image/jpeg')
    except:
        try:
            medium_thumb = thumb_url[:thumb_url.rfind('-') + 1] + 'medium.jpg'
            data = HTTP.Request(medium_thumb, cacheTime = CACHE_1MONTH).content
            return DataObject(data, 'image/jpeg')
        except:
            return Redirect(thumb_url)