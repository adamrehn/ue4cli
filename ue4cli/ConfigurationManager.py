from .JsonDataManager import JsonDataManager
import os, platform

class ConfigurationManager(object):
	"""
	Provides functionality for managing the application's per-user configuration data
	"""
	
	@staticmethod
	def getConfigDirectory():
		"""
		Determines the platform-specific config directory location for ue4cli
		"""
		if platform.system() == 'Windows':
			return os.path.join(os.environ['APPDATA'], 'ue4cli')
		else:
			return os.path.join(os.environ['HOME'], '.config', 'ue4cli')
	
	@staticmethod
	def getConfigKey(key):
		"""
		Retrieves the config data value for the specified dictionary key
		"""
		configFile = ConfigurationManager._configFile()
		return JsonDataManager(configFile).getKey(key)
	
	@staticmethod
	def setConfigKey(key, value):
		"""
		Sets the config data value for the specified dictionary key
		"""
		configFile = ConfigurationManager._configFile()
		return JsonDataManager(configFile).setKey(key, value)
	
	# "Private" methods
	
	@staticmethod
	def _configFile():
		return os.path.join(ConfigurationManager.getConfigDirectory(), 'config.json')
