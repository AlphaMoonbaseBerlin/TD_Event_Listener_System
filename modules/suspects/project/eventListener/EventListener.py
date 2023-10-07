
'''Info Header Start
Name : EventListener
Author : Wieland@AMB-ZEPH15
Saveorigin : Project.toe
Saveversion : 2022.32660
Info Header End'''

class EventListener:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.Subscribe()

	def undefined(self, *args, **kwargs):
		return
	
	def CallbackDefinition(self):
		emitter = self.ownerComp.par.Emitter.eval()
		try:
			return emitter.Construct_Module_Definition()
		except AttributeError:
			return "def noEmitterDefined():\n\treturn"
		
	def Subscribe(self):
		emitter = self.ownerComp.par.Emitter.eval()
		try:
			emitter.Subscribe( self.ownerComp )
		except AttributeError:
			return
		
	
	def Dispatch(self, event, args, kwargs):
		if not self.ownerComp.par.Active.eval(): return False
		self.ownerComp.op("callbackManager").Do_Callback("Event", event, args, kwargs)
		self.ownerComp.op("callbackManager").Do_Callback(f"on{event}", *args, **kwargs)
		return True