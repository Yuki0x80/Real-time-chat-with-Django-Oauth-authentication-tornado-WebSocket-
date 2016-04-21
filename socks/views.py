#coding:utf-8
from django.contrib import auth
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from socks.models import Message,ChatUser
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import now as utcnow
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext,loader
from django.core.urlresolvers import reverse
import tweepy
import sys, re
import time
from django.shortcuts import render, redirect
from django.http import HttpRequest
import importlib
from django.conf import settings
import MeCab
import csv
import os


CONSUMER_KEY = ''
CONSUMER_SECRET = ''
CALLBACK_URL = 'http://127.0.0.1:8000/get_callback/'


t=open(os.getcwd()+"/socks/sample.csv" ,"rU") 
reader = csv.reader(t)
find=next(reader)
tagger = MeCab.Tagger("-Ochasen")

# if login index.html=chat screen else login screen
def index(request):
	if request.method == 'POST':
		print request.POST
	logged_users = []
	if request.user.username and request.user.profile.is_chat_user:
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(request.session.get('key'), request.session.get('secret'))
		api = tweepy.API(auth_handler=auth)
		#print request.user.username
		u = api.get_user(request.user.username)
		logged_users=u.screen_name
		context = {'logged_users':logged_users}
		return render(request, 'index.html', context)
	else:
		'''
		Twitter OAuth Authenticate
		'''
		auth_tw = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
		try:
			auth_url = auth_tw.get_authorization_url()
		except tweepy.TweepError:
			print 'Error! Failed to get request token. You have to access network'
			return HttpResponseRedirect(reverse('index'))
		request.session['request_token'] = auth_tw.request_token
		request.session.save()
		return HttpResponseRedirect(auth_url)

def get_callback(request):
    '''
    Callback
    '''
    # Example using callback (web app)
    verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token') 
    # Let's say this is a web app, so we need to re-build the auth handler first...
    auth_get = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth_get.set_access_token(oauth_token, verifier) 
    auth_get.request_token = request.session.get('request_token') 
    try:
        auth_get.get_access_token(verifier)
    except tweepy.TweepError:
        print 'Error! Failed to get access token.'
        return HttpResponseRedirect(reverse('index'))
    ###Get access token
    request.session['key'] = auth_get.access_token 
    request.session['secret'] = auth_get.access_token_secret 
    ###Get user_id
    user_id = int(tweepy.API(auth_get).me().id_str)
    #print "auth_username"+auth_get.get_username()

    ###Authentication  DataBase!!:
    user=auth.authenticate(username=auth_get.get_username(), password=auth_get.access_token)
   	#print "user_id",user_id,type(user_id)
    #print "user_name",auth_get.get_username()
    if user is None:
		user = User.objects.create_user(username=auth_get.get_username(),password=auth_get.access_token)
		user.userID=user_id
		#print "user_id",user_id
		user.username=auth_get.get_username()
		user.access_token = auth_get.access_token 
		user.access_token_secret = auth_get.access_token_secret
		user.save()
		#user = User.objects.get(username=user_id)
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		engine = importlib.import_module(settings.SESSION_ENGINE)
		request.session = engine.SessionStore()

		user=auth.authenticate(username=auth_get.get_username(), password=auth_get.access_token)
    auth.login(request,user)
    cu = request.user.profile
    cu.is_chat_user = True
    cu.last_accessed = utcnow()
    cu.save()
    request.session['key'] = auth_get.access_token 
    request.session['secret'] = auth_get.access_token_secret 
    return HttpResponseRedirect(reverse('index'))

@csrf_exempt
def chat_api(request):
	if request.method == 'POST':
		###Oauth system:userid for username
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(request.session.get('key'), request.session.get('secret'))
		api = tweepy.API(auth_handler=auth)
		###Update user
		if request.user.username:
			u = request.user.profile
			u.last_accessed = utcnow()
			u.is_chat_user = True
			u.save()
		###Makes json
		#d = json.loads(request.body)
		msg = request.POST['msg'] 
		#msg =  d.get('msg')
		if len(msg) > 120:
			print "error to much word"
			return 0
		######################################
		#形態素解析による不明なコメント除去
		######################################
		word=msg
		node = tagger.parseToNode(word.encode('utf-8'))
		while(node):
			if node.feature.split(",")[0] == "名詞" or node.feature.split(",")[0] == "動詞":
				for checks in find:
					if node.surface == checks:
						#print "Bad Word",node.surface
						return 0;
			node = node.next
		######################################
		u = api.get_user(request.user.username)
		user= u.screen_name
		#print 'user',user
		m = Message(user=user,message=msg)
		m.save()
		#res = {'id':m.id,'msg':m.message,'user':m.user,'time':m.time.strftime('%I:%M:%S %p').lstrip('0')}
		#data = json.dumps(res)
		try:
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(request.session.get('key'), request.session.get('secret'))
			api = tweepy.API(auth_handler=auth)
			""" test get tweet"""
			api.update_status(status=m.message+" "+"#spicetest")
			#count=count+1
		except tweepy.TweepError,e:
			p = re.compile('^\[{u\'message\': u\'(.+)\', u\'code\': (\d+)}\]$')
			m = p.match(e.reason)
			if m:
				message =  m.group(1)
				code = m.group(2)
		#return HttpResponse(data,content_type="application/json")
		return HttpResponse("Sended")
	else:
         print "Http404"
         raise Http404 

def logout(request):
	cu = request.user.profile
	cu.is_chat_user = False
	cu.save()
	return render(request,'logout.html')

def hello(request):
  return HttpResponse("Hello from django")

