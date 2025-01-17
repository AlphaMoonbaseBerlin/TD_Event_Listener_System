

'''Info Header Start
Name : EventEmitter
Author : Wieland@AMB-ZEPH15
Saveorigin : EventListenerSystem.toe
Saveversion : 2023.12000
Info Header End'''
# Imports to generate ID
import hashlib
import uuid
import os


import json
from collections import namedtuple
import event_exceptions
from functools import lru_cache
import sys



argument_tuple = namedtuple("Argument", "name type")
optional_argument_tuple = namedtuple("Optional_Argument", "type default_value")

class EventEmitter:

	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.subscriber = set()
		sys.modules["EventExceptions"] = event_exceptions
		self.module_definition = self.ownerComp.op("module_definition")
		self.Decorators = mod.decorator

	@property
	def definition(self):
		return self._load_definition( self.ownerComp.op("definition").text or "{}" )

	@lru_cache(maxsize=1)
	def _load_definition(self, definitionJson):
		definition_dict = json.loads( definitionJson )
		outputDefinition = {}
		for event_key, event_data in definition_dict.items():
			outputDefinition[event_key] = { "arguments": [], "optional" : {}}

			for argument in event_data.get("arguments", []):
				name, type_string = argument.split(":")
				argument_type =eval(type_string)
				outputDefinition[event_key]["arguments"].append(
					argument_tuple( name, argument_type )
				)

			for optional_argument in event_data.get("optional", []):
				name, definition = optional_argument.split(":")
				type_string, default_value = definition.split("=")
				outputDefinition[event_key]["optional"][name]	= optional_argument_tuple( 
					eval(type_string), 
					default_value )
		return outputDefinition
	
	@property
	def strict(self):
		return self.ownerComp.par.Strict.eval()

	def check_event(self, event, *args, **kwargs):
		definition = self.definition.get(event, None)
		if not definition: raise event_exceptions.InvalidEvent( f"Missing definition for {event}")
		if len(args) > len( definition["arguments"]): 
			raise event_exceptions.ToManyArguments(f"The eventcall passes to many arguments. Expected {len(definition['arguments'])}, got {len(args)} of call for {event}")

		for index,expected_argument in enumerate( definition["arguments"] ):
			try:
				suspect = args[index]
				if not isinstance( suspect, expected_argument.type): 
					raise event_exceptions.WrongArgumentType( f"Expected {expected_argument.type}, got {type(suspect)} on {index} of call for {event}")
			except IndexError:
				raise event_exceptions.MissingArgument( f"Missing argument {expected_argument.name} on {index} of call for {event}")
			
		for optional_name, optional_data in kwargs.items():
			if not optional_name in definition["optional"]: 
				raise event_exceptions.ToManyArguments(f"The eventcall passed a not defined optional argument {optional_name} of call for {event}")
			if not isinstance( optional_data, definition["optional"][optional_name].type): 
					raise event_exceptions.WrongArgumentType( f"Expected {definition['optional'][optional_name].type}, got {type( optional_data)} on {optional_name} of call for {event}")
	
	def Attach_Emitter(self, target):
		setattr( target, "Emit", self.Emit )
		setattr( target, "Subscribe", self.Subscribe)
		setattr( target, "Unsubscribe", self.Unsubscribe )
		setattr( target, "Construct_Module_Op", self.Construct_Module_Op)
		setattr( target, "Construct_Module_Definition", self.Construct_Module_Definition)

		
	def Emit(self, event, *args, **kwargs):
		corpses = set()
		
		if self.strict: self.check_event( event, *args, **kwargs)
		sendBridge =  kwargs.pop("__sendBridge", True)
		
		if sendBridge: self.sendBridge( event, *args, **kwargs)
		
		for sub in self.subscriber:
			if not sub.valid: 
				corpses.add( sub )
				continue
			try:
				sub.Dispatch(event, args, kwargs)
			except Exception as e:
				if self.ownerComp.par.Gracefulerror.eval(): 
					self.ownerComp.op("logger").Log( f"Error during Event {event} in listener {sub}.", e)
					continue
				raise e
		self.subscriber = self.subscriber -  corpses

	def Subscribe( self, listener):
		self.subscriber.add( listener )

	def Unsubscribe( self, listener):
		self.subscriber = self.subscriber - {listener}

	@lru_cache(maxsize=1)
	def Construct_Module_Definition(self):
		self.module_definition.clear()
		#self.module_definition.write( "import EventExceptions\n\n" )
		for callback_name, callback in self.definition.items():
			arguments = []
			for argument in callback["arguments"]:
				arguments.append( f"{argument.name}:{argument.type.__name__}")
			for optional_name, optional in callback["optional"].items():
				arguments.append( f"{optional_name}:{optional.type.__name__}={optional.default_value}" )

			self.module_definition.write( f"def on{callback_name}( {', '.join(arguments)} ):\n\treturn\n\n")

		return self.module_definition.text
	
	def Construct_Module_Op(self):
		
		self.Construct_Module_Definition()
		return self.module_definition

	@lru_cache(	maxsize=1)
	def _bridgeId(self):
		return hashlib.md5(
			f"{self.ownerComp.id}{os.getpid()}{uuid.getnode()}".encode()
		).hexdigest()
	
	def sendBridge(self, eventname, *args, **kwargs):
		if not self.ownerComp.par.Bridgeactive.eval(): return
		messageid = str(uuid.uuid4())
		self.ownerComp.op("receivedIDs").appendRow( messageid)
		for _ in range( self.ownerComp.par.Resends.eval()):
			self.ownerComp.op("udpout1").send(json.dumps(
				{
					"bridgeid" : self._bridgeId(),
					"messageid" : messageid,
					"eventname" : eventname,
					"args" : args,
					"kwargs" : kwargs
				}
			))
	def receiveBridge(self, messagedump:str):
		messageDict = json.loads(messagedump)
		if messageDict["bridgeid"] == self._bridgeId(): return
		if self.ownerComp.op("receivedIDs")[ messageDict["messageid"], 0 ]: return
		self.ownerComp.op("receivedIDs").appendRow( messageDict["messageid"])
		self.Emit(
			messageDict["eventname"],
			*messageDict["args"],
			__sendBridge = False,
			**messageDict["kwargs"]
		)