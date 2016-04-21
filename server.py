#coding:utf-8
from tornado.options import options, define, parse_command_line
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import tornado.wsgi
import wsgiref.simple_server
import os,csv
import MeCab

t=open(os.getcwd()+"/socks/sample.csv" ,"rU") 
reader = csv.reader(t)
find=next(reader)
tagger = MeCab.Tagger("-Ochasen")

define('port', type=int, default=8080)
path= os.path.abspath(os.path.dirname(__file__)) 

class WSHandler(tornado.websocket.WebSocketHandler):
  connections = set()
  msg=[]

  def check_origin(self, origin):
    return True

  def open(self):
    print 'connection opened...'
    self.connections.add(self)
    #self.write_message("The server says: 'Hello'. Connection was accepted.")
    [self.write_message(message) for message in self.msg]
      #self.write_message(message)


  def on_message(self, message):
    #self.write_message("The server says: " + message + " back at you")
    word=message
    node = tagger.parseToNode(word.encode('utf-8'))
    while(node):
      if node.feature.split(",")[0] == "名詞" or node.feature.split(",")[0] == "動詞":
        for checks in find:
          if node.surface == checks:
            print "Bad Word",node.surface
            return 0;
      node = node.next
    print 'received:', message
    self.msg.append(message)
    [con.write_message(message) for con in self.connections]
    

  def on_close(self):
    print 'connection closed...'
    self.connections.remove(self)

def main():
  parse_command_line()
  wsgi_app = tornado.wsgi.WSGIContainer(
    django.core.handlers.wsgi.WSGIHandler())
  tornado_app = tornado.web.Application(
    [
      ('/', WSHandler),
      ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
      ])
  server = tornado.httpserver.HTTPServer(tornado_app)
  server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()