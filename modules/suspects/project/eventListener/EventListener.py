'''Info Header Start
Name : EventListener
Author : Wieland@AMB-ZEPH15
Version : 0
Build : 2
Savetimestamp : 2023-07-24T22:58:22.137571
Saveorigin : Project.toe
Saveversion : 2022.28040
Info Header End'''

class EventListener:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.Subscribe()

	def undefined(self, *args, **kwargs):
		return
		
	def Subscribe(self):
		emitter = self.ownerComp.par.Emitter.eval()
		try:
			emitter.Subscribe( self.ownerComp )
			self.ownerComp.op("callbackManager").op("default_callbacks").text = emitter.Construct_Module_Definition()
		except AttributeError:
			self.ownerComp.op("callbackManager").op("default_callbacks").text = "def noEmitterDefined():\n\treturn"
			return
		
	
	def Dispatch(self, event, args, kwargs):
		if not self.ownerComp.par.Active.eval(): return False
		self.ownerComp.op("callbackManager").Do_Callback("Event", event, args, kwargs)
		self.ownerComp.op("callbackManager").Do_Callback(f"on{event}", *args, **kwargs)
		return True