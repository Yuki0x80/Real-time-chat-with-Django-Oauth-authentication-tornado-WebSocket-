#coding:utf-8
from django.contrib import admin
from socks.models import Message,ChatUser
# Register your models here.
#admin.site.register(Message)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'time',)  # 一覧に出したい項目
    list_display_links = ('id', 'user','message')  # 修正リンクでクリックできる項目
admin.site.register(Message, MessageAdmin)
