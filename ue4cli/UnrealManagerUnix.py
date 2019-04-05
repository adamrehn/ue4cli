from .UnrealManagerBase import UnrealManagerBase
from .Utility import Utility
import os

class UnrealManagerUnix(UnrealManagerBase):
	
	def getBuildScript(self):
		return os.path.join(self.getEngineRoot(), 'Engine', 'Build', 'BatchFiles', self.getPlatformIdentifier(), 'Build.sh')
	
	def getGenerateScript(self):
		return os.path.join(self.getEngineRoot(), 'Engine', 'Build', 'BatchFiles', self.getPlatformIdentifier(), 'GenerateProjectFiles.sh')
	
	def getRunUATScript(self):
		return os.path.join(self.getEngineRoot(), 'Engine', 'Build', 'BatchFiles', 'RunUAT.sh')
	
	def _runDotNetApplication(self, exeFile, args = []):
		scriptFile = self._getRunMonoScript()
		scriptDir = os.path.dirname(scriptFile)
		return Utility.capture([scriptFile, exeFile] + args, cwd=scriptDir, raiseOnError=True)
	
	def _buildDotNetProject(self, projectFile):
		scriptFile = self._getRunXBuildScript()
		scriptDir = os.path.dirname(scriptFile)
		return Utility.capture([scriptFile, '/property:Configuration=Release', '/property:TargetFrameworkVersion=v4.5', projectFile], cwd=scriptDir, raiseOnError=True)
	
	
	# "Private" methods
	
	def _getRunMonoScript(self):
		"""
		Determines the location of the script file to run mono
		"""
		return os.path.join(self.getEngineRoot(), 'Engine', 'Build', 'BatchFiles', self.getPlatformIdentifier(), 'RunMono.sh')
	
	def _getRunXBuildScript(self):
		"""
		Determines the location of the script file to run mono's XBuild tool
		"""
		return os.path.join(self.getEngineRoot(), 'Engine', 'Build', 'BatchFiles', self.getPlatformIdentifier(), 'RunXBuild.sh')
