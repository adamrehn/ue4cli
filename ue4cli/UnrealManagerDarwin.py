from .ThirdPartyLibraryDetails import ThirdPartyLibraryDetails
from .UnrealManagerException import UnrealManagerException
from .UnrealManagerUnix import UnrealManagerUnix
from .Utility import Utility
from pkg_resources import parse_version
import glob, os

class UnrealManagerDarwin(UnrealManagerUnix):
	
	def getPlatformIdentifier(self):
		return 'Mac'
	
	def getGenerateScript(self):
		genScript = super(UnrealManagerDarwin, self).getGenerateScript()
		
		# Under macOS, ensure `GenerateLLDBInit.sh` has been run at least one
		Utility.run(['sh', os.path.join(os.path.dirname(genScript), 'GenerateLLDBInit.sh')])
		
		return genScript
	
	def _detectEngineRoot(self):
		
		# Under macOS, the default installation path is `/Users/Shared/Epic Games/UE_4.XX/UE_5.XX`
		baseDir = '/Users/Shared/Epic Games/'
		version = parse_version(self.getEngineVersion())
		if version < parse_version('5.0.0'):
			prefix = 'UE_4.'
		else:
			prefix = 'UE_5.'
		prefix = 'UE_4.'
		versionDirs = glob.glob(baseDir + prefix + '*')
		if len(versionDirs) > 0:
			installedVersions = sorted([int(os.path.basename(d).replace(prefix, '')) for d in versionDirs])
			newestVersion = max(installedVersions)
			return baseDir + prefix + str(newestVersion)
		
		# Could not auto-detect the Unreal Engine location
		raise UnrealManagerException('could not detect the location of the latest installed Unreal Engine version')
	
	def _editorPathSuffix(self, cmdVersion):
		version = parse_version(self.getEngineVersion())
		if version < parse_version('5.0.0'):
			return '.app/Contents/MacOS/UE4Editor'
		else:
			return '.app/Contents/MacOS/UnrealEditor'
	
	def _transformBuildToolPlatform(self, platform):
		# Prior to 4.22.2, Build.sh under Mac requires "macosx" as the platform name for macOS
		version = parse_version(self.getEngineVersion())
		return 'macosx' if platform == 'Mac' and version < parse_version('4.22.2') else platform
	
	def _getRunXBuildScript(self):
		xbuildScript = super(UnrealManagerDarwin, self)._getRunXBuildScript()
		
		# Under macOS, `SetupMono.sh` does not detect Mono 5.x correctly by default
		setupScript = os.path.join(os.path.dirname(xbuildScript), 'SetupMono.sh')
		Utility.patchFile(setupScript, {
"""
	MONO_VERSION=(`echo ${MONO_VERSION:MONO_VERSION_PREFIX_LEN} |tr '.' ' '`)
	if [ ${MONO_VERSION[0]} -ge 4 ]; then
""":
"""
	MONO_VERSION=(`echo ${MONO_VERSION:MONO_VERSION_PREFIX_LEN} |tr '.' ' '`)
	if [ ${MONO_VERSION[0]} -ge 5 ]; then IS_MONO_INSTALLED=1; fi
	if [ ${MONO_VERSION[0]} -ge 4 ]; then
"""
		})
		
		return xbuildScript
