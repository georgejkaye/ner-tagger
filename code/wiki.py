# The wikification code provided on canvas
import sys, http.client, urllib.request, urllib.parse, urllib.error, json
import re

from pprint import pprint

def get_url( domain, url ) :

  # Headers are used if you need authentication
  headers = {}

  # If you know something might fail - ALWAYS place it in a try ... except
  try:
    conn = http.client.HTTPSConnection( domain )
    conn.request("GET", url, "", headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data 
  except Exception as e:
    # These are standard elements in every error.
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

  # Failed to get data!
  return None


# Development of the code on canvas
# wiki a query, returning a number representing its results
# 0: person
# 1: organisation
# 2: location
# 3: nothing found
def wiki (query, num) :

  if num == 5 :
    return 3
  
  # This makes sure that any funny charecters (including spaces) in the query are
  # modified to a format that url's accept.
  query = urllib.parse.quote_plus( query )

  # Call our function.
  url_data = get_url( 'en.wikipedia.org', '/w/api.php?action=query&prop=revisions&&rvprop=content&format=json&titles=' + query )

  # We know how our function fails - graceful exit if we have failed.
  if url_data is None :
    print( "Failed to get data ... Can not proceed." )
    # Graceful exit.
    sys.exit()

  # http.client socket returns bytes - we convert this to utf-8
  url_data = url_data.decode( "utf-8" ) 

  # Convert the structured json string into a python variable 
  url_data = json.loads( url_data )

  # MY CODE STARTS HERE
  # regex patterns for hyperlinks and the infobox
  hyper = '\[\[(.*?)]]'
  infobox = '{{Infobox(.*?)}}'
  redirect = '#REDIRECT \[\[(.*?)]]'

  # buzzwords (common infobox types and fields)
  location = ["place", "country", "region", "city", "town", "population", "grid_reference", "area", "demonym", "postcode", "state"]
  organisation = ["company", "government agency", "political party", "law enforcement agency", "fire department", "space agency", "military unit", "military rank", "religion", "church", "diocese", "monastery", "journal", "magazine", "newspaper", "publisher", "website", "accounting body", "institute", "laboratory", "museum", "observatory", "school", "university"]
  person = ["writer", "person", "birth", "born", "personal information"]

  try :
    for n in url_data['query']['pages'] :

      # if page doesn't exist return nothing found
      if str(n) == "-1" :
        return 3

      # get the content of the page
      try:
        content = url_data['query']['pages'][n]['revisions']
      except Exception as e :
        return 3
    
      # convert the content to a string for simplicity
      content = str(content)
    
      # check if the page is a redirect, if yes go to that page
      redir = re.search(redirect, content)
      if redir :
        return wiki(redir.group(1), num + 1)
    
      # if it's a disambiguation page, wiki the first option
      if "may refer to" in content :
        link = re.search(hyper, content)
        nextpage = link.group(1)
        return wiki(nextpage, num + 1)

    # look for the infobox
      else:

        infobox = re.search(infobox, content)

        # if there isn't an infobox just return nothing found
        if infobox :
          infobox = infobox.group(1)
        else :
          return 3
      
        # look to see if any of the buzzwords are in the infobox
        for x in person :
          if x in infobox :
            return 0
        for x in organisation :
          if x in infobox :
            return 1
        for x in location :
          if x in infobox :
            return 2
      
        return 3
  except KeyError as k:
    return 3
       
