from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import datetime
import json
import urllib
import urlparse

from googleplus import utils
from googleplus.models import GooglePlusUser

GOOGLEPLUS_LOGIN_URL = '/googleplus/login/'
REDIRECT_URI = urlparse.urljoin( \
    'http://' + Site.objects.get_current().domain, GOOGLEPLUS_LOGIN_URL
)

def login_handler(request):
    """Google+ OAuth2 login handler.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    
    if 'error' in request.GET:
        messages.add_message(request, messages.ERROR, 
                             request.GET['error'])
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    elif 'code' in request.GET:
        params = { \
            'client_id': settings.GOOGLEPLUS_CLIENT_ID, \
            'redirect_uri': REDIRECT_URI, \
            'client_secret': settings.GOOGLEPLUS_CLIENT_SECRET, \
            'code': request.GET['code'], \
            'grant_type': 'authorization_code', \
        }
        req = urllib.urlopen('https://accounts.google.com/o/oauth2/token',
            urllib.urlencode(params)
        )
        if req.getcode() != 200:
            response = render_to_response('500.html', {}, \
                               context_instance=RequestContext(request))
            response.status_code = 500
            return response
        
        response = req.read()
        response_query_dict = json.loads(response)
        access_token = response_query_dict['access_token']
        expires_in = response_query_dict['expires_in']
        
        profile = utils.graph_api('people/me', {'access_token': access_token})
        
        googleplus_user = _create_or_update_googleplus_user(profile, access_token, expires_in)
        
        user = authenticate(googleplus_user=googleplus_user)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session.set_expiry(googleplus_user.expiry_at)
                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.add_message(request, messages.ERROR, "Account disabled.")
        else:
            messages.add_message(request, messages.ERROR, "Login failed.")
    else:
        params = { \
            'client_id': settings.GOOGLEPLUS_CLIENT_ID, \
            'redirect_uri': REDIRECT_URI, \
            'scope': 'https://www.googleapis.com/auth/plus.me', \
            'response_type': 'code', \
        }    
        return HttpResponseRedirect('https://accounts.google.com/o/oauth2/auth?' +
            urllib.urlencode(params)
        )

def _create_or_update_googleplus_user(profile, access_token, expires_in):
    """Creates or updates a Google+ user profile in local database.
    """
    user_is_created = False
    try:
        googleplus_user = GooglePlusUser.objects.get(googleplus_id=profile['id'])
    except GooglePlusUser.DoesNotExist:
        first_name, last_name = _get_first_and_last_name(profile['displayName'])
        user = User.objects.create( \
            first_name=first_name,
            last_name=last_name,
            username='googleplus_' + profile['id']
        )
        user_is_created = True
        
    if user_is_created:
        googleplus_user = GooglePlusUser()
        googleplus_user.googleplus_id = profile['id']
        googleplus_user.user = user
    else:
        first_name, last_name = _get_first_and_last_name(profile['displayName'])
        googleplus_user.user.first_name = first_name
        googleplus_user.last_name = last_name
        
    googleplus_user.googleplus_display_name = profile['displayName']
    googleplus_user.access_token = access_token
    googleplus_user.expiry_at = datetime.datetime.now() + \
        datetime.timedelta(seconds=int(expires_in))    
    googleplus_user.save()
    
    return googleplus_user

def _get_first_and_last_name(display_name):
    try:
        first_name, last_name = display_name.strip().rsplit(' ', 1)
    except ValueError:
        first_name = display_name
        last_name = ''
    return first_name, last_name
