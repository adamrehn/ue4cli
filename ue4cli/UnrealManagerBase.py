from .ThirdPartyLibraryDetails import PrintingFormat, ThirdPartyLibraryDetails
from .UnrealManagerException import UnrealManagerException
from .ConfigurationManager import ConfigurationManager
from .UE4BuildInterrogator import UE4BuildInterrogator
from .CachedDataManager import CachedDataManager
from .CMakeCustomFlags import CMakeCustomFlags
from .Utility import Utility
import glob, hashlib, json, os, re, shutil, sys

class UnrealManagerBase(object):
	"""
	Base class for platform-specific Unreal manager instances
	"""
	
	def clearCachedData(self):
		"""
		Clears any cached data we have stored about specific engine versions
		"""
		CachedDataManager.clearCache()
	
	def validBuildConfigurations(self):
		"""
		Returns the list of valid build configurations supported by UnrealBuildTool
		"""
		return ['Debug', 'DebugGame', 'Development', 'Shipping', 'Test']
	
	def getPlatformIdentifier(self):
		"""
		Returns the platform identifier for the current platform, as used by UnrealBuildTool
		"""
		pass
	
	def getEngineRootOverride(self):
		"""
		Retrieves the user-specified engine root directory if set, otherwise returns None
		"""
		return ConfigurationManager.getConfigKey('rootDirOverride')
	
	def setEngineRootOverride(self, rootDir):
		"""
		Sets a user-specified directory as the root engine directory, overriding any auto-detection
		"""
				
		# Set the new root directory
		rootDir = os.path.abspath(rootDir)
		ConfigurationManager.setConfigKey('rootDirOverride', rootDir)
		print('Set engine root path override: {}'.format(rootDir))
		
		# Check that the specified directory is valid and warn the user if it is not
		try:
			self.getEngineVersion()
		except:
			print('Warning: the specified directory does not appear to contain a valid version of the Unreal Engine.')
	
	def clearEngineRootOverride(self):
		"""
		Removes any previously-specified root engine directory override
		"""
		ConfigurationManager.setConfigKey('rootDirOverride', None)
	
	def getEngineRoot(self):
		"""
		Returns the root directory location of the latest installed version of UE
		"""
		
		if hasattr(self, '_engineRootCached'):
			return self._engineRootCached
		
		override = self.getEngineRootOverride()
		if override:
			self._engineRootCached = override
			Utility.printStderr('Using user-specified engine root: ' + override)
			return override
		
		autodetect = self._detectEngineRoot()
		if autodetect:
			self._engineRootCached = autodetect
			return autodetect
		
		raise UnrealManagerException('could not detect Unreal Engine root directory! Please, provide it manually via: ue4 setroot <ROOTDIR>')
	
	def getEngineVersion(self, outputFormat = 'full'):
		"""
		Returns the version number of the latest installed version of UE4
		"""
		version = self._getEngineVersionDetails()
		formats = {
			'major': version['MajorVersion'],
			'minor': version['MinorVersion'],
			'patch': version['PatchVersion'],
			'full': '{}.{}.{}'.format(version['MajorVersion'], version['MinorVersion'], version['PatchVersion']),
			'short': '{}.{}'.format(version['MajorVersion'], version['MinorVersion'])
		}
		
		# Verify that the requested output format is valid
		if outputFormat not in formats:
			raise Exception('unreconised version output format "{}"'.format(outputFormat))
		
		return formats[outputFormat]
	
	def getEngineChangelist(self):
		"""
		Returns the compatible Perforce changelist identifier for the latest installed version of UE4
		"""
		
		# Newer versions of the engine use the key "CompatibleChangelist", older ones use "Changelist"
		version = self._getEngineVersionDetails()
		if 'CompatibleChangelist' in version:
			return int(version['CompatibleChangelist'])
		else:
			return int(version['Changelist'])
	
	def isInstalledBuild(self):
		"""
		Determines if the Engine is an Installed Build
		"""
		sentinelFile = os.path.join(self.getEngineRoot(), 'Engine', 'Build', 'InstalledBuild.txt')
		return os.path.exists(sentinelFile)
	
	def getEditorBinary(self, cmdVersion=False):
		"""
		Determines the location of the UE4Editor/UnrealEditor binary
		"""
		if self._getEngineVersionDetails()['MajorVersion'] >= 5:
			return os.path.join(self.getEngineRoot(), 'Engine', 'Binaries', self.getPlatformIdentifier(), 'UnrealEditor' + self._editorPathSuffix(cmdVersion))
		else:
			return os.path.join(self.getEngineRoot(), 'Engine', 'Binaries', self.getPlatformIdentifier(), 'UE4Editor' + self._editorPathSuffix(cmdVersion))	

	def getBuildScript(self):
		"""
		Determines the location of the script file to perform builds
		"""
		pass
	
	def getGenerateScript(self):
		"""
		Determines the location of the script file to generate IDE project files
		"""
		pass
	
	def getRunUATScript(self):
		"""
		Determines the location of the script file to run the Unreal Automation Tool
		"""
		pass
	
	def getProjectDescriptor(self, dir):
		"""
		Detects the .uproject descriptor file for the Unreal project in the specified directory
		"""
		for project in glob.glob(os.path.join(dir, '*.uproject')):
			return os.path.realpath(project)
		
		# No project detected
		raise UnrealManagerException('could not detect an Unreal project in the current directory')
	
	def getPluginDescriptor(self, dir):
		"""
		Detects the .uplugin descriptor file for the Unreal plugin in the specified directory
		"""
		for plugin in glob.glob(os.path.join(dir, '*.uplugin')):
			return os.path.realpath(plugin)
		
		# No plugin detected
		raise UnrealManagerException('could not detect an Unreal plugin in the current directory')
	
	def getDescriptor(self, dir):
		"""
		Detects the descriptor file for either an Unreal project or an Unreal plugin in the specified directory
		"""
		try:
			return self.getProjectDescriptor(dir)
		except:
			try:
				return self.getPluginDescriptor(dir)
			except:
				raise UnrealManagerException('could not detect an Unreal project or plugin in the directory "{}"'.format(dir))
	
	def isProject(self, descriptor):
		"""
		Determines if the specified descriptor file is for an Unreal project
		"""
		return descriptor.endswith('.uproject')
	
	def isPlugin(self, descriptor):
		"""
		Determines if the specified descriptor file is for an Unreal plugin
		"""
		return descriptor.endswith('.uplugin')
	
	def getDescriptorName(self, descriptor):
		"""
		Determines the name of the Unreal project or plugin represented by the specified descriptor file
		"""
		return os.path.basename(descriptor).replace('.uproject', '').replace('.uplugin', '')
	
	def listThirdPartyLibs(self, configuration = 'Development'):
		"""
		Lists the supported Unreal-bundled third-party libraries
		"""
		interrogator = self._getUE4BuildInterrogator()
		return interrogator.list(self.getPlatformIdentifier(), configuration, self._getLibraryOverrides())
	
	def getThirdpartyLibs(self, libs, configuration = 'Development', includePlatformDefaults = True):
		"""
		Retrieves the ThirdPartyLibraryDetails instance for Unreal-bundled versions of the specified third-party libraries
		"""
		if includePlatformDefaults == True:
			libs = self._defaultThirdpartyLibs() + libs
		interrogator = self._getUE4BuildInterrogator()
		return interrogator.interrogate(self.getPlatformIdentifier(), configuration, libs, self._getLibraryOverrides())
	
	def getThirdPartyLibCompilerFlags(self, libs):
		"""
		Retrieves the compiler flags for building against the Unreal-bundled versions of the specified third-party libraries
		"""
		fmt = PrintingFormat.singleLine()
		platformDefaults = True

		if libs:
			if libs[0] == '--multiline':
				fmt = PrintingFormat.multiLine()
				libs = libs[1:]

			if libs[0] == '--nodefaults':
				platformDefaults = False
				libs = libs[1:]

		details = self.getThirdpartyLibs(libs, includePlatformDefaults=platformDefaults)
		return details.getCompilerFlags(self.getEngineRoot(), fmt)
	
	def getThirdPartyLibLinkerFlags(self, libs):
		"""
		Retrieves the linker flags for building against the Unreal-bundled versions of the specified third-party libraries
		"""
		fmt = PrintingFormat.singleLine()
		includeLibs = True
		platformDefaults = True

		if libs:
			if libs[0] == '--multiline':
				fmt = PrintingFormat.multiLine()
				libs = libs[1:]

			if (libs[0] == '--flagsonly'):
				includeLibs = False
				libs = libs[1:]

			if libs[0] == '--nodefaults':
				platformDefaults = False
				libs = libs[1:]

		details = self.getThirdpartyLibs(libs, includePlatformDefaults=platformDefaults)
		return details.getLinkerFlags(self.getEngineRoot(), fmt, includeLibs)
	
	def getThirdPartyLibCmakeFlags(self, libs):
		"""
		Retrieves the CMake invocation flags for building against the Unreal-bundled versions of the specified third-party libraries
		"""
		fmt = PrintingFormat.singleLine()
		platformDefaults = True

		if libs:
			if libs[0] == '--multiline':
				fmt = PrintingFormat.multiLine()
				libs = libs[1:]

			if libs[0] == '--nodefaults':
				platformDefaults = False
				libs = libs[1:]

		details = self.getThirdpartyLibs(libs, includePlatformDefaults=platformDefaults)
		CMakeCustomFlags.processLibraryDetails(details)
		return details.getCMakeFlags(self.getEngineRoot(), fmt)
	
	def getThirdPartyLibIncludeDirs(self, libs):
		"""
		Retrieves the list of include directories for building against the Unreal-bundled versions of the specified third-party libraries
		"""
		platformDefaults = True
		if libs and libs[0] == '--nodefaults':
			platformDefaults = False
			libs = libs[1:]

		details = self.getThirdpartyLibs(libs, includePlatformDefaults=platformDefaults)
		return details.getIncludeDirectories(self.getEngineRoot(), delimiter='\n')
	
	def getThirdPartyLibFiles(self, libs):
		"""
		Retrieves the list of library files for building against the Unreal-bundled versions of the specified third-party libraries
		"""
		platformDefaults = True
		if libs and libs[0] == '--nodefaults':
			platformDefaults = False
			libs = libs[1:]

		details = self.getThirdpartyLibs(libs, includePlatformDefaults=platformDefaults)
		return details.getLibraryFiles(self.getEngineRoot(), delimiter='\n')
	
	def getThirdPartyLibDefinitions(self, libs):
		"""
		Retrieves the list of preprocessor definitions for building against the Unreal-bundled versions of the specified third-party libraries
		"""
		platformDefaults = True
		if libs and libs[0] == '--nodefaults':
			platformDefaults = False
			libs = libs[1:]
		
		details = self.getThirdpartyLibs(libs, includePlatformDefaults=platformDefaults)
		return details.getPreprocessorDefinitions(self.getEngineRoot(), delimiter='\n')
	
	def generateProjectFiles(self, dir=os.getcwd(), args=[]):
		"""
		Generates IDE project files for the Unreal project in the specified directory
		"""
		
		# If the project is a pure Blueprint project, then we cannot generate project files
		if os.path.exists(os.path.join(dir, 'Source')) == False:
			Utility.printStderr('Pure Blueprint project, nothing to generate project files for.')
			return
		
		# Generate the project files
		genScript = self.getGenerateScript()
		projectFile = self.getProjectDescriptor(dir)
		Utility.run([genScript, '-project=' + projectFile, '-game', '-engine'] + args, cwd=os.path.dirname(genScript), raiseOnError=True)
	
	def cleanDescriptor(self, dir=os.getcwd()):
		"""
		Cleans the build artifacts for the Unreal project or plugin in the specified directory
		"""
		
		# Verify that an Unreal project or plugin exists in the specified directory
		descriptor = self.getDescriptor(dir)
		
		# Because performing a clean will also delete the engine build itself when using
		# a source build, we simply delete the `Binaries` and `Intermediate` directories
		shutil.rmtree(os.path.join(dir, 'Binaries'), ignore_errors=True)
		shutil.rmtree(os.path.join(dir, 'Intermediate'), ignore_errors=True)
		
		# If we are cleaning a project, also clean any plugins
		if self.isProject(descriptor):
			projectPlugins = glob.glob(os.path.join(dir, 'Plugins', '**', '*.uplugin'), recursive=True)
			for plugin in projectPlugins:
				self.cleanDescriptor(os.path.dirname(plugin))
	
	def buildDescriptor(self, dir=os.getcwd(), configuration='Development', target='Editor', args=[], suppressOutput=False):
		"""
		Builds the editor modules for the Unreal project or plugin in the specified directory, using the specified build configuration
		"""
		
		# Verify that an Unreal project or plugin exists in the specified directory
		descriptor = self.getDescriptor(dir)
		descriptorType = 'project' if self.isProject(descriptor) else 'plugin'
		
		# If the project or plugin is Blueprint-only, there is no C++ code to build
		if os.path.exists(os.path.join(dir, 'Source')) == False:
			Utility.printStderr('Pure Blueprint {}, nothing to build.'.format(descriptorType))
			return
		
		# Verify that the specified build configuration is valid
		if configuration not in self.validBuildConfigurations():
			raise UnrealManagerException('invalid build configuration "' + configuration + '"')
		
		# Check if the user specified the `-notools` flag to opt out of building Engine tools when working with source builds
		unstripped = list(args)
		args = Utility.stripArgs(args, ['-notools'])
		noTools = len(unstripped) > len(args)
		
		# If we're using a source build of the Engine then make sure ShaderCompileWorker is built before building project Editor modules
		if noTools == False and self.isInstalledBuild() == False and self.isProject(descriptor) and target == 'Editor':
			Utility.printStderr('Ensuring ShaderCompileWorker is built before building project Editor modules...')
			self.buildTarget('ShaderCompileWorker', 'Development', [], suppressOutput)
		
		# Generate the arguments to pass to UBT
		if self._getEngineVersionDetails()['MajorVersion'] >= 5:
			target = self.getDescriptorName(descriptor) + target if self.isProject(descriptor) else 'UnrealEditor'
		else:
			target = self.getDescriptorName(descriptor) + target if self.isProject(descriptor) else 'UE4Editor'
		baseArgs = ['-{}='.format(descriptorType) + descriptor]
		
		# Perform the build
		self._runUnrealBuildTool(target, self.getPlatformIdentifier(), configuration, baseArgs + args, suppressOutput)
	
	def buildTarget(self, target, configuration='Development', args=[], suppressOutput=False):
		"""
		Builds the specified target using UBT. Primarily useful for building Engine tools and programs.
		"""
		self._runUnrealBuildTool(target, self.getPlatformIdentifier(), configuration, args, capture=suppressOutput)
	
	def runEditor(self, dir=os.getcwd(), debug=False, args=[]):
		"""
		Runs the editor for the Unreal project in the specified directory (or without a project if dir is None)
		"""
		projectFile = self.getProjectDescriptor(dir) if dir is not None else ''
		extraFlags = ['-debug'] + args if debug == True else args
		Utility.run([self.getEditorBinary(True), projectFile] + extraFlags + ['-stdout', '-FullStdOutLogOutput'], raiseOnError=True)
	
	def runUAT(self, args):
		"""
		Runs the Unreal Automation Tool with the supplied arguments
		"""
		Utility.run([self.getRunUATScript()] + args, cwd=self.getEngineRoot(), raiseOnError=True)
	
	def packageProject(self, dir=os.getcwd(), configuration='Shipping', extraArgs=[]):
		"""
		Packages a build of the Unreal project in the specified directory, using common packaging options
		"""
		
		# Verify that the specified build configuration is valid
		if configuration not in self.validBuildConfigurations():
			raise UnrealManagerException('invalid build configuration "' + configuration + '"')
		
		# Strip out the `-NoCompileEditor` flag if the user has specified it, since the Development version
		# of the Editor modules for the project are needed in order to run the commandlet that cooks content
		extraArgs = Utility.stripArgs(extraArgs, ['-nocompileeditor'])
		
		# Prevent the user from specifying multiple `-platform=` or `-targetplatform=` arguments,
		# and use the current host platform if no platform argument was explicitly specified
		platformArgs = Utility.findArgs(extraArgs, ['-platform=', '-targetplatform='])
		platform = Utility.getArgValue(platformArgs[0]) if len(platformArgs) > 0 else self.getPlatformIdentifier()
		extraArgs = Utility.stripArgs(extraArgs, platformArgs) + ['-platform={}'.format(platform)]
		
		# If we are building a dedicated server then ensure the server platform is set correctly
		serverArg = Utility.findArgs(extraArgs, ['-server'])
		serverPlatformArg = Utility.findArgs(extraArgs, ['-serverplatform=', '-servertargetplatform='])
		if len(serverArg) > 0 and len(serverPlatformArg) == 0:
			extraArgs.append('-serverplatform={}'.format(platform))
		
		# If we are packaging a Shipping build, do not include debug symbols unless explicitly requested
		preserveDebugArg = Utility.findArgs(extraArgs, ['-debuginfo'])
		extraArgs = Utility.stripArgs(extraArgs, ['-debuginfo'])
		if configuration == 'Shipping' and len(preserveDebugArg) == 0:
			extraArgs.append('-nodebuginfo')
		
		# Define the usage of pak files, default value is pak files for all platforms except HTML5
		pakArg = Utility.findArgs(extraArgs, ['-pak', '-package'])
		if len(pakArg) == 0:
			pakArg = '-package' if platform.upper() == 'HTML5' else '-pak'
		else:
			pakArg = ''
		
		# Include the `-allmaps` flag if we are building a client target and haven't specified a list of maps
		buildingClient = (len(Utility.findArgs(extraArgs, ['-noclient'])) == 0)
		specifiedMaps = (len(Utility.findArgs(extraArgs, ['-MapsToCook', '-MapIniSectionsToCook'])) > 0)
		if buildingClient == True and specifiedMaps == False:
			extraArgs.append('-allmaps')
		
		# Automatically set the archive directory if the user has not explicitly specified one
		if (len(Utility.findArgs(extraArgs, ['-archivedirectory='])) == 0):
			extraArgs.extend(['-archivedirectory=' + os.path.join(os.path.abspath(dir), 'dist')])
		
		# Invoke UAT to package the build
		self.runUAT([
			'BuildCookRun'
			] + extraArgs + [
			'-utf8output',
			'-clientconfig=' + configuration,
			'-serverconfig=' + configuration,
			'-project=' + self.getProjectDescriptor(dir),
			'-noP4',
			'-cook',
			'-build',
			'-stage',
			'-prereqs',
			pakArg,
			'-archive'
		])
	
	def packagePlugin(self, dir=os.getcwd(), extraArgs=[]):
		"""
		Packages a build of the Unreal plugin in the specified directory, suitable for use as a prebuilt Engine module
		"""
		
		# Invoke UAT to package the build
		distDir = os.path.join(os.path.abspath(dir), 'dist')
		self.runUAT([
			'BuildPlugin'
			] + extraArgs + [
			'-Plugin=' + self.getPluginDescriptor(dir),
			'-Package=' + distDir
		])
	
	def packageDescriptor(self, dir=os.getcwd(), args=[]):
		"""
		Packages a build of the Unreal project or plugin in the specified directory
		"""
		
		# Verify that an Unreal project or plugin exists in the specified directory
		descriptor = self.getDescriptor(dir)
		
		# Perform the packaging step
		if self.isProject(descriptor):
			self.packageProject(dir, args[0] if len(args) > 0 else 'Shipping', args[1:])
		else:
			self.packagePlugin(dir, args)
	
	def runAutomationCommands(self, projectFile, commands, extraArgs, capture=False, enableRHI=False):
		'''
		Invokes the Automation Test commandlet for the specified project with the supplied automation test commands
		'''
		
		# IMPORTANT IMPLEMENTATION NOTE:
		# We need to format the command as a string and execute it using a shell in order to
		# ensure the "-ExecCmds" argument will be parsed correctly under Windows. This is because
		# the WinMain() function uses GetCommandLineW() to retrieve the raw command-line string,
		# rather than using an argv-style structure. The string is then passed to FParse::Value(),
		# which checks for the presence of a quote character after the equals sign to determine if
		# whitespace should be stripped or preserved. Without the quote character, the spaces in the
		# argument payload will be stripped out, corrupting our list of automation commands and
		# preventing them from executing correctly.
		
		command = '{} {}'.format(Utility.escapePathForShell(self.getEditorBinary(True)), Utility.escapePathForShell(projectFile))
		command += ' -game -buildmachine -stdout -fullstdoutlogoutput -forcelogflush -unattended -nopause -nosplash'
		if enableRHI == False:
			command += ' -nullrhi'
		command += ' -ExecCmds="automation {};quit" '.format(';'.join(commands))
		command += ' '.join([Utility.escapePathForShell(a) for a in extraArgs])
		
		if capture == True:
			return Utility.capture(command, shell=True)
		else:
			Utility.run(command, shell=True)
	
	def listAutomationTests(self, projectFile):
		'''
		Returns the list of supported automation tests for the specified project
		'''
		
		# Attempt to retrieve the list of automation tests
		tests = set()
		testRegex = re.compile('.*LogAutomationCommandLine: Display: \t(.+)')
		logOutput = self.runAutomationCommands(projectFile, ['List'], [], capture=True)
		for line in logOutput.stdout.split('\n'):
			matches = testRegex.search(line)
			if matches != None:
				tests.add(matches[1].strip())
		
		# Detect if the Editor terminated abnormally (i.e. not triggered by `automation quit`)
		# In Unreal Engine 4.27.0, the exit method changed from RequestExit to RequestExitWithStatus
		if 'PlatformMisc::RequestExit(' not in logOutput.stdout and 'PlatformMisc::RequestExitWithStatus(' not in logOutput.stdout:
			raise RuntimeError(
				'failed to retrieve the list of automation tests!' +
				' stdout was: "{}", stderr was: "{}"'.format(logOutput.stdout, logOutput.stderr)
			)
		
		return sorted(list(tests))
	
	def automationTests(self, dir=os.getcwd(), args=[]):
		'''
		Performs automation tests for the Unreal project in the specified directory
		'''
		
		# Determine if rendering should be enabled
		enableRHI = len(Utility.findArgs(args, ['--withrhi'])) > 0
		args = Utility.stripArgs(args, ['--withrhi'])
		
		# Verify that at least one argument was supplied
		if len(args) == 0:
			raise RuntimeError('at least one test name must be specified')
		
		# Gather any additional arguments to pass directly to the Editor
		extraArgs = []
		if '--' in args:
			delimIndex = args.index('--')
			extraArgs = args[delimIndex+1:]
			args = args[:delimIndex]
		
		# Build the project if it isn't already built
		Utility.printStderr('Ensuring project is built...')
		self.buildDescriptor(dir, suppressOutput=True)
		
		# Determine which arguments we are passing to the automation test commandlet
		projectFile = self.getProjectDescriptor(dir)
		if '--list' in args:
			Utility.printStderr('Retrieving automation test list...')
			print('\n'.join(self.listAutomationTests(projectFile)))
		else:
			
			# Sanitise the user-supplied arguments to prevent command injection
			runAll = '--all' in args
			runFilter = '--filter' in args
			sanitised = [arg.replace(',', '').replace(';', '') for arg in args if arg not in ['--all', '--filter']]
			command = []
			
			# Determine if we are enqueueing a 'RunAll' command
			if runAll == True:
				command.append('RunAll')
			
			# Determine if we are enqueueing a 'RunFilter' command
			if runFilter == True and len(sanitised) > 0:
				command.append('RunFilter ' + sanitised.pop(0))
			
			# Enqueue a 'RunTests' command for any individual test names that were specified
			if len(sanitised) > 0:
				command.append('RunTests Now ' + '+'.join(sanitised))
			
			# Attempt to run the automation tests
			Utility.printStderr('Running automation tests...')
			logOutput = self.runAutomationCommands(projectFile, command, extraArgs, capture=True, enableRHI=enableRHI)
			
			# Propagate the log output
			print(logOutput.stdout)
			print(logOutput.stderr)
			
			# Detect abnormal exit conditions (those not triggered by `automation quit`)
			# In Unreal Engine 4.27.0, the exit method changed from RequestExit to RequestExitWithStatus
			if 'PlatformMisc::RequestExit(' not in logOutput.stdout and 'PlatformMisc::RequestExitWithStatus(' not in logOutput.stdout:
				sys.exit(1)
			
			# Since UE4 doesn't consistently produce accurate exit codes across all platforms, we need to rely on
			# text-based heuristics to detect failed automation tests or errors related to not finding any tests to run
			errorStrings = [
				'Incorrect automation command syntax!',
				'Automation Test Failed',
				'Result={Failed}',
				'Found 0 Automation Tests, based on',
				'is not a valid flag to filter on!'
			]
			for errorStr in errorStrings:
				if errorStr in logOutput.stdout:
					sys.exit(1)
			
			# If an explicit exit code was specified in the output text then identify it and propagate it
			match = re.search('TEST COMPLETE\\. EXIT CODE: ([0-9]+)', logOutput.stdout + logOutput.stderr)
			if match is not None:
				sys.exit(int(match.group(1)))
	
	# "Protected" methods
	
	def _detectEngineRoot(self):
		"""
		Determines the root directory location of the latest installed version of UE4
		"""
		pass
	
	def _getEngineVersionDetails(self):
		"""
		Parses the JSON version details for the latest installed version of UE4
		"""
		versionFile = os.path.join(self.getEngineRoot(), 'Engine', 'Build', 'Build.version')
		return json.loads(Utility.readFile(versionFile))
	
	def _getEngineVersionHash(self):
		"""
		Computes the SHA-256 hash of the JSON version details for the latest installed version of UE4
		"""
		versionDetails = self._getEngineVersionDetails()
		hash = hashlib.sha256()
		hash.update(json.dumps(versionDetails, sort_keys=True, indent=0).encode('utf-8'))
		return hash.hexdigest()
	
	def _editorPathSuffix(self, cmdVersion):
		"""
		Returns the suffix for the path to the UE4Editor binary
		"""
		pass
	
	def _runDotNetApplication(self, exeFile, args = []):
		"""
		Runs a .NET application and captures the output
		"""
		pass
	
	def _buildDotNetProject(self, projectFile):
		"""
		Builds a .NET project and captures the output
		"""
		pass
	
	def _defaultThirdpartyLibs(self):
		"""
		Returns the list of default third-party libraries to build against under the current platform
		"""
		return []
	
	def _getLibraryOverrides(self):
		"""
		Returns the dictionary of third-party library detail overrides
		"""
		return {}
	
	def _transformBuildToolPlatform(self, platform):
		"""
		Derived classes can override this method to transform platform strings when running UBT
		"""
		return platform
	
	def _runUnrealBuildTool(self, target, platform, configuration, args, capture=False):
		"""
		Invokes UnrealBuildTool with the specified parameters
		"""
		platform = self._transformBuildToolPlatform(platform)
		arguments = [self.getBuildScript(), target, platform, configuration] + args
		if capture == True:
			return Utility.capture(arguments, cwd=self.getEngineRoot(), raiseOnError=True)
		else:
			Utility.run(arguments, cwd=self.getEngineRoot(), raiseOnError=True)
	
	def _getUE4BuildInterrogator(self):
		"""
		Uses UE4BuildInterrogator to interrogate UnrealBuildTool about third-party library details
		"""
		ubtLambda = lambda target, platform, config, args: self._runUnrealBuildTool(target, platform, config, args, True)
		interrogator = UE4BuildInterrogator(self.getEngineRoot(), self._getEngineVersionDetails(), self._getEngineVersionHash(), ubtLambda)
		return interrogator
