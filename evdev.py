
import struct
import os
import fcntl
from time import sleep

class Input:
	def __init__(self, fname):
		s = struct.Struct("<QQHHi")
		self.rlen = s.size
		self.event_parser = s.unpack
		self.fd = open(fname, "rb")
		flags = fcntl.fcntl(self.fd.fileno(), fcntl.F_GETFL)
		fcntl.fcntl(self.fd.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
		self.pressed = set()

	def read_event(self):
		evb = self.fd.read(self.rlen)
		if not evb:
			return None
		if len(evb) == self.rlen:
			tsec, tusec, typ, code, value = self.event_parser(evb)
			return tsec + (tusec / 1000000), typ, code, value
		else:
			return None

	def read_key(self):
		while True:
			ev = self.read_event()
			if ev is None:
				return None
			ts, typ, code, value = ev
			if typ == 1:
				break
		return code, value

	def test(self):
		while True:
			keys = self.keys_pressed()
			print(repr(keys))
			sleep(0.05)

	def keys_pressed(self):
		ev = self.read_key()
		if ev is not None:
			code, value = ev
			if value == 0:
				self.pressed.discard(code)
			else:
				self.pressed.add(code)
		return self.pressed

def find_keyboards():
	with open("/proc/bus/input/devices", "r") as f:
		lines = f.readlines()
	name = None
	handlers = None
	ev = None
	for l in lines:
		l = l.strip(" \r\n")
		if l.startswith("N: Name="):
			name = l.split("=",1)[-1]
		elif l.startswith("H: Handlers"):
			handlers = l.split("=",1)[-1].split()
		elif l.startswith("B: EV="):
			ev = l.split("=",1)[-1]
			if ev == "120013":
				print("Found keyboard: {}".format(name))
				print("Handlers: {}".format(repr(handlers)))
				for h in handlers:
					if h.startswith("event"):
						return "/dev/input/"+h
	return None

if __name__ == "__main__":
	fname = find_keyboards()
	ih = Input(fname)
	ih.test()
