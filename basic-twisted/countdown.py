
class Countdown(object):
    def __init__(self, counter, rate, on_finished):
        self._counter = counter
        self.counter = counter
        self.rate = rate
        self.on_finished = on_finished
        self.count()

    def count(self):
        if self.counter <= 0:
            self.on_finished(self)
        else:
            print('Countdown with rate', self.rate, 'says', self.counter, 'out of', self._counter)
            self.counter -= 1
            reactor.callLater(self.rate, self.count)


# Excercise 1: Concurrent Countdowns
def countdowns_fire(counters, rates):
    countdowns = []

    def finished(countdown):
        countdowns.remove(countdown)
        if not countdowns:
            reactor.stop()

    for c, r in zip(counters, rates):
        countdowns.append(Countdown(c, r, finished))


from twisted.internet import reactor

reactor.callWhenRunning(countdowns_fire, [5,3,7], [1,1.7,0.7])

print('Start!')
reactor.run()
print ('Stop!')
