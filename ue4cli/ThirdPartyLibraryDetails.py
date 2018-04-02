from .Utility import Utility
import platform

class PrintingFormat(object):
	"""
	Represents the formatting used to print a set of flags
	"""
	
	def __init__(self, delim, quotes):
		self.delim = delim
		self.quotes = quotes
	
	@staticmethod
	def singleLine():
		"""
		Printing format for a single, space-delimited line
		"""
		return PrintingFormat(' ', True)
	
	@staticmethod
	def multiLine():
		"""
		Printing format for multiple lines
		"""
		return PrintingFormat('\n', False)


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
	
	def getCompilerFlags(self, engineRoot, fmt):
		"""
		Constructs the compiler flags string for building against this library
		"""
		return Utility.join(
			fmt.delim, 
				self._prefixedStrings(self.definitionPrefix, self.definitions, engineRoot, False) +
				self._prefixedStrings(self.includeDirPrefix, self.includeDirs, engineRoot, False) +
				self._prefixedStrings('', self.cxxFlags, engineRoot, False),
			fmt.quotes
		)
	
	def getLinkerFlags(self, engineRoot, fmt, includeLibs=True):
		"""
		Constructs the linker flags string for building against this library
		"""
		components = self._prefixedStrings('', self.ldFlags, engineRoot, False)
		if includeLibs == True:
			components.extend(self._prefixedStrings(self.linkerDirPrefix, self.linkDirs, engineRoot, False))
			components.extend(self._prefixedStrings('', self.libs, engineRoot, False))
		
		return Utility.join(fmt.delim, components, fmt.quotes)
	
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
	
	def getLibraryFiles(self, engineRoot, delimiter=' '):
		"""
		Returns the list of library files for this library, joined using the specified delimiter
		"""
		return delimiter.join([d.replace('%UE4_ROOT%', engineRoot) for d in self.libs])
	
	def getPreprocessorDefinitions(self, engineRoot, delimiter=' '):
		"""
		Returns the list of preprocessor definitions for this library, joined using the specified delimiter
		"""
		return delimiter.join([d.replace('%UE4_ROOT%', engineRoot) for d in self.definitions])
	
	def getCMakeFlags(self, engineRoot, fmt):
		"""
		Constructs the CMake invocation flags string for building against this library
		"""
		return Utility.join(
			fmt.delim,
			[
				'-DCMAKE_PREFIX_PATH=' + self.getPrefixDirectories(engineRoot, ';'),
				'-DCMAKE_INCLUDE_PATH=' + self.getIncludeDirectories(engineRoot, ';'),
				'-DCMAKE_LIBRARY_PATH=' + self.getLinkerDirectories(engineRoot, ';'),
			] + self._prefixedStrings('', self.cmakeFlags, engineRoot, False),
			fmt.quotes
		)
	
	
	# "Private" methods
	
	def _prefixedStrings(self, prefix, strings, engineRoot, join=True, quotes=True):
		transformed = [prefix + s.replace('%UE4_ROOT%', engineRoot) for s in strings]
		if join == True:
			return Utility.join('" "', transformed, quotes=quotes)
		else:
			return transformed
