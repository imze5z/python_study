# -*- coding: utf-8 -*-
import pika


class RabbitmqBase(object):
    def __init__(self, user, passwd, host):
        credentials = pika.PlainCredentials(user, passwd)
        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(
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
        if not self.no_ack:
            self.ch.basic_ack(delivery_tag=self.method.delivery_tag)


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
        self.ch.basic_publish(
            exchange='',
            routing_key=self.task_queue,
            properties=pika.BasicProperties(delivery_mode=2),
            body=body)

    def store_data(self, data):
        self.ch.basic_publish(
            exchange='',
            routing_key=self.store_queue,
            properties=pika.BasicProperties(delivery_mode=2),
            body=data)

    def serv_forever(self, func):
        if self.task_queue:
            self.ch.queue_declare(queue=self.task_queue, durable=self.durable)
        if self.store_queue:
            self.ch.queue_declare(queue=self.store_queue, durable=self.durable)

        def callback(ch, method, properties, body):
            if self.prefetch_count > 1:
                task = _RabbitmqTask(func, (self, body), self.no_ack, ch,
                                     method, properties)
                task.start()
            else:
                func(self, body)
                if not self.no_ack:
                    self.ch.basic_ack(delivery_tag=self.method.delivery_tag)

        self.ch.basic_qos(prefetch_count=self.prefetch_count)
        self.ch.basic_consume(
            callback, queue=self.task_queue, no_ack=self.no_ack)
        self.ch.start_consuming()


class RabbitmqProducter(RabbitmqBase):
    def __init__(self, user, passwd, host, task_queue, durable):
        super().__init__(user, passwd, host)
        self.task_queue = task_queue
        self.durable = durable

    def send_task(self, body):
        self.ch.basic_publish(
            exchange='',
            routing_key=self.task_queue,
            properties=pika.BasicProperties(delivery_mode=2),
            body=body)

    def produce(self, func):
        if not self.task_queue:
            self.ch.queue_declare(queue=self.task_queue, durable=self.durable)
        func(self)
