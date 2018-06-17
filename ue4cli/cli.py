from __future__ import print_function
from collections import OrderedDict
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
	
	'run': {
		'description': 'Run the editor for the Unreal project',
		'action': lambda m, args: m.runEditor(os.getcwd()),
		'args': None
	},
	
	'gen': {
		'description': 'Generate IDE project files for the Unreal project',
		'action': lambda m, args: m.generateProjectFiles(os.getcwd()),
		'args': None
	},
	
	'build': {
		'description': 'Build the editor for the Unreal project',
		'action': lambda m, args: m.buildProject(os.getcwd(), args[0] if len(args) > 0 else 'Development'),
		'args': '[CONFIGURATION]'
	},
	
	'clean': {
		'description': 'Clean the Unreal project',
		'action': lambda m, args: m.cleanProject(os.getcwd()),
		'args': None
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
		'commands': ['root', 'version']
	},
	{
		'name': 'Project-related commands',
		'description': 'These commands relate to an individual Unreal project, and will look\nfor a .uproject file located in the current working directory:',
		'commands': ['run', 'gen', 'build', 'clean']
	},
	{
		'name': 'Library-related commands',
		'description': 'These commands are for developers compiling modules that need to build against\nUE4-bundled third-party libs for purposes of interoperability with the engine:',
		'commands': ['libs', 'cxxflags', 'ldflags', 'cmakeflags', 'includedirs', 'libfiles', 'defines']
	},
	{
		'name': 'Automation-related commands',
		'description': 'These commands relate to Unreal\'s automation system. Unless explicitly\nspecified, the platform and project file path arguments will be\nautomatically generated when invoking RunUAT:',
		'commands': ['uat']
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
		for command in group['commands']:
			commandStr = '\t' + command
			if SUPPORTED_COMMANDS[command]['args'] != None:
				commandStr += ' ' + SUPPORTED_COMMANDS[command]['args']
			commandStr += ' - ' + SUPPORTED_COMMANDS[command]['description']
			print(commandStr)
		print()

def main():
	try:
		
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
