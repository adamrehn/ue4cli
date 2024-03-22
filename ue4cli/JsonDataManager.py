from .UnrealManagerException import UnrealManagerException
from .Utility import Utility
import json, os, platform

class JsonDataManager(object):
	"""
	Provides functionality for interacting with a JSON-formatted dictionary file
	"""
	
	def __init__(self, jsonFile):
		"""
		Creates a new JsonDataManager instance for the specified JSON file
		"""
		self.jsonFile = jsonFile
	
	def getKey(self, key):
		"""
		Retrieves the value for the specified dictionary key
		"""
		data = self.getDictionary()
		if key in data:
			return data[key]
		else:
			return None
	
	def getDictionary(self):
		"""
		Retrieves the entire data dictionary
		"""
		if os.path.exists(self.jsonFile):
			return json.loads(Utility.readFile(self.jsonFile))
		else:
			return {}
	
	def setKey(self, key, value):
		"""
		Sets the value for the specified dictionary key
		"""
		data = self.getDictionary()
		data[key] = value
		self.setDictionary(data)
	
	def setDictionary(self, data):
		"""
		Overwrites the entire dictionary
		"""
		
		# Create the directory containing the JSON file if it doesn't already exist
		jsonDir = os.path.dirname(self.jsonFile)
		if os.path.exists(jsonDir) == False:
			os.makedirs(jsonDir)
		
		# Store the dictionary
		Utility.writeFile(self.jsonFile, json.dumps(data))
