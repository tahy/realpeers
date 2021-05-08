import pika
from time import sleep


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='cle_queue')


def publish(message):
    channel.basic_publish(exchange='',
                          routing_key='cle_queue',
                          body=message)
    print("Published to rabbit")
    print(message)


if __name__ == '__main__':
    while True:
        publish("test")
        sleep(1)
