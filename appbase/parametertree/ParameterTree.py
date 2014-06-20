# -*- coding: utf-8 -*-

from pyqtgraph.parametertree.ParameterTree import ParameterTree as PTree


class ParameterTree(PTree):
	
	def __init__(self, parameter=None, showHeader=False, showTop=False, animated=True):
		PTree.__init__(self, showHeader=showHeader)
		self.setAnimated(animated)
		if parameter:
			self.setParameters(parameter, showTop)
		self.itemExpanded.connect(lambda item: item.param.expand(True))
		self.itemCollapsed.connect(lambda item: item.param.expand(False))


	def returnParameterOnKlick(self, activate, executeMethod=None):
		if activate:
			self.selectionChanged = self._doReturnParameterOnKlick
			self._execute_ReturnParam = executeMethod
		else:
			self.selectionChanged = super(ParameterTree,self).selectionChanged


	def _doReturnParameterOnKlick(self,*args):
		sel = self.selectedItems()
		for item in sel:
			try:
				param = item.param
				if self._execute_ReturnParam:
					self._execute_ReturnParam(param)
			except AttributeError:
				pass
		super(ParameterTree,self).selectionChanged(*args)

