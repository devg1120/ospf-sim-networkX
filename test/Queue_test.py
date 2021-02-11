from thespian.actors import ActorSystem
from thespian.actors import Actor

import thespian

asys = 0

class FullKeyLogActor(Actor):
    def receiveMessage(self, message, sender):
        print("FullKeyLogActor MSG recive:%s" % message)
        print(sender)
        #asys.tell(sender,"recieve ok")
        #ActorSystem().tell(sender,"recieve ok")
        self.send(sender,{"result": "ok"})


#class KSApplication(Actor):
class KSApplication():
    def __init__(self):
        self.actors = []

    def add_actor(self, actor_name):     
        class_str = actor_name
        aref = None
        try:
            #aref = ActorSystem().createActor(eval(class_str))
            aref = asys.createActor(eval(class_str))
        except NameError:
            try:
                class_str = "Actors.{}".format(class_str)
                #aref = ActorSystem().createActor(eval(class_str))
                aref = asys.createActor(eval(class_str))
            except NameError:
                print("Error: Actor Class {} not found".format(actor_name))
                return
            
        #ActorSystem().tell(aref,{"load": "ok"})
        #asys.tell(aref,{"load": "ok"})
        r = asys.ask(aref,{"load": "ok"})
        print("KSA: %s" %r)
        adata = {'actor':class_str, 'aref':aref}
        self.actors.append(adata)
    def receiveMessage(self, message, sender):
        print("KSA MSG recive:%s" % message)

if __name__ == "__main__":


    #asys = ActorSystem('multiprocUDPBase')
    #asys = ActorSystem('multiprocTCPBase')
    asys = ActorSystem('multiprocQueueBase')
    app = KSApplication()
    app.add_actor("FullKeyLogActor")

    #asys.shutdown()
