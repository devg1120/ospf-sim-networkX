from thespian.actors import *

class Hello(Actor):
    def receiveMessage(self, message, sender):
        if message == 'are you there?':  #(ref:messageCheck)
            world = self.createActor(World)  #(ref:createGoodbye)
            worldmsg = (sender, 'Hello,')  #(ref:messageTuple)
            self.send(world, worldmsg)

class World(Actor):
    def receiveMessage(self, message, sender):
        if isinstance(message, tuple):  #(ref:messageIsTuple)
            orig_sender, pre_world = message
            self.send(orig_sender, pre_world + ' world!')  #(ref:sendOriginalSender)

class Goodbye(Actor):
    def receiveMessage(self, message, sender):
        self.send(sender, 'Goodbye')

def run_example(systembase=None):
    hello = ActorSystem(systembase).createActor(Hello)
    goodbye = ActorSystem().createActor(Goodbye)
    greeting = ActorSystem().ask(hello, 'are you there?', 1.5)
    print(greeting + '\n' + ActorSystem().ask(goodbye, None, 0.1))  #(ref:print)
    #ActorSystem().shutdown()   #(ref:actorSysShutdown)

if __name__ == "__main__":
    import sys
    run_example(sys.argv[1] if len(sys.argv) > 1 else None)
