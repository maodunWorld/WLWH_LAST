import redis
from settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
REDISHOST = REDIS_HOST
REDISPORT = REDIS_PORT
"""
redis 封装

"""

class RedisHelper():
    def __init__(self):
        self.__redis = redis.Redis(REDISHOST, REDISPORT, db=0, password=REDIS_PASSWORD, socket_timeout=500)

    #删除一个String 通过 key
    def del_a_key(self, key):
        return self.__redis.delete(key)

    def get_a_key(self, key):
        return self.__redis.get(key)

    def set_a_key(self, key, value):
        return self.__redis.set(key, value)

    def get_all_key(self):
        return self.__redis.keys()

re_handler = RedisHelper()
#测试
if __name__ == '__main__':
    re_test = RedisHelper()
    # print(re_test.del_a_key('me'))
    for _ in range(50, 101):
        print(_)
        print(re_test.del_a_key('pubId:{}'.format(_)))
    # re = re_test.get_a_key('pubId:50')
    # print(re)
    # print(re_test.get_all_key())
    # re_test.set_a_key('me', 'I am a tester')
    # print(re_test.get_a_key('me'))