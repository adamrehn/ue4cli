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
	
	def __init__(self, prefixDirs=[], includeDirs=[], linkDirs=[], libs=[], systemLibs=[], definitions=[], cxxFlags=[], ldFlags=[], cmakeFlags=[]):
		self.prefixDirs = Utility.forwardSlashes(prefixDirs)
		self.includeDirs = Utility.forwardSlashes(includeDirs)
		self.linkDirs = Utility.forwardSlashes(linkDirs)
		self.libs = Utility.forwardSlashes(libs)
		self.systemLibs = systemLibs
		self.definitions = definitions
		self.cxxFlags = cxxFlags
		self.ldFlags = ldFlags
		self.cmakeFlags = cmakeFlags
		
		# Set our prefixes to either GCC style or MSVC style, depending on platform
		isWindows = platform.system() == 'Windows'
		self.definitionPrefix = '/D'        if isWindows else '-D'
		self.includeDirPrefix = '/I'        if isWindows else '-I'
		self.linkerDirPrefix  = '/LIBPATH:' if isWindows else '-L'
		self.systemLibPrefix  = ''          if isWindows else '-l'
	
	def __repr__(self):
		return repr({
			'prefixDirs': self.prefixDirs,
			'includeDirs': self.includeDirs,
			'linkDirs': self.linkDirs,
			'libs': self.libs,
			'systemLibs': self.systemLibs,
			'definitions': self.definitions,
			'cxxFlags': self.cxxFlags,
			'ldFlags': self.ldFlags,
			'cmakeFlags': self.cmakeFlags
		})
	
	def merge(self, other):
		self.prefixDirs  = self.prefixDirs + other.prefixDirs
		self.includeDirs = self.includeDirs + other.includeDirs
		self.linkDirs    = self.linkDirs + other.linkDirs
		self.libs        = self.libs + other.libs
		self.systemLibs  = self.systemLibs + other.systemLibs
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
				self.prefixedStrings(self.definitionPrefix, self.definitions, engineRoot) +
				self.prefixedStrings(self.includeDirPrefix, self.includeDirs, engineRoot) +
				self.resolveRoot(self.cxxFlags, engineRoot),
			fmt.quotes
		)
	
	def getLinkerFlags(self, engineRoot, fmt, includeLibs=True):
		"""
		Constructs the linker flags string for building against this library
		"""
		components = self.resolveRoot(self.ldFlags, engineRoot)
		if includeLibs == True:
			components.extend(self.prefixedStrings(self.linkerDirPrefix, self.linkDirs, engineRoot))
			components.extend(self.resolveRoot(self.libs, engineRoot))
			components.extend(self.prefixedStrings(self.systemLibPrefix, self.systemLibs, engineRoot))
		
		return Utility.join(fmt.delim, components, fmt.quotes)
	
	def getPrefixDirectories(self, engineRoot, delimiter=' '):
		"""
		Returns the list of prefix directories for this library, joined using the specified delimiter
		"""
		return delimiter.join(self.resolveRoot(self.prefixDirs, engineRoot))
	
	def getIncludeDirectories(self, engineRoot, delimiter=' '):
		"""
		Returns the list of include directories for this library, joined using the specified delimiter
		"""
		return delimiter.join(self.resolveRoot(self.includeDirs, engineRoot))
	
	def getLinkerDirectories(self, engineRoot, delimiter=' '):
		"""
		Returns the list of linker directories for this library, joined using the specified delimiter
		"""
		return delimiter.join(self.resolveRoot(self.linkDirs, engineRoot))
	
	def getLibraryFiles(self, engineRoot, delimiter=' '):
		"""
		Returns the list of library files for this library, joined using the specified delimiter
		"""
		return delimiter.join(self.resolveRoot(self.libs, engineRoot))
	
	def getSystemLibraryFiles(self, engineRoot, delimiter=' '):
		"""
		Returns the list of system library files for this library, joined using the specified delimiter
		"""
		return delimiter.join(self.systemLibs)
	
	def getPreprocessorDefinitions(self, engineRoot, delimiter=' '):
		"""
		Returns the list of preprocessor definitions for this library, joined using the specified delimiter
		"""
		return delimiter.join(self.resolveRoot(self.definitions, engineRoot))
	
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
			] + self.resolveRoot(self.cmakeFlags, engineRoot),
			fmt.quotes
		)
	
	def resolveRoot(self, paths, engineRoot):
		return [p.replace('%UE4_ROOT%', engineRoot) for p in paths]
	
	def prefixedStrings(self, prefix, strings, engineRoot):
		resolved = self.resolveRoot(strings, engineRoot)
		return [prefix + s for s in resolved]
