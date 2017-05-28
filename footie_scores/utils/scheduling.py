import sched
import grequests as gr

SCHEDULER = sched.scheduler()


def start_periodic_calls(interval, action, args=()):
    s = sched.scheduler()
    _periodic(s, interval, action, args)
    s.run()


def _periodic(scheduler, interval, action, args=()):
    scheduler.enter(interval, 1, _periodic,
                    (scheduler, interval, action, args))
    action(*args)


def schedule_action(action, time):
    s = SCHEDULER.enter(time, 1, action)


def batch_request(urls):
    requests = (gr.get(url) for url in urls)
    responses = gr.map(requests)
    return responses
