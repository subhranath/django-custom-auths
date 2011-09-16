from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed,\
    HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import urllib
import urlparse

from facebook import helpers, utils
from facebook.models import FacebookUser

FACEBOOK_LOGIN_URL = '/facebook/login/'
#FACEBOOK_LOGIN_URL = reverse('facebook.views.login_handler')
REDIRECT_URI = urlparse.urljoin( \
    'http://' + Site.objects.get_current().domain, FACEBOOK_LOGIN_URL
)

def login_handler(request):
    """Login handler.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    
    if 'error' in request.GET:
        messages.add_message(request, messages.ERROR, 
                             request.GET['error_description'])
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    elif 'code' in request.GET:
        params = { \
            'client_id': settings.FACEBOOK_APP_ID, \
            'redirect_uri': REDIRECT_URI, \
            'client_secret': settings.FACEBOOK_APP_SECRET, \
            'code': request.GET['code'], \
        }
        req = urllib.urlopen('https://graph.facebook.com/oauth/access_token?' +
            urllib.urlencode(params)
        )
        if req.getcode() != 200:
            response = render_to_response('500.html', {}, \
                               context_instance=RequestContext(request))
            response.status_code = 500
            return response
        
        response = req.read()
        response_query_dict = dict(urlparse.parse_qsl(response))
        access_token = response_query_dict['access_token']
        expires = response_query_dict['expires']
        
        profile = utils.graph_api('/me', {'access_token': access_token})
        
        fb_user = _create_or_update_facebook_user(profile, access_token, expires)
        
        user = authenticate(fb_user=fb_user)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session.set_expiry(fb_user.expiry_at)
                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.add_message(request, messages.ERROR, "Account disabled.")
        else:
            messages.add_message(request, messages.ERROR, "Login failed.")
    else:
        params = { \
            'client_id': settings.FACEBOOK_APP_ID, \
            'redirect_uri': REDIRECT_URI, \
        }
        if settings.FACEBOOK_APP_PERMISSIONS:
            params['scope'] = settings.FACEBOOK_APP_PERMISSIONS
            
        return HttpResponseRedirect('https://www.facebook.com/dialog/oauth?' +
            urllib.urlencode(params)
        )

def _create_or_update_facebook_user(profile, access_token, expires):
    """Creates or updates a facebook user profile in local database.
    """
    user_is_created = False
    try:
        fb_user = FacebookUser.objects.get(fb_id=profile['id'])
    except FacebookUser.DoesNotExist:
        user = User.objects.create( \
            first_name=profile['first_name'],
            last_name=profile['last_name']
        )
        user_is_created = True
        
    if user_is_created:
        fb_user = FacebookUser()
        fb_user.fb_id = profile['id']
        fb_user.user = user
    else:
        fb_user.user.first_name = profile['first_name']
        fb_user.last_name = profile['last_name']
        
    fb_user.fb_username = profile['username']
    fb_user.access_token = access_token
    fb_user.expiry_at = datetime.datetime.now() + \
        datetime.timedelta(seconds=int(expires))    
    fb_user.save()
    
    return fb_user

@csrf_exempt
def deauthorize_handler(request):
    """Deauthorize handler.
    """
    if request.method == "GET":
        return HttpResponseNotAllowed(['POST'])
    else:
        if 'signed_request' in request.POST:
            signed_request_dict = helpers.unpack_signed_request( \
                request.POST['signed_request'], settings.FACEBOOK_APP_SECRET \
            )
            if signed_request_dict:
                _deauthorize_user(signed_request_dict['user_id'])
                return HttpResponse(json.dumps({'deauthorized': True}), \
                                    mimetype="application/json")
            else:
                return HttpResponseForbidden('Request not allowed.')
        return HttpResponseBadRequest('Required parameter missing.')

def _deauthorize_user(fb_id):
    """An user has deauthorized the application.
    """
    try:
        fb_user = FacebookUser.objects.get(fb_id=fb_id)
    except FacebookUser.DoesNotExist:
        return None
    #TODO - This is not completed.
    return HttpResponse("Temp done")
