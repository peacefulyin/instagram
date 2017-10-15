import time
import pymongo
import redis

from django.conf import settings
from django.http import HttpResponse,HttpResponseForbidden
from django.utils import deprecation


mong_url = settings.MONGO_URL
mong_db = settings.MONGO_DB
client = pymongo.MongoClient(mong_url)
db = client[mong_db]

redisconn = redis.Redis(host='localhost', port=6379, db=3)

class BlockedIpMiddleware(deprecation.MiddlewareMixin):
    def process_request(self, request):
        ua = request.META.get('HTTP_USER_AGENT', 'unknown')
        if not ua:
            return HttpResponseForbidden()

        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            ip = request.request.META.get('HTTP_X_FORWARDED_FOR')
        else:
            ip = request.META.get('REMOTE_ADDR')
        if ip in redisconn.smembers('block_ip'):
            return HttpResponseForbidden()


        if not redisconn.hexists(ip,'ip'):
            origin_time = time.time()
            totaltime = 60
            total_visit_count = 5
            item = {
                'ip': ip,
                'origin_time': origin_time,
                'total_count': 0,
                'block_time':0,
            }

            redisconn.hmset(ip,item)
        else:
            keys = ['ip', 'origin_time', 'total_count', 'block_time']
            values = redisconn.hmget(ip,keys)
            item = dict(zip(keys,values))

            origin_time = float(item['origin_time'])
            now_time = time.time()
            total_count = int(item['total_count']) + 1

            if now_time - origin_time < 60 and total_count > 100:
                redisconn.sadd('block_ip',ip)
                item['total_count'] = 0
                item['origin_time'] = time.time()
                item['block_time'] = int(item['block_time']) + 1
                redisconn.hmset(ip, item)
            elif now_time - origin_time > 60 and total_count < 100:
                item['total_count'] = 0
                item['origin_time'] = time.time()
                redisconn.hmset(ip, item)
            else:
                item['total_count'] = int(item['total_count']) + 1
                redisconn.hmset(ip, item)


