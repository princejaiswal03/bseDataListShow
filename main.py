import cherrypy
import os
import redis
from jinja2 import Environment, FileSystemLoader


env = Environment(loader = FileSystemLoader('templates'))

class stockEntries(object):
    @cherrypy.expose
    def index(self,searchValue = None, submit = None):
        tmpl = env.get_template('index.html')
        sortedData = self.get10StockList()
        if submit == 'submit':
            searchValue = searchValue.strip()
            sortedData = self.getDataByName(searchValue)
        return tmpl.render(sortedData = sortedData)
    
    #function to connect redis server
    def redisConnect(self):
        r = redis.Redis(host='localhost', port=6379,charset = 'utf-8', db=0, decode_responses = True)
        return r

    #function to find top 10 data
    def get10StockList(self):
        retData = []
        sortedData = []
        r = self.redisConnect()
        keys = r.keys('*')
        if keys:
            keys.remove('dataSaveOn')
            for item in keys:
                retData.append(r.hgetall(item))

        sortedData = sorted(retData, key = lambda pk:((float(pk['PREVCLOSE']) - float(pk['CLOSE']))/float(pk['LAST'])))

        return sortedData[:10]

    #function to find value by name
    def getDataByName(self,name):
        retData = []
        keys =[]
        name = str(name).upper()
        r = self.redisConnect()
        for key in r.scan_iter(match = '*'+name+'*'):
            keys.append(key)
        
        for item in keys:
            retData.append(r.hgetall(item))
        retData = sorted(retData, key = lambda pk:((float(pk['PREVCLOSE']) - float(pk['CLOSE']))/float(pk['LAST'])))

        return retData

        


config = { '/':
            { 
                "tools.staticdir.root": os.path.abspath(os.path.dirname(__file__)) 
            }, 
        '/static': 
            { 
                'tools.staticdir.on': True,
                'tools.staticdir.dir': "static" 
            } 
        }
cherrypy.quickstart(stockEntries(),'/', config = config)
