'''Info Header Start
Name : event_exceptions
Author : Wieland@AMB-ZEPH15
Saveorigin : EventListenerSystem.toe
Saveversion : 2023.12000
Info Header End'''
#globals()['var'] = "an object"

class EventException( Exception ):
    pass

class InvalidEvent( EventException ):
    pass

class MissingArgument( EventException ): 
    pass

class ToManyArguments( EventException ):
    pass

class WrongArgumentType( EventException ):
    pass