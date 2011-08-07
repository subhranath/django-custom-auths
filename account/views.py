from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from account import forms

def index(request):
    return render_to_response('account/index.html', { \
    }, context_instance=RequestContext(request))
    
def login_handler(request):
    """Login handler.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account.views.index'))
    
    if request.method == 'GET':
        form = forms.LoginForm()
    else:
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if 'next' in request.GET:
                        return HttpResponseRedirect(request.GET['next'])
                    return HttpResponseRedirect(reverse('account.views.index'))
                else:
                    messages.add_message(request, messages.ERROR, "Account disabled.")
            else:
                messages.add_message(request, messages.ERROR, "Login failed.")
        
    return render_to_response('account/login.html', { \
        'form': form, \
    }, context_instance=RequestContext(request))

def logout_handler(request):
    """Logout handler.
    """
    if request.user.is_authenticated():
        logout(request)
        messages.add_message(request, messages.SUCCESS, \
            'You have been successfully logged out.')
    else:
        messages.add_message(request, messages.INFO, \
            'Only authenticated users can be logged out.')
    return HttpResponseRedirect(reverse('account.views.index'))
