README.txt
-----------

This is README-file for applications(='utilities') in "utils" folder of project.
It contains description of utilities, and usage thereof.

Subversion changeset-to-headerfile utility: 'svn_rev_update.exe'
----------------------------------------------------------------
Description: 
this utility takes a path to a SVN-repository local copy 
(e.g. *not* URL to remote or local repository), 
as a required argument, and writes out a sample 
C/C++ header file (default = "svn_changeset.h") - 
optionally to a file given as second argument.

Synopsis/Usage: 
<<
svn_rev_update ver.1.0.3

usage: svn_rev_update.exe [-h] [--time] [--ignore IGNORE_FILES_LIST]
                          [--skip SKIP_PATHS_LIST] [--out OUT_FILE]
                          [--prefix PREFIX_ARG]
                          path
svn_rev_update.exe: error: the following arguments are required: path
>>

Basic command-line usage:
'svn_rev_update.exe -o [optional: full pathname for .h-file] <path-to-local-copy-of-SVN-repo> '

NOTE: current version is 1.0.2


Integration:
------------
Run the utility as part of a pre-build step in Eclipse(CDT)-variant, 
like KinetisDevelopmentStudio("KDS") or McuXpresso from NXP(Freescale).
All EclipseCDT-based IDEs have the same basic build-setup procedure, 
but the naming and usage of built-in (environment-)variables vary.


Simple usage:
-------------
Example pre-build step definition (if using McuXpresso IDE):
<<
	${PROJECT_ROOT}\utils\svn_rev_update.exe  ${PROJECT_ROOT}
>>

Example pre-build step definition (if using KinetisDesignStudio IDE, or 'KDS'):
<<
	${PROJECT_LOC}\utils\svn_rev_update.exe  ${PROJECT_LOC}
>>
NOTE: use 
<<
	${PROJECT_LOC}\utils\svn_rev_update.exe  ${PROJECT_LOC}
>>
if the PROJECT_LOC environment variable fails to expand to anything (valid)!

Running the post-build step will emit something like the following output:
<<
Generating 'svn_changeset.h' header file ...
../utils/svn_rev_update.exe  ..
Scanning path: ..
Got SVN revision = 998
Warning: working copy DIRTY!

Status in header file definition SVN_STATUS set to 'dirty'
Modified files and/or directories:
==========================================================================================
..\.cproject
..\IrrigationSensorAppl Debug.launch
..\Sources\product.h
..\utils\UTILS_README.txt
==========================================================================================

Note: there are unversioned files and/or directories:
==========================================================================================
..\.settings\language.settings.xml.mine
..\.settings\language.settings.xml.r867
..\.settings\language.settings.xml.r985
..\RELEASE_FW1\Generated_Code
..\RELEASE_FW1\IrrigationSensorAppl_FW1.elf
..\RELEASE_FW1\IrrigationSensorAppl_FW1.map
..\RELEASE_FW1\IrrigationSensorAppl_FW1.srec.mine
..\RELEASE_FW1\IrrigationSensorAppl_FW1.srec.r867
..\RELEASE_FW1\IrrigationSensorAppl_FW1.srec.r985
..\RELEASE_FW1\SDK
..\RELEASE_FW1\Sources
..\RELEASE_FW1\Static_Code
..\RELEASE_FW1\makefile
..\RELEASE_FW1\objects.mk
..\RELEASE_FW1\sources.mk
..\RELEASE_FW2\Generated_Code
..\RELEASE_FW2\IrrigationSensorAppl_FW2.elf
..\RELEASE_FW2\IrrigationSensorAppl_FW2.map
..\RELEASE_FW2\IrrigationSensorAppl_FW2.srec.mine
..\RELEASE_FW2\IrrigationSensorAppl_FW2.srec.r867
..\RELEASE_FW2\IrrigationSensorAppl_FW2.srec.r985
..\RELEASE_FW2\SDK
..\RELEASE_FW2\Sources
..\RELEASE_FW2\Static_Code
..\RELEASE_FW2\makefile
..\RELEASE_FW2\objects.mk
..\RELEASE_FW2\sources.mk
..\Sources.zip
..\auth
..\config
..\servers
==========================================================================================
UUID for this build: 216141758657034270884983335115745460932
--> Updating SVN revision header file 'svn_changeset.h' ...
--> Finished updating SVN revision header file.
>>

NOTE: because of the "product.h" NEVER being in sync with the SVN repository version when building (PRODUCT_TYPE must be set), 
the 'dirty' status will ALWAYS be the case for the local copy! The build process, and/or the 'svn_rev_update.exe' utility 
will have to use the "-i"(ignore) and/or "-s"(skip) flag(s) to cope with this. See 'Advanced Usage' below for details!


Advanced Usage:
---------------
Typically, it will be desirable (or even necessary) to specify files to ignore during SVN-status check, 
and sometimes also entire folders to skip checking for 
(typically folders NOT containing any source code, but instead project-relevant files NOT referenced during build).


List files to ignore with the "-i" flag, as a comma-separated list, 
and optionally folders to skip with "-s" flag, as a comma-separated list, 
as the following example demonstrates:
<<
svn_rev_update.exe -i ReadMe.txt,product.h  -s docs,utils,firmware ..
>>
Which ignores files named "ReadMe.txt" and "product.h" - 
and skips folders below project-toplevel path starting with 'docs', 'utils' or 'firmware'.


Using the generated header file:
--------------------------------
The generated header file produced from running this step, 
will end up in the build-folder (typically named "Debug" or "Release")
unless otherwise is specified as 2nd argument to the utility.

The content of the header file is primarily symbol definition:
	SVN_CHANGESET_NUM --> unsigned integer, reflecting the latest update of (local) working copy from remote SVN repository 

In addition, the following symbols will de defined in auto-generated header file:
 	SVN_STATUS --> string, either "clean" (if working copy is synchronized with repository) or "dirty" (if local changes not checked in)
	LOCAL_IS_CLEAN --> bool, simply a complement to 'SVN_STATUS' to enable simple checks. FALSE if project is 'dirty', TRUE if 'clean'.
	IS_TOP_LEVEL_UPDATED --> bool, FALSE if project is NOT updated from project's top-level folder, may be used to ABORT build (as this may be critical).
 	BUILD_UUID --> unsigned integer, 128-bit Windows UUID per 'uuid4()' system call (random value) 
	DATE_STAMP --> current date as string
	TIME_STAMP --> current date as string, NOTE: only second-granularity!

This results in a header file (default name "svn_changeset.h") as shown in example below:
<<
/****** Generated by 'svn_rev_update' ver.1.0.2 ***********/

#define SVN_CHANGESET_NUM		334
#define SVN_STATUS				"clean"
#define LOCAL_IS_CLEAN			true
#define IS_TOP_LEVEL_UPDATED	true
#define BUILD_UUID				7663926157779610978663892114156450379
#define DATE_STAMP				"2019-04-05"
#define TIME_STAMP				"09:35:45"
>>

Symbol SVN_CHANGESET_NUM is supposed to be included in user code as follows:
<<
	#ifdef NDEBUG
	#include "Debug/svn_changeset.h"
	#else
	#include "Release/svn_changeset.h"
	#endif
>>
typically this code is placed in a "version.h" header file - 
containing nothing but definition of version(-string) for the application.

Example "version.h" content:
<<
	#ifdef NDEBUG
	#include "Debug/svn_changeset.h"
	#else
	#include "Release/svn_changeset.h"
	#endif
	#ifdef __cplusplus
	extern "C"
	{
	#endif
	
	/* Helpers */
	#define STRINGIFY(s)	str(s)
	#define str(s)			#s
	
	/* Version literal values */
	#define FW_VERSION_MAJOR	0
	#define FW_VERSION_MINOR	1	// First version
	#define FW_VERSION_SUBMINOR	0	// No fixes or cleanups yet ...
	//
	#define FW_VERSION_SVN		// auto-updated field
	
	/* Version string values */
	#ifdef SVN_CHANGESET_NUM
	#define SVN_REVISION_STRING     STRINGIFY(SVN_CHANGESET_NUM)
	#else
	#define SVN_REVISION_STRING     "none"
	#endif
	
	#define FW_VERSION	STRINGIFY(FW_VERSION_MAJOR)"."STRINGIFY(FW_VERSION_MINOR)"."STRINGIFY(FW_VERSION_SUBMINOR)"-"SVN_REVISION_STRING
	
	#define FW_STATUS	"Alpha"
	
	#ifdef __cplusplus
	}
	#endif
>>

User code including "version.h" can now refer directly to firmware-version string 'FW_VERSION', 
which will have the following format:
	"<major-num>.<minor-num>.<subminor-num>-<SVN revision-num>"
	
Example:
	"0.1.2-168"

This will enable developers and testers to track the firmware back to exactly 
the SVN changeset used to build this firmware. Note that the LOCAL copy is used 
to generate the changeset number definition, as this what is actually used for building firmware - 
NOT the repository database itself (as local copy may lag behind).

If added verbosity in version string is needed, the 2 extra definitions can be added as well.
Example:
<<
#define BUILD_ID_STRING     STRINGIFY(BUILD_UUID)
#define FW_VERSION	STRINGIFY(FW_VERSION_MAJOR)"."STRINGIFY(FW_VERSION_MINOR)"."STRINGIFY(FW_VERSION_SUBMINOR)"-"SVN_REVISION_STRING"-"BUILD_ID_STRING"-"SVN_STATUS
>>
(or similar)


NOTES: 
------
1) it is imperative to *NOT* place "svn_changeset.h" (or similar autogenerated SVN-info header file)
under version control! This would defy the file's intended purpose.  

2) use the other symbol definitions from generated SVN-info file at will, but also with care.
LOCAL_IS_CLEAN and IS_TOP_LEVEL_UPDATED are both 'bool' types (from <stdbool.h>), 
and should *ULTIMATELY* be used to qualify a build (or, at least emit a warning during build).

It could be relevant to extend the build-process to detect 
- if local/working copy is in sync w. repository (or, if it lags behind) --> autosync, or emit warning!
- if local/working copy has uncommited changes --> this should (possibly?) DENY build-attempts in RELEASE-configuration!

Example (using IFDEFs):
<<
#if defined(LOCAL_IS_CLEAN) and (LOCAL_IS_CLEAN==true)
#error "Local copy is NOT in sync - please update from top before build!"
#endif
>>
(place somewhere at top of "main.c" or similar)

3) Build-time/date is typically also available from the compiler tool (predefined symbols or macros).
Prefer using these, as most compilers today use the same naming 
(GCC-defs/macros is typically what the other tools refer to).


TODO:
-----
No idea (yet) ...

The application is written in Python language, using the 'pysvn' module.
Source file is commited along with executable for reference.
All SVN operations are implemented in this module, making it possible to 
do anything from Python code that SVN client application ('svn' command) can do.


