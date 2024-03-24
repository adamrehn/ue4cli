from .UnrealManagerException import UnrealManagerException
from .Utility import Utility
from .UtilityException import UtilityException
import json, os

class JsonDataManager(object):
	"""
	Provides functionality for interacting with a JSON-formatted dictionary file
	"""
	
	def __init__(self, jsonFile):
		"""
		Creates a new JsonDataManager instance for the specified JSON file
		"""
		self.jsonFile = jsonFile

	def loads(self):
		"""
		Reads and loads owned jsonFile
		"""
		try:
			path = self.jsonFile
			file = Utility.readFile(path)
			return json.loads(file)
		except json.JSONDecodeError as e:
			# FIXME: This is the only place outside of Utility class where we use UtilityException.
			# Not worth to create new Exception class for only one single case, at least not now.
			raise UtilityException(f'failed to load "{str(path)}" due to: ({type(e).__name__}) {str(e)}') from e
	
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
			return self.loads()
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
			Utility.makeDirs(jsonDir)
		
		# Store the dictionary
		Utility.writeFile(self.jsonFile, json.dumps(data))
