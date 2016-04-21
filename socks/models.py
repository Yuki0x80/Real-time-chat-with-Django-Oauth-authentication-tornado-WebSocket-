#coding:utf-8
from django.db import models

# Create your models here.
from datetime import datetime
from django.contrib.auth.signals import user_logged_in, user_logged_out  
from django.contrib.auth.models import User
import urllib, hashlib, binascii
from numpy.random import *

class Message(models.Model):
	user = models.CharField(max_length=20)
	message = models.TextField(max_length=120)
	time = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return self.user

class ChatUser(models.Model):
	user = models.OneToOneField(User)
	userID =  models.IntegerField(primary_key=True)
	username = models.CharField(max_length=20)
	access_token = models.CharField(max_length=255)
	access_token_secret = models.CharField(max_length=255)
	is_chat_user = models.BooleanField(default=False)
	last_accessed = models.DateTimeField(auto_now_add=True)

def random():
	number=randint(1000)
	print number
	return number

#まだDBにデータが登録されていない場合は登録し、登録されている場合はそのデータを返します。
#lambda = make Value property=it mean getter
User.profile = property(lambda u: ChatUser.objects.get_or_create(user=u,defaults={'userID':random()})[0])
#defaults={'username':u.username,'userID':hash_username(u.username)}
#defaults={'userID':random()}