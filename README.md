# Event Listener System


# Description
This project tries to implement a touchesqe Event Listener/Emitter system, meaning that you can have a nice 1 to N connection, where emitters do not care about listeners.

There are two concepts right now:
## Listener / Emitter Comps
The EmitterCOMP is a direct representation of an emitter. You can attach an en emitter to your extension by using the AttachEmitter method and passing the extensionObject itself. This way, Listeners can then easily refference the extension object itself.
The Listener object now can refference one Emitter, but many Listeners can refference the same emitter.

## EventManager
The eventmanager is a more generic PubSub-Approach based on namespaces and event-names. 
You simply define your callbacks. The Manager will automatically subscribe to the specific events. 
Using the Emit method will now notify all other managers that are subscribed to the specific event in that namespace.

# Version
2022.28040
