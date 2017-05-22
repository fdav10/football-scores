import sched
import grequests as gr


def start_periodic_calls(interval, action, args=()):
    s = sched.scheduler()
    _periodic(s, interval, action, args)
    s.run()


def _periodic(scheduler, interval, action, args=()):
    scheduler.enter(interval, 1, _periodic,
                    (scheduler, interval, action, args))
    action(*args)

def batch_request(urls):
    requests = (gr.get(url) for url in urls)
    responses = gr.map(requests)
    return responses
