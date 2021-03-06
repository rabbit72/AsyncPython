import socket
import time
from select import select
from threading import Thread

from collections import deque

tasks = deque()
stopped = {}

def run_queries():
    while any([tasks, stopped]):
        while not tasks:
            ready_to_read, _, _ = select(stopped.keys(), [], [])
            for r in ready_to_read:
                tasks.append(stopped.pop(r))
        while tasks:
            task = tasks.popleft()
            try:
                sock = next(task)
                stopped[sock] = task
            except StopIteration:
                print("query done")

def make_request():
    start_time = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8000))
    sock.send(b'GET /\n\n')

    yield sock
    
    resp = sock.recv(100)
    sock.close()
    end_time = time.time()
    print(time.strftime("%H:%M:%S"), end_time-start_time)

def run_request_producer():
    while True:
        tasks.append(make_request())
        time.sleep(1.0)

t = Thread(target=run_request_producer)
t.start()

run_queries()
