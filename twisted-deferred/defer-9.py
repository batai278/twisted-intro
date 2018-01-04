import sys

from twisted.internet.defer import Deferred

def got_poem(poem):
    print(poem)
    return("Got poem!")

def poem_failed(err):
    print('poem download failed')
    print(sys.stderr, 'I am terribly sorry')
    print('try again later?')
    #print(err)

def poem_done(arg):
    # arg is None when invoked in callback chain: got_poem -> poem_done with got_poem returning nothing (None)
    # arg is returned value of got_poem when latter returns one
    print(arg)
    from twisted.internet import reactor
    reactor.stop()

d = Deferred()

d.addCallbacks(got_poem, poem_failed)
d.addBoth(poem_done)

from twisted.internet import reactor

reactor.callWhenRunning(d.callback, 'Another short poem.')

reactor.run()
