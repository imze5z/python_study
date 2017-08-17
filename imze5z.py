# -*- coding: utf-8 -*-

import random
import string
import xlwt
from scrapy.selector import  Selector
import pika
import pymysql
import pymongo
import yaml
from threading import Thread, Lock, current_thread
import logging
import traceback
import time

def func_runtime(callback):
    now = time.time()
    print('%s - start: %f' % (callback, now))
    callback()
    now = time.time() - now
    print('%s - spent: %f Second' % (callback, now))

def timestamp_to_time(timestamp):
    x = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', x)

def time_to_timestamp(time_str):
    x = time.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    return time.mktime(x)

def get_current_timestamp():
    return time.time()

def random_str(n=20):
    return ''.join(random.sample(string.ascii_letters + string.digits, n))

class _MySQLConnection(dict):
    is_used = None
    connection = None

class MongoPool(object):
    def __init__(self, host, username, password):
        uri = "mongodb://%s:%s@%s" % (quote_plus(username),
                quote_plus(password), quote_plus(host))
        self.mc = pymongo.MongoClient(uri)

    def close(self):
        self.mc.close()

class MYSQLPool(object):
    def __init__(self, size, **kwargs):
        self._pool = []
        self.lock = Lock()
        kwargs['cursorclass'] = pymysql.cursors.DictCursor
        for i in range(size):
            self._pool.append(_MySQLConnection(
                is_used=False, connection=pymysql.Connection(**kwargs)))

    def close(self):
        for i in self._pool:
            i['connection'].close()

    def _get_connection(self):
        with self.lock:
            while 1:
                for conn in self._pool:
                    if conn['is_used'] == False:
                        conn['is_used'] = True
                        return conn

                logging.debug(('%r - waitting for other thread to release the'
                    'connection' % current_thread()))

    def execute(self, sql, args):
        conn = self._get_connection()
        try:
            with conn['connection'].cursor() as cursor:
                sql = sql.lower().strip()
                cursor.execute(sql,replace('?', '%s'), args or ())
                tmp = sql[:6]
                if 'insert' in tmp or 'delete' in tmp or 'update' in tmp:
                    conn['connection'].commit()
                if 'select' in tmp:
                    rows = cursor.fetchall()
                    result = []
                    for row in rows:
                        result.append(row)
                    return result
                else:
                    affected = cursor.rowcount
                    return affected
        except:
            print(traceback.format_exc())
            if 'insert' in tmp or 'delete' in tmp or 'update' in tmp:
                conn['connection'].rollback()
        finally:
            cursor.close()
            conn['is_used'] = False

class Yaml(object):
    def __init__(self, filename):
        f = open(filename, 'r')
        self.cfg = yaml.load(f.read())
        f.close()

    def get(self, key):
        return self.cfg[key]

class ExcelWriter(object):
    def __init__(self):
        self.excel = xlwt.Workbook()
        self.sheet = sel.excel.add_sheet('default')

    def write(self, x, y, value):
        self.sheet.write(x, y, value)

    def save(self, filename):
        self.excel.save(filename)

class XPathParser(object):
    def __init__(self, text):
        self.res = Selector(text=text)

    def xpath(self, text):
        return self.res.xpath(text)

class RabbitmqBase(object):
    def __init__(self, user, passwd, host):
        credentials = pika.PlainCredentials(user, passwd)
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
        self.ch = self.conn.channel()

    def __del__(self):
        try:
            self.ch.close()
            self.conn.close()
        except:
            pass

class _RabbitmqTask(Thread):
    def __init__(self, target, args, no_ack, ch, method, properties):
        super().__init__(target=target, args=args)
        self.no_ack = no_ack
        self.ch = ch
        self.method = method
        self.properties = properties

    def run(self):
        super().run()
        if self.no_ack == False:
            self.ch.basic_ack(delivery_tag = self.method.delivery_tag)

class RabbitmqCustomer(RabbitmqBase):
    def __init__(self, user, passwd, host, prefetch_count, durable, no_ack,
            task_queue, store_queue):
        super().__init__(user, passwd, host)

        self.task_queue = task_queue
        self.store_queue = store_queue
        self.prefetch_count = prefetch_count
        self.durable = durable
        self.no_ack = no_ack

    def send_task(self, body):
        self.ch.basic_publish(exchange='', routing_key=self.task_queue,
                properties=pika.BasicProperties(delivery_mode=2), body=body)

    def store_data(self, data):
        self.ch.basic_publish(exchange='', routing_key=self.store_queue,
                properties=pika.BasicProperties(delivery_mode=2), body=data)

    def serv_forever(self, func):
        if self.task_queue != None:
            self.ch.queue_declare(queue=self.task_queue, durable=self.durable)
        if self.store_queue != None:
            self.ch.queue_declare(queue=self.store_queue, durable=self.durable)

        def callback(ch, method, properties, body):
            if self.prefetch_count > 1:
                task = _RabbitmqTask(func, (self, body), self.no_ack, ch, method, properties)
                task.start()
            else:
                func(self, body)
                if self.no_ack == False:
                    self.ch.basic_ack(delivery_tag=self.method.delivery_tag)

        self.ch.basic_qos(prefetch_count=self.prefetch_count)
        self.ch.basic_consume(callback, queue=self.task_queue, no_ack=self.no_ack)
        self.ch.start_consuming()


class RabbitmqProducter(RabbitmqBase):
    def __init__(self, user, passwd, host, task_queue, durable):
        super().__init__(user, passwd, host)
        self.task_queue = task_queue
        self.durable = durable

    def send_task(self, body):
        self.ch.basic_publish(exchange='', routing_key=self.task_queue,
                properties=pika.BasicProperties(delivery_mode=2), body=body)

    def produce(self, func):
        if self.task_queue != None:
            self.ch.queue_declare(queue=self.task_queue, durable=self.durable)
        func(self)


if __name__ == '__main__':
    print(random_str())
