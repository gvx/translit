#!/usr/bin/env python
#encoding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
import appindicator
import gobject
import os
import re

def files(location):
	lst = []
	try:
		for filename in os.listdir(location):
			lst.extend(parsefile(location + filename))
	except OSError as e:
		print(e)
	return lst

class Item(object):
	def __init__(self, caption, transforms):
		self.caption = caption
		self.transforms = transforms
	def apply(self, text):
		for trans in self.transforms:
			text = trans.apply(text)
		return text

class Transform(object):
	def __init__(self, kind, source, dest):
		self.kind = kind
		if kind == 's':
			self.source = re.compile(source)
		elif kind == 'p':
			self.source = eval('lambda _: ' + (source or dest))
		else:
			self.source = source
		self.dest = dest
	def apply(self, text):
		if self.kind == 's':
			return self.source.sub(self.dest, text)
		elif self.kind == 'p':
			return self.source(text)
		return text.replace(self.source, self.dest)

def parsefile(name):
	with open(name) as f:
		caption = f.readline().strip().split('->', 1)
		state = None
		closer = None
		only = False
		from_ = []
		to = []
		substate = False
		transformations = [[] for x in caption]
		for ch in f.read():
			if not state:
				if ch == '<':
					only = 1
				elif ch == '>':
					only = 0
				elif ch in 'rs':
					state = ch
				elif ch == 'p':
					state = 'p'
					substate = True
				elif ch in ' \t\n\r':
					pass
			elif not closer:
				closer = ch
			elif ch == closer:
				if not substate:
					substate = True
				else:
					from_ = ''.join(from_)
					to = ''.join(to)
					if only != 1:
						transformations[0].append(Transform(state, from_, to))
					if len(caption) == 2 and (only is False or only):
						transformations[1].append(Transform(state, to, from_))
					state = None
					closer = None
					only = False
					from_ = []
					to = []
					substate = False
			elif substate:
				to.append(ch)
			else:
				from_.append(ch)
		items = [Item(' → '.join(caption), transformations[0])]
		if len(caption) == 2:
			items.append(Item(' → '.join(reversed(caption)), reversed(transformations[1])))
		return items

PATH = (os.environ.get('XDG_DATA_DIR') or (os.environ.get('HOME') + '/.local/share')) + '/translit/'

disabled = set()

class Main:
	def __init__(self):
		self.ind = appindicator.Indicator("translit", "indicator-translit", appindicator.CATEGORY_OTHER)
		self.ind.set_status(appindicator.STATUS_ACTIVE)

		self.menu = gtk.Menu()

		self.read_disabled(PATH)
		self.read_from_dir(PATH)

		sep = gtk.SeparatorMenuItem()
		sep.show()
		self.menu.append(sep)

		item = gtk.MenuItem("Options")
		item.connect("activate", self.show_options)
		item.show()
		self.menu.append(item)

		sep = gtk.SeparatorMenuItem()
		sep.show()
		self.menu.append(sep)

		image = gtk.ImageMenuItem(gtk.STOCK_QUIT)
		image.connect("activate", self.quit)
		image.show()
		self.menu.append(image)

		self.menu.show()
		self.ind.set_menu(self.menu)
		self.clipboard = gtk.Clipboard()

	def convert(self, widget, data):
		t = self.clipboard.wait_for_text()
		if t:
			self.clipboard.set_text(data(t))

	def quit(self, widget, data=None):
		gtk.main_quit()

	def read_disabled(self, dir):
		try:
			with open(dir + 'disabled') as f:
				for line in f:
					disabled.add(line.strip())
		except (IOError, OSError) as e:
			print(e)

	def write_disabled(self, dir):
		try:
			with open(dir + 'disabled', 'w') as f:
				for item in disabled:
					f.write(item)
					f.write('\n')
		except (IOError, OSError) as e:
			print(e)

	def read_from_dir(self, dir):
		for i in files(dir + 'transforms/'):
			item = gtk.MenuItem(i.caption)
			item.connect("activate", self.convert, i.apply)
			if i.caption not in disabled:
				item.show()
			self.menu.append(item)
	
	def show_options(self, widget, data=None):
		o = Options(self)
		o.run()
		o.destroy()

class Options(gtk.Dialog):
	def __init__(self, main):
		gtk.Dialog.__init__(self, "Options", buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))
		self.liststore = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING)
		self.main = main
		self.map = {}
		for item in main.menu.get_children():
			if type(item) != gtk.MenuItem:
				break
			label = item.get_label()
			self.map[label] = item
			self.liststore.append((label not in disabled, label))
		self.list = gtk.TreeView(self.liststore)
		self.list.set_headers_visible(False)
		column = gtk.TreeViewColumn("Enabled")
		self.list.append_column(column)
		cell = gtk.CellRendererToggle()
		cell.set_activatable(True)
		cell.set_property('activatable', True)
		cell.connect('toggled', self.toggle, self.liststore)
		column.pack_start(cell, False)
		column.add_attribute(cell, "active", 0)
		column = gtk.TreeViewColumn("Name")
		self.list.append_column(column)
		cell = gtk.CellRendererText()
		column.pack_start(cell, False)
		column.add_attribute(cell, "text", 1)
		
		self.list.show()
		self.get_content_area().add(self.list)
	def toggle(self, cell, path, model):
		model[path][0] = not model[path][0]
		self.map[model[path][1]].set_visible(model[path][0])
		if model[path][0]:
			disabled.remove(model[path][1])
		else:
			disabled.add(model[path][1])
		self.main.write_disabled(PATH)

if __name__ == "__main__":
	Main()
	gtk.main()

