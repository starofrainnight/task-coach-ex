Task Coach Portable Launcher
============================
Copyright 2004-2009 John T. Haller
Copyright 2007-2009 Patrick Patience

Website: http://PortableApps.com/TaskCoachPortable

This software is OSI Certified Open Source Software.
OSI Certified is a certification mark of the Open Source Initiative.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

ABOUT TASK COACH PORTABLE
=========================
The Task Coach Portable Launcher allows you to run Task Coach from a removable drive whose
letter changes as you move it to another computer.  The application can be entirely self-
contained on the drive and then used on any Windows computer.


LICENSE
=======
This code is released under the GPL.  The full code is included with this package as
TaskCoachPortable.nsi.


INSTALLATION / DIRECTORY STRUCTURE
==================================
By default, the program expects one of these directory structures:

-\ <--- Directory with TaskCoachPortable.exe
	+\App\
		+\TaskCoach\
	+\Data\
		+\settings\


It can be used in other directory configurations by including the TaskCoachPortable.ini
file in the same directory as TaskCoachPortable.exe and configuring it as details in the
INI file section below.


TASKCOACHPORTABLE.INI CONFIGURATION
===================================
The TaskCoach Portable Launcher will look for an ini file called TaskCoachPortable.ini
within its directory (see the Installation/Directory Structure section above for more
details).  If you are happy with the default options, it is not necessary, though.  The
INI file is formatted as follows:

[TaskCoachPortable]
TaskCoachDirectory=App\TaskCoach
SettingsDirectory=Data\settings
TaskCoachExecutable=taskcoach.exe
AdditionalParameters=
DisableSplashScree=false

The TaskCoachDirectory and SettingsDirectory entries should be set to the *relative* path
to the directory containing TaskCoach.exe and the settings files.  They must be a
subdirectory (or multiple subdirectories) of the directory containing
TaskCoachPortable.exe.  The default entries for these are described in the installation
section above.

The TaskCoachExecutable entry allows you to set the TaskCoach Portable Launcher to use an
alternate EXE call to launch TaskCoach.  This is helpful if you are using a machine that
is set to deny TaskCoach.exe from running or to launch the writer, calc, etc directly.
You'll need to rename the TaskCoach.exe file and then enter the name you gave it on the
TaskCoachExecutable= line of the INI.

The AdditionalParameters entry allows you to pass additional commandline parameter
entries to TaskCoach.exe.  Whatever you enter here will be appended to the call to
TaskCoach.exe.

DisableSplashScreen allows you to disable the splash screen when set to true.


PROGRAM HISTORY / ABOUT THE AUTHOR
==================================
This launcher grew from the work of John T. Haller on his Firefox Portable and Thunderbird 
Portable Launchers.  Some of the ideas arose from discussions relating to Firefox Portable &
Thunderbird Portable in the mozillaZine forums.