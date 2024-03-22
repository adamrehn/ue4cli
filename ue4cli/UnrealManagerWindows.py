from .UnrealManagerException import UnrealManagerException
from .UnrealManagerBase import UnrealManagerBase
from .Utility import Utility
import glob, os, platform

# The (_)winreg module is named differently between Python 2.x and Python 3.x
try:
	import winreg
except:
	import _winreg as winreg

class UnrealManagerWindows(UnrealManagerBase):
	
	def getPlatformIdentifier(self):
		if platform.machine().endswith('64'):
			return 'Win64'
		else:
			return 'Win32'
	
	def getBuildScript(self):
		return self.getEngineRoot() + '\\Engine\\Build\\BatchFiles\\Build.bat'
	
	def getGenerateScript(self):
		
		# Under Windows, GenerateProjectFiles.bat only exists for source builds of the engine
		batFile = self.getEngineRoot() + '\\Engine\\Build\\BatchFiles\\GenerateProjectFiles.bat'
		if os.path.exists(batFile):
			return batFile
		
		# For versions of the engine installed using the launcher, we need to query the shell integration
		# to determine the location of the Unreal Version Selector executable, which generates VS project files
		try:
			key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'Unreal.ProjectFile\\shell\\rungenproj\\command')
			if key:
				command = winreg.QueryValue(key, None)
				if len(command) > 0:
					
					# Write the command to run UnrealVersionSelector.exe to our own batch file
					customBat = os.path.join(self._customBatchScriptDir(), 'GenerateProjectFiles.bat')
					Utility.writeFile(customBat, command.replace('"%1"', '%1') + '\r\n')
					return customBat
		except:
			pass
		
		raise UnrealManagerException('could not detect the location of GenerateProjectFiles.bat or UnrealVersionSelector.exe.\nThis typically indicates that .uproject files are not correctly associated with UE4.')
	
	def getRunUATScript(self):
		return self.getEngineRoot() + '\\Engine\\Build\\BatchFiles\\RunUAT.bat'
	
	def generateProjectFiles(self, dir=os.getcwd(), args=[]):
		
		# If we are using our custom batch file, use the appropriate arguments
		genScript = self.getGenerateScript()
		projectFile = self.getProjectDescriptor(dir)
		Utility.printStderr('Using project file:', projectFile)
		if '.ue4\\GenerateProjectFiles.bat' in genScript:
			Utility.run([genScript, projectFile], raiseOnError=True)
		else:
			super(UnrealManagerWindows, self).generateProjectFiles(dir, args)
	
	def _detectEngineRoot(self):
		
		# Under Windows, the default installation path is `%PROGRAMFILES%\Epic Games`
		baseDir = os.environ['PROGRAMFILES'] + '\\Epic Games\\'
		prefixes = ['UE_5.', 'UE_4.']
		for prefix in prefixes:
			versionDirs = glob.glob(baseDir + prefix + '*')
			if len(versionDirs) > 0:
				installedVersions = sorted([int(os.path.basename(d).replace(prefix, '')) for d in versionDirs])
				newestVersion = max(installedVersions)
				return baseDir + prefix + str(newestVersion)
		
		# Could not auto-detect the Unreal Engine location
		return None
	
	def _editorPathSuffix(self, cmdVersion):
		return '-Cmd.exe' if cmdVersion == True else '.exe'
	
	def _runDotNetApplication(self, exeFile, args = []):
		return Utility.capture([exeFile] + args, raiseOnError=True)
	
	def _buildDotNetProject(self, projectFile):
		msbuildExe = self._getMsbuildLocation()
		return Utility.capture([msbuildExe, '/property:Configuration=Release', '/property:TargetFrameworkVersion=v4.5', projectFile], raiseOnError=True)
	
	
	# "Private" methods
	
	def _customBatchScriptDir(self):
		
		# If the script directory doesn't already exist, attempt to create it
		scriptDir = os.path.join(os.environ['HOMEDRIVE'] + os.environ['HOMEPATH'], '.ue4')
		try:
			os.makedirs(scriptDir)
		except:
			pass
		
		return scriptDir
	
	def _getMsbuildLocation(self):
		
		# `GetMSBuildPath.bat` sets the path to an environment variable instead of printing it,
		# so we need to wrap it in another script to print the value so it can be captured
		msbuildBat = os.path.join(os.path.dirname(self.getBuildScript()), 'GetMSBuildPath.bat')
		customBat = os.path.join(self._customBatchScriptDir(), 'PrintMSBuildPath.bat')
		Utility.writeFile(customBat, '@echo off\r\ncall "' + msbuildBat + '"\r\necho %MSBUILD_EXE%')
		return Utility.capture([customBat], raiseOnError=True).stdout.strip().strip('"')
