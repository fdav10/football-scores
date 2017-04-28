import time
import sched


def task(output='default'):
    print ("From print time", time.time(), output)


def periodic(scheduler, interval, action, arg=()):
    scheduler.enter(interval, 1, periodic,
                    (scheduler, interval, action, arg))
    action(*arg)


if __name__ == '__main__':
    s = sched.scheduler()
    periodic(s, 3, task, ('slower output',))
    periodic(s, 1, task, ('quicker output',))
    s.run()

