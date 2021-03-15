from .ThirdPartyLibraryDetails import ThirdPartyLibraryDetails
from .UnrealManagerException import UnrealManagerException
from .UnrealManagerUnix import UnrealManagerUnix
from .Utility import Utility
import re, os

# Details for libc++
LIBCXX_LIBDIR = '%UE4_ROOT%/Engine/Source/ThirdParty/Linux/LibCxx/lib/Linux/x86_64-unknown-linux-gnu'
LIBCXX_DETAILS_OVERRIDE = ThirdPartyLibraryDetails(
	prefixDirs  = [],
	includeDirs = [
		'%UE4_ROOT%/Engine/Source/ThirdParty/Linux/LibCxx/include',
		'%UE4_ROOT%/Engine/Source/ThirdParty/Linux/LibCxx/include/c++/v1'
	],
	linkDirs    = [LIBCXX_LIBDIR],
	libs        = ['{}/libc++.a'.format(LIBCXX_LIBDIR), '{}/libc++abi.a'.format(LIBCXX_LIBDIR), '-lm', '-lc', '-lgcc_s', '-lgcc'],
	cxxFlags    = ['-fPIC', '-nostdinc++'],
	ldFlags     = ['-nodefaultlibs'],
	cmakeFlags  = []
)

class UnrealManagerLinux(UnrealManagerUnix):
	
	def getPlatformIdentifier(self):
		return 'Linux'
	
	def _detectEngineRoot(self):
		
		# If UE4Editor is available in the PATH, use its location to detect the root directory path
		editorLoc = Utility.capture(['which', 'UE4Editor']).stdout.strip()
		if editorLoc != '':
			editorLoc = os.path.dirname(os.path.realpath(editorLoc))
			return os.path.abspath(editorLoc + '/../../..')
		
		# Under Debian-based systems, we can use the desktop integration to find UE4Editor
		potentialLauncherPaths = [
			os.path.join(os.environ['HOME'], '.local', 'share', 'applications', 'UE4Editor.desktop'),
			os.path.join(os.environ['HOME'], '.local', 'share', 'applications', 'com.epicgames.UnrealEngineEditor.desktop')
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
		raise UnrealManagerException('could not detect the location of the latest installed Unreal Engine 4 version')
	
	def _editorPathSuffix(self, cmdVersion):
		return ''
	
	# Under Linux, we always need to build against Unreal's bundled libc++
	def _defaultThirdpartyLibs(self):
		return ['libc++']
	
	def _getLibraryOverrides(self):
		return {'libc++': LIBCXX_DETAILS_OVERRIDE}
