from collections import OrderedDict
from .PluginManager import PluginManager
from .UnrealManagerException import UnrealManagerException
from .UnrealManagerFactory import UnrealManagerFactory
import os, sys

# Our list of supported commands
SUPPORTED_COMMANDS = {
	
	'help': {
		'description': 'Display usage syntax',
		'action': lambda m, args: displayHelp(),
		'args': None
	},
	
	'setroot': {
		'description': 'Sets an engine root path override that supercedes auto-detect',
		'action': lambda m, args: m.setEngineRootOverride(args[0]),
		'args': '<ROOTDIR>'
	},
	
	'clearroot': {
		'description': 'Removes any previously-specified engine root path override',
		'action': lambda m, args: m.clearEngineRootOverride(),
		'args': None
	},
	
	'clearcache': {
		'description': 'Clears any cached data that ue4cli has stored',
		'action': lambda m, args: m.clearCachedData(),
		'args': None
	},
	
	'root': {
		'description': 'Print the path to the root directory of the Unreal Engine',
		'action': lambda m, args: print(m.getEngineRoot()),
		'args': None
	},
	
	'version': {
		'description': 'Print the version string of the Unreal Engine (default format is "full")',
		'action': lambda m, args: print(m.getEngineVersion(args[0] if len(args) > 0 else 'full')),
		'args': '[major|minor|patch|full|short]'
	},
	
	'editor': {
		'description': 'Run the editor without an Unreal project (useful for creating new projects)',
		'action': lambda m, args: m.runEditor(None, False, args),
		'args': '[EXTRA ARGS]'
	},
	
	'run': {
		'description': 'Run the editor for the Unreal project',
		'action': lambda m, args: m.runEditor(
			os.getcwd(),
			True if '--debug' in args else False,
			list([arg for arg in args if arg != '--debug'])
		),
		'args': '[--debug] [EXTRA ARGS]'
	},
	
	'gen': {
		'description': 'Generate IDE project files for the Unreal project',
		'action': lambda m, args: m.generateProjectFiles(os.getcwd(), args),
		'args': '[EXTRA ARGS]'
	},
	
	'build': {
		'description': 'Build the Editor modules for the Unreal project or plugin',
		'action': lambda m, args: m.buildDescriptor(os.getcwd(), args.pop(0) if len(args) > 0 else 'Development', args.pop(0) if len(args) > 0 else '', args),
		'args': '[CONFIGURATION] [TARGET]'
	},
	
	'clean': {
		'description': 'Clean build artifacts for the Unreal project or plugin',
		'action': lambda m, args: m.cleanDescriptor(os.getcwd()),
		'args': None
	},
	
	'test': {
		'description': 'Run automation tests for the Unreal project',
		'action': lambda m, args: m.automationTests(os.getcwd(), args),
		'args': '[--list] [--all] [--filter FILTER] TEST1 TEST2 TESTN [-- EXTRA ARGS]'
	},
	
	'package': {
		'description': 'Package a build of the Unreal project or plugin in the current directory, storing the result in a subdirectory named "dist". Default configuration for projects is Shipping.',
		'action': lambda m, args: m.packageDescriptor(os.getcwd(), args),
		'args': '[PROJECT CONFIGURATION] [EXTRA UAT ARGS]'
	},
	
	'libs': {
		'description': 'List the supported third-party libs',
		'action': lambda m, args: print('\n'.join(m.listThirdPartyLibs())),
		'args': None
	},
	
	'cxxflags': {
		'description': 'Print compiler flags for building against libs',
		'action': lambda m, args: print(m.getThirdPartyLibCompilerFlags(args)),
		'args': '[--multiline] [--nodefaults] [LIBS]'
	},
	
	'ldflags': {
		'description': 'Print linker flags for building against libs',
		'action': lambda m, args: print(m.getThirdPartyLibLinkerFlags(args)),
		'args': '[--multiline] [--flagsonly] [--nodefaults] [LIBS]'
	},
	
	'cmakeflags': {
		'description': 'Print CMake flags for building against libs',
		'action': lambda m, args: print(m.getThirdPartyLibCmakeFlags(args)),
		'args': '[--multiline] [--nodefaults] [LIBS]'
	},
	
	'includedirs': {
		'description': 'Print include directories for building against libs',
		'action': lambda m, args: print(m.getThirdPartyLibIncludeDirs(args)),
		'args': '[--nodefaults] [LIBS]'
	},
	
	'libfiles': {
		'description': 'Print library files for building against libs',
		'action': lambda m, args: print(m.getThirdPartyLibFiles(args)),
		'args': '[--nodefaults] [LIBS]'
	},
	
	'defines': {
		'description': 'Print preprocessor definitions for building against libs',
		'action': lambda m, args: print(m.getThirdPartyLibDefinitions(args)),
		'args': '[--nodefaults] [LIBS]'
	},
	
	'uat': {
		'description': 'Invoke RunUAT with the specified arguments',
		'action': lambda m, args: m.runUAT(args),
		'args': '[ARGS]'
	}
}

# The groupings for our supported commands
COMMAND_GROUPINGS = [
	{
		'name': 'Configuration-related commands',
		'description': 'These commands control the configuration of ue4cli:',
		'commands': ['setroot', 'clearroot', 'clearcache']
	},
	{
		'name': 'Engine-related commands',
		'description': 'These commands relate to the Unreal Engine itself:',
		'commands': ['root', 'version', 'editor']
	},
	{
		'name': 'Descriptor-related commands',
		'description': 'These commands relate to an individual Unreal project or plugin, and will look\nfor a .uproject or .uplugin file located in the current working directory\n(Note that some commands only support projects, not plugins):',
		'commands': ['run', 'gen', 'build', 'clean', 'test', 'package']
	},
	{
		'name': 'Library-related commands',
		'description': 'These commands are for developers compiling modules that need to build against\nUE4-bundled third-party libs for purposes of interoperability with the engine:',
		'commands': ['libs', 'cxxflags', 'ldflags', 'cmakeflags', 'includedirs', 'libfiles', 'defines']
	},
	{
		'name': 'Automation-related commands',
		'description': 'These commands relate to Unreal\'s automation system:',
		'commands': ['uat']
	},
	{
		'name': 'Commands defined by plugins',
		'description': 'These commands are defined by currently installed ue4cli plugins:',
		'commands': []
	}
]

def displayHelp():
	print('Usage:')
	print(os.path.basename(sys.argv[0]) + ' COMMAND [ARGS]')
	for group in COMMAND_GROUPINGS:
		print()
		print(group['name'])
		print('-' * len(group['name']))
		print()
		print(group['description'])
		print()
		if len(group['commands']) == 0:
			print('\t(No commands in this group)')
		else:
			for command in group['commands']:
				commandStr = '\t' + command
				if SUPPORTED_COMMANDS[command]['args'] != None:
					commandStr += ' ' + SUPPORTED_COMMANDS[command]['args']
				commandStr += ' - ' + SUPPORTED_COMMANDS[command]['description']
				print(commandStr)
		print()

def main():
	try:
		
		# Perform plugin detection and register our detected plugins
		plugins = PluginManager.getPlugins()
		for command in plugins:
			details = plugins[command]
			if command not in SUPPORTED_COMMANDS:
				SUPPORTED_COMMANDS[command] = details
				COMMAND_GROUPINGS[-1]['commands'].append(command)
		
		# Create the Unreal manager instance for the current platform
		manager = UnrealManagerFactory.create()
		
		# Extract the specified command and any trailing arguments
		command = 'help' if len(sys.argv) < 2 else sys.argv[1].strip('-')
		args = sys.argv[2:]
		
		# If the specified command is supported, invoke it
		if command in SUPPORTED_COMMANDS:
			SUPPORTED_COMMANDS[command]['action'](manager, args)
		else:
			raise UnrealManagerException('unrecognised command "' + command + '"')
		
	except UnrealManagerException as e:
		print('Error: ' + str(e))
		sys.exit(1)
