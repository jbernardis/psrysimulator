import wx


def makeBlank():
	empty = wx.Bitmap(24, 24, 32)
	dc = wx.MemoryDC(empty)
	dc.SetBackground(wx.Brush((0,0,0,0)))
	dc.Clear()
	del dc
	empty.SetMaskColour((0,0,0))
	return empty


class ScriptListCtrl(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent

		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(490, 280),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES
			)

		self.scripts = []
		self.checked = []
		self.selected = None

		self.InsertColumn(0, "Script")
		self.InsertColumn(1, "Status")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 400)

		self.SetItemCount(0)

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

		self.loadImages()
		self.il = wx.ImageList(24, 24)
		empty = makeBlank()
		self.idxEmpty = self.il.Add(empty)
		self.idxSelected = self.il.Add(self.selected)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)

		self.ticker = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTicker)
		self.ticker.Start(1000)

	def loadImages(self):
		png = wx.Image("selected.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.selected = png

	def onTicker(self, _):
		self.refreshAll()

	def ClearChecks(self):
		self.checked = [self.idxEmpty for _ in range(len(self.scripts))]
		self.refreshAll()

	def AddScript(self, script):
		self.scripts.append(script)
		self.checked.append(self.idxEmpty)
		self.refreshItemCount()

	def refreshItemCount(self):
		self.SetItemCount(len(self.scripts))

	def refreshAll(self):
		self.refreshItemCount()
		if self.GetItemCount() > 0:
			self.RefreshItems(0, self.GetItemCount()-1)

	def setSelection(self, tx, dclick=False):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			if dclick:
				self.parent.reportDoubleClick(tx)
			else:
				self.parent.reportSelection(tx)

	def GetChecked(self):
		return [self.scripts[i].GetName() for i in range(len(self.scripts)) if self.checked[i] == self.idxSelected]

	def OnItemSelected(self, event):
		idx = event.Index
		if self.checked[idx] == self.idxEmpty:
			self.checked[idx] = self.idxSelected
		else:
			self.checked[idx] = self.idxEmpty

		self.setSelection(event.Index)

	def OnItemDeselected(self, evt):
		self.setSelection(None)

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)

	def OnGetItemImage(self, item):
		return self.checked[item]

	def OnGetItemText(self, item, col):
		scr = self.scripts[item]

		if col == 0:
			return scr.GetName()
		elif col == 1:
			return scr.GetStatus()

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
