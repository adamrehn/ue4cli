from .Utility import Utility
import platform

class ThirdPartyLibraryDetails(object):
	"""
	Represents the details of the Unreal-specific versions of one of more third-party libraries
	"""
	
	def __init__(self, prefixDirs=[], includeDirs=[], linkDirs=[], libs=[], definitions=[], cxxFlags=[], ldFlags=[], cmakeFlags=[]):
		self.prefixDirs = Utility.forwardSlashes(prefixDirs)
		self.includeDirs = Utility.forwardSlashes(includeDirs)
		self.linkDirs = Utility.forwardSlashes(linkDirs)
		self.libs = Utility.forwardSlashes(libs)
		self.definitions = definitions
		self.cxxFlags = cxxFlags
		self.ldFlags = ldFlags
		self.cmakeFlags = cmakeFlags
		
		# Set our prefixes to either GCC style or MSVC style, depending on platform
		isWindows = platform.system() == 'Windows'
		self.definitionPrefix = '/D'        if isWindows else '-D'
		self.includeDirPrefix = '/I'        if isWindows else '-I'
		self.linkerDirPrefix  = '/LIBPATH:' if isWindows else '-L'
	
	def merge(self, other):
		self.prefixDirs  = self.prefixDirs + other.prefixDirs
		self.includeDirs = self.includeDirs + other.includeDirs
		self.linkDirs    = self.linkDirs + other.linkDirs
		self.libs        = self.libs + other.libs
		self.definitions = self.definitions + other.definitions
		self.cxxFlags    = self.cxxFlags + other.cxxFlags
		self.ldFlags     = self.ldFlags + other.ldFlags
		self.cmakeFlags  = self.cmakeFlags + other.cmakeFlags
	
	def getCompilerFlags(self, engineRoot):
		"""
		Constructs the compiler flags string for building against this library
		"""
		return Utility.join(' ', [
			self._prefixedStrings(self.definitionPrefix, self.definitions, engineRoot),
			self._prefixedStrings(self.includeDirPrefix, self.includeDirs, engineRoot),
			self._prefixedStrings('', self.cxxFlags, engineRoot)
		])
	
	def getLinkerFlags(self, engineRoot):
		"""
		Constructs the linker flags string for building against this library
		"""
		return Utility.join(' ', [
			self._prefixedStrings(self.linkerDirPrefix, self.linkDirs, engineRoot),
			self._prefixedStrings('', self.libs, engineRoot),
			self._prefixedStrings('', self.ldFlags, engineRoot)
		])
	
	def getPrefixDirectories(self, engineRoot, delimiter=' '):
		"""
		Returns the list of prefix directories for this library, joined using the specified delimiter
		"""
		return delimiter.join([d.replace('%UE4_ROOT%', engineRoot) for d in self.prefixDirs])
	
	def getIncludeDirectories(self, engineRoot, delimiter=' '):
		"""
		Returns the list of include directories for this library, joined using the specified delimiter
		"""
		return delimiter.join([d.replace('%UE4_ROOT%', engineRoot) for d in self.includeDirs])
	
	def getLinkerDirectories(self, engineRoot, delimiter=' '):
		"""
		Returns the list of linker directories for this library, joined using the specified delimiter
		"""
		return delimiter.join([d.replace('%UE4_ROOT%', engineRoot) for d in self.linkDirs])
	
	def getCMakeFlags(self, engineRoot):
		"""
		Constructs the CMake invocation flags string for building against this library
		"""
		flags = '"-DCMAKE_PREFIX_PATH=' + self.getPrefixDirectories(engineRoot, ';') + '"'
		flags += ' "-DCMAKE_INCLUDE_PATH=' + self.getIncludeDirectories(engineRoot, ';') + '"'
		flags += ' "-DCMAKE_LIBRARY_PATH=' + self.getLinkerDirectories(engineRoot, ';') + '"'
		flags += ' ' + self._prefixedStrings('', self.cmakeFlags, engineRoot)
		return flags
	
	
	# "Private" methods
	def _prefixedStrings(self, prefix, strings, engineRoot):
		transformed = [prefix + s.replace('%UE4_ROOT%', engineRoot) for s in strings]
		return Utility.join('" "', transformed, quotes=True)
