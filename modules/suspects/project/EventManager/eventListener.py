'''Info Header Start
Name : eventListener
Author : Wieland@AMB-ZEPH15
Saveorigin : Project.toe
Saveversion : 2022.32660
Info Header End'''
def defaultattr(target, attrName, default):
	try:
		return getattr(target, attrName)
	except AttributeError:
		setattr(target, attrName, default)
	return default

import td
from inspect import getmembers, isfunction
from typing import Iterable, Dict
EVENT_ATTR_NAME = "__AMB_EVENT_DICT"

class extEventManager:
	
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.unsubscribe()
		self.Update(
			self.ownerComp.op("callbackManager").ext.extCallbackManager.moduleOperator
		)
		
	def _generateNamespace(self, namespace:str):
		return  f"__{namespace}__"
	
	def Update(self, moduleDAT):
		self.unsubscribe()
		module = mod( moduleDAT )
		for member in getmembers(module, isfunction):
			self.Subscribe( member[0], self.ownerComp.par.Namespace.eval() )

	@property
	def Namespace(self):
		return self.ownerComp.par.Namespace.eval()

	def Emit(self, event:str, namespace:str= "", data:any = None, source:OP = None):
		invalid:Iterable[COMP] = []
		listeners:set = defaultattr(td, EVENT_ATTR_NAME, {} ).get(
			self._generateNamespace( namespace or self.Namespace ), {}).get(
			event, set()
			)
		for listener in listeners:
			if not listener.valid: 
				invalid.append( listener )
				continue
			listener.Dispatch( event, source or self.ownerComp, data)

		for invalidListener in invalid:
			listeners.remove( invalidListener )

	def Subscribe(self, event:str, namespace:str = ""):
		eventData		= defaultattr(td, EVENT_ATTR_NAME, {} )
		namespaceDict	= eventData.setdefault( self._generateNamespace( namespace or self.Namespace ), {} )
		eventSet:set	= namespaceDict.setdefault(event, set() )
		eventSet.add( self.ownerComp )

	def Dispatch(self, event:str, source:OP, data:any):
		self.ownerComp.op("callbackManager").Do_Callback( event, source, data, self.ownerComp )
		return
	
	def unsubscribe(self):
		for namespace in defaultattr(td, EVENT_ATTR_NAME, {} ).values():
			for eventSet in namespace.values():
				eventSet = eventSet - {self.ownerComp}