import platform

# Import the implementation for the current platform
if platform.system() == 'Windows':
	from .UnrealManagerWindows import UnrealManagerWindows as UnrealManagerImp
elif platform.system() == 'Darwin':
	from .UnrealManagerDarwin import UnrealManagerDarwin as UnrealManagerImp
else:
	from .UnrealManagerLinux import UnrealManagerLinux as UnrealManagerImp

class UnrealManagerFactory:
	"""
	Factory class for creating UnrealManagerBase instances
	"""
	
	@staticmethod
	def create():
		"""
		Creates an Unreal manager instance for the current platform
		"""
		return UnrealManagerImp()
