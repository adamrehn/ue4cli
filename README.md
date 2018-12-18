Command-line interface for Unreal Engine 4
==========================================

The ue4cli Python package implements a command-line tool called `ue4` that provides a simplified interface to various functionality of the build system for Epic Games' [Unreal Engine 4](https://www.unrealengine.com/). The primary goals of this tool are as follows:

- Abstract away the platform-specific details of the various batch files and shell scripts scattered throughout the Engine's source tree.
- Provide the ability to easily generate IDE project files under Linux, where no shell integration currently exists to perform this task from outside the Editor.
- Determine the compiler flags required to build third-party libraries for use within Engine modules. This is particularly important under macOS and Linux where [symbol interposition](https://developer.apple.com/library/content/documentation/DeveloperTools/Conceptual/DynamicLibraries/100-Articles/DynamicLibraryUsageGuidelines.html#//apple_ref/doc/uid/TP40001928-SW9) can cause clashes between external libraries and those bundled in the `ThirdParty` directory of the Engine source tree, and under Linux where libraries need to build against the Engine's bundled version of libc++.

This package requires **Unreal Engine 4.19 or newer** (since 4.19 is the first release to include the necessary patches to UnrealBuildTool.) The package also requires Python 3.5 or newer.

**Check out the [comprehensive documentation](https://adamrehn.com/docs/ue4cli/) to view installation instructions and the full command reference.**

Resources:

- **Documentation:** <https://adamrehn.com/docs/ue4cli/>
- **GitHub repository:** <https://github.com/adamrehn/ue4cli>
- **Package on PyPI:** <https://pypi.org/project/ue4cli/>
- **Related articles:** <https://adamrehn.com/articles/tag/Unreal%20Engine/>

## Legal

Copyright &copy; 2017-2018, Adam Rehn. Licensed under the MIT License, see the file [LICENSE](https://github.com/adamrehn/ue4cli/blob/master/LICENSE) for details.
