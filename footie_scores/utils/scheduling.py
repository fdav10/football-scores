import time
import sched


def start_periodic_calls(interval, action):
    s = sched.scheduler()
    _periodic(s, interval, action)
    s.run()


def _periodic(scheduler, interval, action, arg=()):
    scheduler.enter(interval, 1, _periodic,
                    (scheduler, interval, action, arg))
    action(*arg)
