from __future__ import print_function
import subprocess, sys

class CommandOutput(object):
	"""
	Helper class to wrap the output of Utility.capture()
	"""
	def __init__(self, stdout, stderr):
		self.stdout = stdout
		self.stderr = stderr


class Utility:
	"""
	Provides utility functionality
	"""
	
	@staticmethod
	def printStderr(*args, **kwargs):
		"""
		Prints to stderr instead of stdout
		"""
		print(*args, file=sys.stderr, **kwargs)
	
	@staticmethod
	def readFile(filename):
		"""
		Reads data from a file
		"""
		with open(filename, 'rb') as f:
			return f.read().decode('utf-8')
	
	@staticmethod
	def writeFile(filename, data):
		"""
		Writes data to a file
		"""
		with open(filename, 'wb') as f:
			f.write(data.encode('utf-8'))
	
	@staticmethod
	def patchFile(filename, replacements):
		"""
		Applies the supplied list of replacements to a file
		"""
		patched = Utility.readFile(filename)
		
		# Perform each of the replacements in the supplied dictionary
		for key in replacements:
			patched = patched.replace(key, replacements[key])
		
		Utility.writeFile(filename, patched)
	
	@staticmethod
	def forwardSlashes(paths):
		"""
		Replaces Windows directory separators with Unix separators
		"""
		return list([p.replace('\\', '/') for p in paths])
	
	@staticmethod
	def join(delim, items, quotes=False):
		"""
		Joins the supplied list of strings after removing any empty strings from the list
		"""
		transform = lambda s: s
		if quotes == True:
			transform = lambda s: s if ' ' not in s else '"{}"'.format(s)
		
		stripped = list([transform(i) for i in items if len(i) > 0])
		if len(stripped) > 0:
			return delim.join(stripped)
		return ''
	
	@staticmethod
	def capture(command, input=None, cwd=None, shell=False, raiseOnError=False):
		"""
		Executes a child process and captures its output
		"""
		
		# Attempt to execute the child process
		proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, shell=shell, universal_newlines=True)
		(stdout, stderr) = proc.communicate(input)
		
		# If the child process failed and we were asked to raise an exception, do so
		if raiseOnError == True and proc.returncode != 0:
			raise Exception(
				'child process ' + str(command) +
				' failed with exit code ' + str(proc.returncode) +
				'\nstdout: "' + stdout + '"' +
				'\nstderr: "' + stderr + '"'
			)
		
		return CommandOutput(stdout, stderr)
	
	@staticmethod
	def run(command, cwd=None, shell=False, raiseOnError=False):
		"""
		Executes a child process and waits for it to complete
		"""
		returncode = subprocess.call(command, cwd=cwd, shell=shell)
		if raiseOnError == True and returncode != 0:
			raise Exception('child process ' + str(command) + ' failed with exit code ' + str(returncode))
