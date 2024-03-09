from .ThirdPartyLibraryDetails import ThirdPartyLibraryDetails
from .UnrealManagerException import UnrealManagerException
from .UnrealManagerUnix import UnrealManagerUnix
from .Utility import Utility
import re, os

class UnrealManagerLinux(UnrealManagerUnix):
	
	def getPlatformIdentifier(self):
		return 'Linux'
	
	def _detectEngineRoot(self):
		
		# FIXME: With current setup, 'UE4Editor' can be returned instead of:
		# 'UnrealEditor.desktop' or 'com.epicgames.UnrealEngineEditor.desktop',
		# which will mean that NOT the highest version will be returned.
		# Such case would be very rare (mixing different ways of instalations) but it can happen!
		# (this was always a problem)
		
		# If UE4Editor/UnrealEditor is available in the PATH, use its location to detect the root directory path
		potentialEditorLocs = [
			Utility.capture(['which', 'UnrealEditor']).stdout.strip(),
			Utility.capture(['which', 'UE4Editor']).stdout.strip(),
		]
		for editorLoc in potentialEditorLocs:
			if editorLoc != '':
				editorLoc = os.path.dirname(os.path.realpath(editorLoc))
				return os.path.abspath(editorLoc + '/../../..')
		
		# Under Debian-based systems, we can use the desktop integration to find UE4Editor/UnrealEditor
		potentialLauncherPaths = [
			os.path.join(os.environ['HOME'], '.local', 'share', 'applications', 'UnrealEditor.desktop'),
			os.path.join(os.environ['HOME'], '.local', 'share', 'applications', 'com.epicgames.UnrealEngineEditor.desktop'),
			os.path.join(os.environ['HOME'], '.local', 'share', 'applications', 'UE4.desktop'),
		]
		for launcherPath in potentialLauncherPaths:
			if os.path.exists(launcherPath):
				with open(launcherPath, 'r') as f:
					launcherData = f.read()
					match = re.search('Path=(.*)\n', launcherData)
					if match != None:
						editorLoc = os.path.realpath(match.group(1))
						return os.path.abspath(editorLoc + '/../../..')
		
		# Could not auto-detect the Unreal Engine location
		raise UnrealManagerException('could not detect the location of the latest installed Unreal Engine version')
	
	def _editorPathSuffix(self, cmdVersion):
		return ''
	
	# Under Linux, we always need to build against Unreal's bundled libc++
	def _defaultThirdpartyLibs(self):
		return ['libc++']
	
	def _getLibraryOverrides(self):
		# Details for libc++
		osType = 'Unix' if self._getEngineVersionDetails()['MajorVersion'] >= 5 else 'Linux'
		libCXXRoot = '%UE4_ROOT%/Engine/Source/ThirdParty/{0}/LibCxx'.format(osType)
		libCXXLibDir = '{}/lib/{}/x86_64-unknown-linux-gnu'.format(libCXXRoot, osType)
		libCXXDetailsOverride = ThirdPartyLibraryDetails(
			prefixDirs  = [],
			includeDirs = [
				'{}/include'.format(libCXXRoot),
				'{}/include/c++/v1'.format(libCXXRoot)
			],
			linkDirs    = [libCXXLibDir],
			libs        = ['{}/libc++.a'.format(libCXXLibDir), '{}/libc++abi.a'.format(libCXXLibDir), '-lm', '-lc', '-lgcc_s', '-lgcc'],
			cxxFlags    = ['-fPIC', '-nostdinc++'],
			ldFlags     = ['-nodefaultlibs'],
			cmakeFlags  = []
		)
		
		return {'libc++': libCXXDetailsOverride}
