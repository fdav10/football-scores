import sched


def start_periodic_calls(interval, action, args=()):
    s = sched.scheduler()
    _periodic(s, interval, action, args)
    s.run()


def _periodic(scheduler, interval, action, args=()):
    scheduler.enter(interval, 1, _periodic,
                    (scheduler, interval, action, args))
    action(*args)
