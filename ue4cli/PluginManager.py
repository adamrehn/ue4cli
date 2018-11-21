from inspect import signature
import pkg_resources

class PluginManager:
	"""
	Provides functionality to detect ue4cli plugins
	"""
	
	@staticmethod
	def getPlugins():
		"""
		Returns the list of valid ue4cli plugins
		"""
		
		# Retrieve the list of detected entry points in the ue4cli.plugins group
		plugins = {
			entry_point.name: entry_point.load()
			for entry_point
			in pkg_resources.iter_entry_points('ue4cli.plugins')
		}
		
		# Filter out any invalid plugins
		plugins = {
			name: plugins[name]
			for name in plugins
			if
				'action' in plugins[name] and
				'description' in plugins[name] and
				'args' in plugins[name] and
				callable(plugins[name]['action']) == True and
				len(signature(plugins[name]['action']).parameters) == 2
		}
		
		return plugins
