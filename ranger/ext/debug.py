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

LOGFILE = '/tmp/errorlog'

def log(*objects, **keywords):
	"""Writes objects to a logfile.
	Has the same arguments as print() in python3"""
	start = 'start' in keywords and keywords['start'] or 'ranger:'
	sep   =   'sep' in keywords and keywords['sep']   or ' '
	_file =  'file' in keywords and keywords['file']  or open(LOGFILE, 'a')
	end   =   'end' in keywords and keywords['end']   or '\n'
	_file.write(sep.join(map(str, (start, ) + objects)) + end)

#for python3-only versions, this could be replaced with:
#
#def log(*objects, start='ranger:', sep=' ', end='\n'):
#	print(start, *objects, end=end, sep=sep, file=open(LOGFILE, 'a'))

def trace():
	from traceback import print_stack
	print_stack(file=open(LOGFILE, 'a'))
