from threading import Thread
import time
import requests
import warnings

SESSION = requests.Session()
warnings.filterwarnings("ignore")


class UrlThread(Thread):
    def run(self):
        resp = SESSION.get(
            'https://dev.koreromaori.com/api/',
            headers={'Accept': 'application/json'},
            verify=False)


def make_n_requests(num_requests):
    threads = []
    for i in range(num_requests):
        threads.append(UrlThread())
        start = time.time()

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    end = time.time()
    print "Time to get response for %d simultaneous requests" % (num_requests,), end - start
