import schedule
import time

class PeriodicScheduler:
    def __init__(self):
        self.scheduler = schedule.Scheduler()

    def scheduleTaskInSeconds(self, interval, task, *args):
        self.scheduler.every(interval).seconds.do(task, *args)

    def scheduleTaskInHours(self, interval, task, *args):
        self.scheduler.every(interval).hours.do(task, *args)

    def executeTaskLoop(self):
        self.scheduler.run_all() # first run
        while True:
            self.scheduler.run_pending()
            time.sleep(1)


# ps = PeriodicScheduler()
# argTuple = ('argseconds', 'argseconds2')
# argTuple2 = ('arghours')
# ps.periodicTaskInSeconds(5, job, *argTuple)
# ps.periodicTaskInHours(1, job, *argTuple2)
# ps.executeTaskLoop()
