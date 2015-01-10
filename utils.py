import Queue
import threading

def flatten(list_of_lists):
    return [item for sublist in list_of_lists if sublist for item in sublist]

def parallelize_closures(fns, max_threads=50):
    in_queue = Queue.Queue()
    out_queue = Queue.Queue()

    for index, fn in enumerate(fns):
        in_queue.put((fn, index))

    def target():
        while True:
            try:
                fn, index = in_queue.get(block=False)
            except Queue.Empty:
                return
            value = fn()
            out_queue.put((value, index))

    num_threads = min(len(fns), max_threads) if max_threads else len(fns)
    threads = []
    for _ in xrange(num_threads):
        thread = threading.Thread(target=target)
        threads.append(thread)
        thread.daemon = True
        thread.start()
    for thread in threads:
        thread.join()

    response = [None] * len(fns)
    while not out_queue.empty():
        item = out_queue.get()
        response[item[1]] = item[0]
    return response
