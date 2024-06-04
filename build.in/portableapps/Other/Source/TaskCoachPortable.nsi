;Copyright (C) 2004-2009 John T. Haller
;Copyright (C) 2007-2009 Patrick Patience

;Website: http://PortableApps.com/TaskCoachPortable

;This software is OSI Certified Open Source Software.
;OSI Certified is a certification mark of the Open Source Initiative.

;This program is free software; you can redistribute it and/or
;modify it under the terms of the GNU General Public License
;as published by the Free Software Foundation; either version 2
;of the License, or (at your option) any later version.

;This program is distributed in the hope that it will be useful,
;but WITHOUT ANY WARRANTY; without even the implied warranty of
;MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;GNU General Public License for more details.

;You should have received a copy of the GNU General Public License
;along with this program; if not, write to the Free Software
;Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

!define PORTABLEAPPNAME "Task Coach Portable"
!define APPNAME "Task Coach"
!define NAME "TaskCoachPortable"
!define VER "1.6.2.0"
!define WEBSITE "PortableApps.com/TaskCoachPortable"
!define DEFAULTEXE "taskcoach.exe"
!define DEFAULTAPPDIR "TaskCoach"
!define DEFAULTSETTINGSDIR "settings"
!define LAUNCHERLANGUAGE "English"

;=== Program Details
Name "${PORTABLEAPPNAME}"
OutFile "..\..\${NAME}.exe"
Caption "${PORTABLEAPPNAME} | PortableApps.com"
VIProductVersion "${VER}"
VIAddVersionKey ProductName "${PORTABLEAPPNAME}"
VIAddVersionKey Comments "Allows ${APPNAME} to be run from a removable drive.  For additional details, visit ${WEBSITE}"
VIAddVersionKey CompanyName "PortableApps.com"
VIAddVersionKey LegalCopyright "PortableApps.com & Contributors"
VIAddVersionKey FileDescription "${PORTABLEAPPNAME}"
VIAddVersionKey FileVersion "${VER}"
VIAddVersionKey ProductVersion "${VER}"
VIAddVersionKey InternalName "${PORTABLEAPPNAME}"
VIAddVersionKey LegalTrademarks "PortableApps.com is a Trademark of Rare Ideas, LLC."
VIAddVersionKey OriginalFilename "${NAME}.exe"
;VIAddVersionKey PrivateBuild ""
;VIAddVersionKey SpecialBuild ""

;=== Runtime Switches
CRCCheck On
WindowIcon Off
SilentInstall Silent
AutoCloseWindow True
RequestExecutionLevel user
XPStyle On

; Best Compression
SetCompress Auto
SetCompressor /SOLID lzma
SetCompressorDictSize 32
SetDatablockOptimize On

;=== Include
;(Standard NSIS)
!include Registry.nsh
!include FileFunc.nsh
!insertmacro GetParameters
!insertmacro GetRoot

;(NSIS Plugins)
!include TextReplace.nsh

;(Custom)
!include ReadINIStrWithDefault.nsh
!include ReplaceInFileWithTextReplace.nsh

;=== Program Icon
Icon "..\..\App\AppInfo\appicon.ico"

;=== Icon & Stye ===
!define MUI_ICON "..\..\App\AppInfo\appicon.ico"

;=== Languages
;!insertmacro MUI_LANGUAGE "${LAUNCHERLANGUAGE}"
LoadLanguageFile "${NSISDIR}\Contrib\Language files\${LAUNCHERLANGUAGE}.nlf"
!include PortableApps.comLauncherLANG_${LAUNCHERLANGUAGE}.nsh

Var PROGRAMDIRECTORY
Var SETTINGSDIRECTORY
Var ADDITIONALPARAMETERS
Var EXECSTRING
Var PROGRAMEXECUTABLE
Var DISABLESPLASHSCREEN
Var SECONDARYLAUNCH
Var DEFAULTLOCATION
Var MISSINGFILEORPATH
Var LASTDRIVE
Var CURRENTDRIVE
Var APPLANGUAGE
Var DOCUMENTSDIR

Section "Main"
	;=== Check if already running
	System::Call 'kernel32::CreateMutexA(i 0, i 0, t "${NAME}") i .r1 ?e'
	Pop $0
	StrCmp $0 0 CheckRunning
		StrCpy $SECONDARYLAUNCH "true"
		Goto CheckINI

	CheckRunning:
		FindProcDLL::FindProc "taskcoach.exe"
		StrCmp $R0 "1" "" CheckINI
			MessageBox MB_OK|MB_ICONINFORMATION `$(LauncherAlreadyRunning)`
			Abort
		
	CheckINI:
		;=== Find the INI file, if there is one
		IfFileExists "$EXEDIR\${NAME}.ini" "" NoINI

			;=== Read the parameters from the INI file
			${ReadINIStrWithDefault} $0 "$EXEDIR\${NAME}.ini" "${NAME}" "${APPNAME}Directory" "App\${DEFAULTAPPDIR}"
			StrCpy $PROGRAMDIRECTORY "$EXEDIR\$0"
			${ReadINIStrWithDefault} $0 "$EXEDIR\${NAME}.ini" "${NAME}" "SettingsDirectory" "Data\${DEFAULTSETTINGSDIR}"
			StrCpy $SETTINGSDIRECTORY "$EXEDIR\$0"
			${ReadINIStrWithDefault} $ADDITIONALPARAMETERS "$EXEDIR\${NAME}.ini" "${NAME}" "AdditionalParameters" ""
			${ReadINIStrWithDefault} $PROGRAMEXECUTABLE "$EXEDIR\${NAME}.ini" "${NAME}" "${APPNAME}Executable" "${DEFAULTEXE}"
			${ReadINIStrWithDefault} $DISABLESPLASHSCREEN "$EXEDIR\${NAME}.ini" "${NAME}" "DisableSplashScreen" "false"
			
			StrCmp $PROGRAMDIRECTORY "$EXEDIR\App\${DEFAULTAPPDIR}" "" CheckForFile
			StrCmp $SETTINGSDIRECTORY "$EXEDIR\Data\${DEFAULTSETTINGSDIR}" "" CheckForFile
				StrCpy $DEFAULTLOCATION "true"

		CheckForFile:
			IfFileExists "$PROGRAMDIRECTORY\$PROGRAMEXECUTABLE" FoundProgramEXE NoProgramEXE

	NoINI:
		;=== No INI file, so we'll use the defaults
		StrCpy $ADDITIONALPARAMETERS ""
		StrCpy $PROGRAMEXECUTABLE "${DEFAULTEXE}"
		StrCpy $DISABLESPLASHSCREEN "false"
		StrCpy $DEFAULTLOCATION "true"

		IfFileExists "$EXEDIR\App\${DEFAULTAPPDIR}\${DEFAULTEXE}" "" NoProgramExe
			StrCpy $PROGRAMDIRECTORY "$EXEDIR\App\${DEFAULTAPPDIR}"
			StrCpy $SETTINGSDIRECTORY "$EXEDIR\Data\${DEFAULTSETTINGSDIR}"
			GoTo FoundProgramEXE

	NoProgramEXE:
		;=== Program executable not where expected
		StrCpy $MISSINGFILEORPATH ${DEFAULTEXE}
		MessageBox MB_OK|MB_ICONEXCLAMATION `$(LauncherFileNotFound)`
		Abort
		
	FoundProgramEXE:
		StrCmp $SECONDARYLAUNCH "true" GetPassedParameters
		StrCmp $DISABLESPLASHSCREEN "true" SkipSplashScreen
			;=== Show the splash screen before processing the files
			InitPluginsDir
			File /oname=$PLUGINSDIR\splash.jpg "${NAME}.jpg"
			newadvsplash::show /NOUNLOAD 1200 0 0 -1 /L "$PLUGINSDIR\splash.jpg"

	SkipSplashScreen:		
		;=== Copy the default settings files
		StrCmp $DEFAULTLOCATION "true" "" UpdateLocations ;=== if not default location, user is on their own
		IfFileExists "$SETTINGSDIRECTORY\TaskCoach.ini" UpdateLocations
		CreateDirectory "$SETTINGSDIRECTORY"
		CopyFiles /SILENT "$EXEDIR\App\DefaultData\settings\*.*" "$SETTINGSDIRECTORY\"
		GoTo UpdateLocations

	UpdateLocations:
		;=== Update files for new location
		ReadINIStr $LASTDRIVE "$SETTINGSDIRECTORY\${NAME}Settings.ini" "${NAME}Settings" "LastDriveLetter"
		${GetRoot} $EXEDIR $CURRENTDRIVE
		StrCmp $LASTDRIVE $CURRENTDRIVE GetAppLanguage
		IfFileExists "$SETTINGSDIRECTORY\TaskCoach.ini" "" StoreCurrentDriveLetter
			${ReplaceInFile} `$SETTINGSDIRECTORY\TaskCoach.ini` `$LASTDRIVE\` `$CURRENTDRIVE\`
			Delete "$SETTINGSDIRECTORY\TaskCoach.ini.old"

	GetAppLanguage:
		ReadEnvStr $APPLANGUAGE "PortableApps.comLocaleglibc"
		StrCmp $APPLANGUAGE "" StoreCurrentDriveLetter ;if not set, move on
		StrCmp $APPLANGUAGE "en_US" "" GetCurrentLanguage

	GetCurrentLanguage:
		StrCmp $APPLANGUAGE "en_US" SetAppLanguage ;english is built in, so skip locale file check
		StrCmp $APPLANGUAGE "bg_BG" "" +3
			StrCpy $APPLANGUAGE "bg_BG"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "br" "" +3
			StrCpy $APPLANGUAGE "br_FR"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "cs" "" +3
			StrCpy $APPLANGUAGE "cs_CS"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "da" "" +3
			StrCpy $APPLANGUAGE "da_DA"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "de" "" +3
			StrCpy $APPLANGUAGE "de_DE"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "en_GB" "" +2
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "es" "" +3
			StrCpy $APPLANGUAGE "es_ES"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "fr" "" +3
			StrCpy $APPLANGUAGE "fr_FR"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "gl" "" +3
			StrCpy $APPLANGUAGE "gl_ES"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "he" "" +3
			StrCpy $APPLANGUAGE "he_IL"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "hu" "" +3
			StrCpy $APPLANGUAGE "hu_HU"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "it" "" +3
			StrCpy $APPLANGUAGE "it_IT"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "ja" "" +3
			StrCpy $APPLANGUAGE "ja_JP"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "ko" "" +3
			StrCpy $APPLANGUAGE "ko_KO"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "lv" "" +3
			StrCpy $APPLANGUAGE "lv_LV"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "nn" "" +3
			StrCpy $APPLANGUAGE "nn_NO"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "nl" "" +3
			StrCpy $APPLANGUAGE "nl_NL"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "pl" "" +3
			StrCpy $APPLANGUAGE "pl_PL"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "pt_BR" "" +2
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "pt" "" +3
			StrCpy $APPLANGUAGE "pt_PT"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "ro" "" +3
			StrCpy $APPLANGUAGE "ro_RO"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "ru" "" +3
			StrCpy $APPLANGUAGE "ru_RU"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "sk" "" +3
			StrCpy $APPLANGUAGE "sk_SK"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "sv" "" +3
			StrCpy $APPLANGUAGE "sv_SE"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "tr" "" +3
			StrCpy $APPLANGUAGE "tr_TR"
			Goto SetAppLanguage
		StrCmp $APPLANGUAGE "zh_CN" SetAppLanguage
		StrCmp $APPLANGUAGE "zh_TW" SetAppLanguage StoreCurrentDriveLetter
	
	SetAppLanguage:
		WriteINIStr "$SETTINGSDIRECTORY\TaskCoach.ini" "view" "language" "$APPLANGUAGE"

	StoreCurrentDriveLetter:
		WriteINIStr "$SETTINGSDIRECTORY\${NAME}Settings.ini" "${NAME}Settings" "LastDriveLetter" "$CURRENTDRIVE"
		Goto CheckDocumentsExists
		
	CheckDocumentsExists:
		ReadEnvStr $DOCUMENTSDIR "PortableApps.comDocuments"
		StrCmp $DOCUMENTSDIR "$CURRENTDRIVE\Documents" UpdateSaveDirectory
		IfFileExists "$CURRENTDRIVE\Documents" UpdateSaveDirectory GetPassedParameters

	UpdateSaveDirectory:
		SetOutPath "$CURRENTDRIVE\Documents"

	GetPassedParameters:
		;=== Get any passed parameters
		${GetParameters} $0
		StrCmp "'$0'" "''" "" LaunchProgramParameters

		;=== No parameters
		StrCpy $EXECSTRING `"$PROGRAMDIRECTORY\$PROGRAMEXECUTABLE" --ini "$SETTINGSDIRECTORY\TaskCoach.ini"`
		Goto AdditionalParameters

	LaunchProgramParameters:
		StrCpy $EXECSTRING `"$PROGRAMDIRECTORY\$PROGRAMEXECUTABLE" --ini "$SETTINGSDIRECTORY\TaskCoach.ini" $0`

	AdditionalParameters:
		StrCmp $ADDITIONALPARAMETERS "" RegistryTweak

		;=== Additional Parameters
		StrCpy $EXECSTRING `$EXECSTRING $ADDITIONALPARAMETERS`
		
	RegistryTweak:
		${registry::KeyExists} "HKEY_CURRENT_USER\Software\wxaddons" $R0
		StrCmp $R0 "-1" LaunchNow
		${registry::MoveKey} "HKEY_CURRENT_USER\Software\wxaddons" "HKEY_CURRENT_USER\Software\wxaddons-BackupByTaskCoachPortable" $R0
		Sleep 100

	LaunchNow:
		StrCmp $SECONDARYLAUNCH "true" LaunchAndExit
		ExecWait $EXECSTRING

	;SetOriginalKeyBack:
		${registry::DeleteKey} "HKEY_CURRENT_USER\Software\wxaddons" $R0
		Sleep 100
		${registry::KeyExists} "HKEY_CURRENT_USER\Software\wxaddons-BackupByTaskCoachPortable" $R0
		StrCmp $R0 "-1" TheEnd
		${registry::MoveKey} "HKEY_CURRENT_USER\Software\wxaddons-BackupByTaskCoachPortable" "HKEY_CURRENT_USER\Software\wxaddons" $R0
		Sleep 100
		Goto TheEnd
	
	LaunchAndExit:
		Exec $EXECSTRING

	TheEnd:
		${registry::Unload}
		newadvsplash::stop /WAIT
SectionEnd