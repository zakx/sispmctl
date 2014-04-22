import subprocess

class SisPMError(Exception):
	pass

class SisPM:
	binary = "/usr/local/bin/sispmctl"
	serial = ""
	OFF = False
	ON = True

	def __init__(self, serial, binary=None):
		self.serial = serial
		if binary:
			self.binary = binary

	def get(self, outlet=None):
		status = {}

		if outlet == "all":
			del outlet # all's the default case, handled later.

		command = [
			self.binary,
			'-D', # specify serial
			self.serial,
			'-q', # quiet
			'-n', # numerical
			'-g', # get status
			'all' if not outlet else str(int(outlet))
		]
		try:
			result = subprocess.check_output(command)
		except subprocess.CalledProcessError:
			raise SisPMError("Querying outlets failed.")
		for i, line in enumerate(result.split('\n')[:-1]):
				status[i+1] = bool(int(line))
		if not outlet: # "all" case
			return status
		else:
			return {outlet: status[1]}

	def off(self, outlet='all'):
		self.set(outlet, SisPM.OFF)

	def on(self, outlet='all'):
		self.set(outlet, SisPM.ON)

	def toggle(self, outlet):
		status = self.get(outlet)
		for myoutlet in status:
			self.set(outlet=myoutlet, status=(not status[myoutlet]))

	def set(self, outlet, status):
		cmdStatus = ""
		if status == SisPM.ON or status == True or status == "on":
			cmdStatus = "-o"
		elif status == SisPM.OFF or status == False or status == "off":
			cmdStatus = "-f"
		else:
			raise SisPMError("Invalid status '%s'." % status)

		if outlet == "all":
			del outlet # all's the default case, handled later.

		command = [
			self.binary,
			'-D', # specify serial
			self.serial,
			'-q', # quiet
			cmdStatus, # set status
			'all' if not outlet else str(int(outlet))
		]

		try:
			subprocess.check_call(command)
		except subprocess.CalledProcessError:
			raise SisPMError("Failed to set outlet(s).")
