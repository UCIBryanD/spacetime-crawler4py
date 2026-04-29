import re
from urllib.parse import urlparse

# custom imports
from bs4 import BeautifulSoup
from urllib.parse import urldefrag
from urllib.parse import parse_qs
from datetime import date
from datetime import datetime
from dateutil.parser import parse as dtparse
from dateutil import tz

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content


    # 601: request malformed
    # 601: download exception
    # 602: spacetime server failure (skip)
    # 603: scheme not http/https (skip)
    # 604: domain not in spec (skip)
    # 605: inappropriate extension (skip)
    # 606: exception in parsing url
    # 607: content too big (check resp.header['content-length'], should also use this to weigh against length)
    # 608: robot rules (skip)
    
    SKIP_STATUS = {403, 404, 602, 603, 604, 605, 608}
    MAX_LENGTH = 1000000 # max allowed content-length
    MIN_LENGTH = 300 # least amount of content length (to be changed, should just avoid empty for now)
    page_links = set() # set of links on page
    viable_links = set() # set of links to add to frontier

    #print(url)
    #print(resp.headers)

    if re.match(r".*(physics.uci.edu)$", url.lower()):
        assert(str(valid_domain) + "  - valid domain of: " + url)


    # if response is empty somehow, raise error and return
    if (resp == None):
        print("NoneType object: " + url)
        assert(url)
        return list()
    
    # if status is not 200, check status if it should be skipped
    if (resp.status != 200):
        if (resp.status in SKIP_STATUS):
            return list() 
        print(str(resp.status) + " not skipped: " + url)


    # check header content here to ensure it's text/html
    if (resp.headers["Content-Type"] != "text/html; charset=utf-8"):
        print(url + " - invalid content-type: " + resp.headers["Content-Type"])
        return list()

    # if page has no content then ignore
    if (resp.raw_response == None or resp.raw_response.content == None):
        print("download error?: " + str(resp.status))
        assert(url)
        return list()    

    # check if response length is within range (min length should be edited relatively)    
    if (len(resp.raw_response.content) < MIN_LENGTH or len(resp.raw_response.content) > MAX_LENGTH):
        print("Size skip: " + str(len(resp.raw_response.content)) + " : " + url)
        return list()


    # use beutiful soup to parse/extract strings from content
    bsoup = BeautifulSoup(resp.raw_response.content, "html.parser")
    
    # check actual contents within with beautifulsoup, check for certain keywords that indicate no info
    keywords = {"no content", "no event", "no events", "content missing"} #no upcoming
    for keyword in keywords:
        if bsoup.find(string=re.compile(keyword, re.IGNORECASE)):
            print(keyword + " found: " + url)
            return list()
    

    # extract all links in <a> tags
    for link in bsoup.find_all("a", href=True):
        page_links.add(link["href"])
    
    # validate each link individually
    for link in page_links:
        #print("validating sublink: " + link)
        # if link is equal to webpage itself, ignore it
        if (url == link):
            continue



        # strip the fragment off of the url and add it to the set (final check)
        if is_valid(link):
            viable_links.add(urldefrag(link).url)


    return list(viable_links)





def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        # check if the link itself is a valid url OR if it is on-page html (# link, javascript)
        if (parsed == None or parsed.hostname == None):
            #print("NoneType: " + url)
            return False

        
        # check scheme to be http or https
        if parsed.scheme not in set(["http", "https"]):
            #print("scheme incorrect")
            return False

        # check to ensure it ISN'T one of these extensions
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
           + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ics)$", parsed.path.lower()): # add ics extension
            #print("extension incorrect")
            return False

        # check that the domain is one of these
        valid_domain = re.match(
            r".*(ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu)$", 
            parsed.hostname.lower())
            
        if not valid_domain:
            #print("Invalid domain, not adding")
            return False

        #print(str(valid_domain) + "  - valid domain of: " + url)
        if re.match(r".*(physics.uci.edu)$", parsed.hostname.lower()):
            assert(str(valid_domain) + "  - valid domain of: " + url)




        
        # check query parameters, limit date range? for now avoid altogether
        # ignore Ical parameter

        year_limit_past = 8        
        year_limit_future = 1
        dt_curr = today = datetime.today().date()
        dt_limit_past = dt_curr.replace(year=today.year - year_limit_past) # limit to pages from 10 years ago
        dt_limit_future = dt_curr.replace(year=today.year + year_limit_future) # limit to pages from 10 years ago
        #print(dt_limit)
        
        
        query_param = dict()
        if (parsed.query != ""):
            query_param = parse_qs(parsed.query.lower())
            #print(query_param)

        bad_keys = {"ical", "outlook-ical", "eventdisplay", "share"}
        #print(query_param.keys())
        for p in query_param.keys():
            if (p in bad_keys):
                return False
        

        for v in query_param.values():
            #print(v[0])
            try:
                #date.fromisoformat(v[0])
                if (dtparse(v[0]) < dt_limit_past or dt_limit_future < dtparse(v[0])):
                #print("skipping: " + v[0])
                    return False # should just return if date can be converted/is iso format
            except:
                continue


        # check path for dates as well, limit date range but avoid altogether for now
        path_param = list()
        if (parsed.path != ""):
            path_param = parsed.path.split('/')[1:]
        for p in path_param:
            #print(p)
            try:
                #dtparse(p)
                #date.fromisoformat(p)

                if (dtparse(p) < dt_limit_past or dt_limit_future < dtparse(p)):
                #print("skipping: " + v[0])
                    return False # should just return if date can be converted/is iso format
                #print("skipping: " + p)
                #return False # should just return if date can be converted/is iso format
            except:
                continue
        

        return True



    except TypeError:
        print ("TypeError for ", parsed)
        raise
