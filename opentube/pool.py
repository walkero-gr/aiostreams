try:
    from multiprocessing.pool import ThreadPool
except ImportError:
    # Fallback for Python 2.5: simple thread pool implementation
    import threading

    class ThreadPool(object):
        def __init__(self, processes):
            self.processes = processes

        def map(self, func, args):
            results = [None] * len(args)
            threads = []

            def worker(i, arg):
                results[i] = func(arg)

            for i, arg in enumerate(args):
                t = threading.Thread(target=worker, args=(i, arg))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()
            return results

def collect(func, args):
    max_workers = len(args) or 1
    pool = ThreadPool(max_workers)
    return pool.map(func, args)
