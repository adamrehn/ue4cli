import os

# The list of include directory substrings that trigger custom CMake flags
CUSTOM_FLAGS_FOR_INCLUDE_DIRS = {
	'libPNG-': 'PNG_PNG_INCLUDE_DIR'
}

# The list of library files that trigger custom CMake flags
CUSTOM_FLAGS_FOR_LIBS = {
	'png':        'PNG_LIBRARY',
	'z':          'ZLIB_LIBRARY',
	'z_fPIC':     'ZLIB_LIBRARY',
	'zlibstatic': 'ZLIB_LIBRARY'
}

class CMakeCustomFlags(object):
	
	@staticmethod
	def processLibraryDetails(details):
		"""
		Processes the supplied ThirdPartyLibraryDetails instance and sets any custom CMake flags
		"""
		
		# If the header include directories list contains any directories we have flags for, add them
		for includeDir in details.includeDirs:
			
			# If the directory path matches any of the substrings in our list, generate the relevant flags
			for pattern in CUSTOM_FLAGS_FOR_INCLUDE_DIRS:
				if pattern in includeDir:
					flag = '-D' + CUSTOM_FLAGS_FOR_INCLUDE_DIRS[pattern] + '=' + includeDir
					details.cmakeFlags.append(flag)
		
		# If the libraries list contains any libs we have flags for, add them
		for lib in details.libs:
			
			# Extract the name of the library from the filename
			# (We remove any "lib" prefix or numerical suffix)
			filename = os.path.basename(lib)
			(name, ext) = os.path.splitext(filename)
			libName = name.replace('lib', '') if name.startswith('lib') else name
			libName = libName.rstrip('_-1234567890')
			
			# If the library name matches one in our list, generate its flag
			if libName in CUSTOM_FLAGS_FOR_LIBS:
				flag = '-D' + CUSTOM_FLAGS_FOR_LIBS[libName] + '=' + lib
				details.cmakeFlags.append(flag)
