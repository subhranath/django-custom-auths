import json
import urllib
import urlparse

def api(path, params, method="GET"):
    """Invokes the Google+ API.
    Returns the response as python dictionary.
    """
    # Construct the API url.
    base_url = 'https://www.googleapis.com/plus/v1/'
    url = urlparse.urljoin(base_url, path)
    
    # Invoke the Google+ API with the specified method. 
    if method.upper() == "GET":
        req = urllib.urlopen(url + '?' + urllib.urlencode(params))
    elif method.upper() == "POST":
        req = urllib.urlopen(url, urllib.urlencode(params))
    
    response = req.read()
    response_dict = json.loads(response)
    
    return response_dict
