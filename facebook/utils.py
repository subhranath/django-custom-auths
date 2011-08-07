import json
import urllib
import urlparse

def graph_api(path, params, method="GET"):
    """Invokes the facebook Graph API.
    Returns the response as python dictionary.
    """
    # Construct the API url.
    base_url = 'https://graph.facebook.com'
    url = urlparse.urljoin(base_url, path)
    
    # Invoke the Graph API with the specified method. 
    if method.upper() == "GET":
        req = urllib.urlopen(url + '?' + urllib.urlencode(params))
    elif method.upper() == "POST":
        req = urllib.urlopen(url, urllib.urlencode(params))
    
    response = req.read()
    response_dict = json.loads(response)
    
    return response_dict
