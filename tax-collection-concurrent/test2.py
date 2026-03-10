import threading
import time
counter = 0
lock = threading.Lock()
def increment(x):
    global counter
    for i in range(1000):
        with lock:
            temp = counter
            time.sleep(0)
            counter = temp+1
threads = []
for i in range(1000):
    thread = threading.Thread(target=increment, args=(i,))
    threads.append(thread)
    thread.start()
for thread in threads:
    thread.join()

print(counter)
