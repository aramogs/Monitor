import queue
import threading
import time


def func(que, thread_no):
    while True:
        task = que.get()
        time.sleep(.05)
        que.task_done()
        print(f'Thread #{thread_no} is doing task #{task} in the queue.\n')


q = queue.Queue()

for i in range(4):
    worker = threading.Thread(target=func, args=(q, i,), daemon=True)
    worker.start()

for j in range(10):
    q.put(j)

q.join()
