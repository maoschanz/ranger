# Copyright (C) 2009, 2010  Roman Zimbelmann <romanz@lavabit.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The BrowserView manages a set of BrowserColumns."""
from . import Widget
from .browsercolumn import BrowserColumn
from .pager import Pager
from ..displayable import DisplayableContainer

class BrowserView(Widget, DisplayableContainer):
	ratios = None
	preview = True
	preview_available = True
	stretch_ratios = None
	need_clear = False

	def __init__(self, win, ratios, preview = True):
		DisplayableContainer.__init__(self, win)
		self.ratios = ratios
		self.preview = preview

		# normalize ratios:
		ratio_sum = float(sum(ratios))
		self.ratios = tuple(map(lambda x: x / ratio_sum, ratios))

		if len(self.ratios) >= 2:
			self.stretch_ratios = self.ratios[:-2] + \
					((self.ratios[-2] + self.ratios[-1] * 0.9),
					(self.ratios[-1] * 0.1))

		offset = 1 - len(ratios)
		if preview: offset += 1

		for level in range(len(ratios)):
			fl = BrowserColumn(self.win, level + offset)
			self.add_child(fl)

		try:
			self.main_column = self.container[preview and -2 or -1]
		except IndexError:
			self.main_column = None
		else:
			self.main_column.display_infostring = True
			self.main_column.main_column = True

		self.pager = Pager(self.win, embedded=True)
		self.pager.visible = False
		self.add_child(self.pager)

	def draw(self):
		try:
			if self.env.cmd.show_obj.draw_bookmarks:
				self._draw_bookmarks()
		except AttributeError:
			if self.need_clear:
				self.win.erase()
				self.need_redraw = True
				self.need_clear = False
			DisplayableContainer.draw(self)

	def finalize(self):
		if self.pager.visible:
			try:
				self.fm.ui.win.move(self.main_column.y, self.main_column.x)
			except:
				pass
		else:
			try:
				x = self.main_column.x
				y = self.main_column.y + self.main_column.target.pointer\
						- self.main_column.scroll_begin
				self.fm.ui.win.move(y, x)
			except:
				pass

	def _draw_bookmarks(self):
		self.need_clear = True

		sorted_bookmarks = sorted(item for item in self.fm.bookmarks \
				if '/.' not in item[1].path)

		def generator():
			return zip(range(self.hei), sorted_bookmarks)

		try:
			maxlen = max(len(item[1].path) for i, item in generator())
		except ValueError:
			return
		maxlen = min(maxlen + 5, self.wid)

		for line, items in generator():
			key, mark = items
			string = " " + key + ": " + mark.path
			self.addnstr(line, 0, string.ljust(maxlen), self.wid)

	def resize(self, y, x, hei, wid):
		"""Resize all the columns according to the given ratio"""
		DisplayableContainer.resize(self, y, x, hei, wid)
		left = 0

		cut_off_last = self.preview and not self.preview_available \
				and self.stretch_ratios

		if cut_off_last:
			generator = zip(self.stretch_ratios, range(len(self.ratios)))
		else:
			generator = zip(self.ratios, range(len(self.ratios)))

		last_i = len(self.ratios) - 1

		for ratio, i in generator:
			wid = int(ratio * self.wid)

			if i == last_i:
				wid = int(self.wid - left + 1)

			if i == last_i - 1:
				self.pager.resize(0, left, hei, max(1, self.wid - left))

			try:
				self.container[i].resize(0, left, hei, max(1, wid-1))
			except KeyError:
				pass

			left += wid

	def click(self, event):
		n = event.ctrl() and 1 or 3
		if event.pressed(4):
			self.main_column.scroll(relative = -n)
		elif event.pressed(2) or event.key_invalid():
			self.main_column.scroll(relative = n)
		else:
			DisplayableContainer.click(self, event)

	def open_pager(self):
		self.pager.visible = True
		self.pager.focused = True
		self.pager.open()
		try:
			self.container[-2].visible = False
			self.container[-3].visible = False
		except IndexError:
			pass

	def close_pager(self):
		self.pager.visible = False
		self.pager.focused = False
		self.pager.close()
		try:
			self.container[-2].visible = True
			self.container[-3].visible = True
		except IndexError:
			pass

	def poke(self):
		DisplayableContainer.poke(self)
		if self.settings.collapse_preview and self.preview:
			has_preview = self.container[-2].has_preview()
			if self.preview_available != has_preview:
				self.preview_available = has_preview
				self.resize(self.y, self.x, self.hei, self.wid)
