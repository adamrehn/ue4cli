from .ConfigurationManager import ConfigurationManager
from .JsonDataManager import JsonDataManager
from .Utility import Utility
import os

class CachedDataManager(object):
	"""
	Provides functionality for caching data about different engine versions
	"""
	
	@staticmethod
	def clearCache():
		"""
		Clears any cached data we have stored about specific engine versions
		"""
		if os.path.exists(CachedDataManager._cacheDir()) == True:
			Utility.removeDir(CachedDataManager._cacheDir())
	
	@staticmethod
	def getCachedDataKey(engineVersionHash, key):
		"""
		Retrieves the cached data value for the specified engine version hash and dictionary key
		"""
		cacheFile = CachedDataManager._cacheFileForHash(engineVersionHash)
		return JsonDataManager(cacheFile).getKey(key)
	
	@staticmethod
	def setCachedDataKey(engineVersionHash, key, value):
		"""
		Sets the cached data value for the specified engine version hash and dictionary key
		"""
		cacheFile = CachedDataManager._cacheFileForHash(engineVersionHash)
		return JsonDataManager(cacheFile).setKey(key, value)
	
	# "Private" methods
	
	@staticmethod
	def _cacheDir():
		return os.path.join(ConfigurationManager.getConfigDirectory(), 'cache')
	
	@staticmethod
	def _cacheFileForHash(hash):
		return os.path.join(CachedDataManager._cacheDir(), hash + '.json')
