"""
Task Coach - Your friendly task manager
Copyright (C) 2004-2016 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import wx, os, sys, imp, tempfile, locale, gettext
from taskcoachlib import patterns, operating_system
from . import po2dict


class Translator(metaclass=patterns.Singleton):
    def __init__(self, language):
        load = (
            self._loadPoFile if language.endswith(".po") else self._loadModule
        )
        module, language = load(language)
        self._installModule(module)
        self._setLocale(language)

    def _loadPoFile(self, poFilename):
        """Load the translation from a .po file by creating a python
        module with po2dict and them importing that module."""
        language = self._languageFromPoFilename(poFilename)
        pyFilename = self._tmpPyFilename()
        po2dict.make(poFilename, pyFilename)
        module = imp.load_source(language, pyFilename)
        os.remove(pyFilename)
        return module, language

    def _tmpPyFilename(self):
        """Return a filename of a (closed) temporary .py file."""
        tmpFile = tempfile.NamedTemporaryFile(suffix=".py")
        pyFilename = tmpFile.name
        tmpFile.close()
        return pyFilename

    def _loadModule(self, language):
        """Load the translation from a python module that has been
        created from a .po file with po2dict before."""
        for moduleName in self._localeStrings(language):
            try:
                module = __import__(moduleName, globals())
                break
            except ImportError:
                module = None
        return module, language

    def _installModule(self, module):
        """Make the module's translation dictionary and encoding available."""
        # pylint: disable=W0201
        if module:
            self.__language = module.dict
            self.__encoding = module.encoding

    def _setLocale(self, language):
        """Try to set the locale, trying possibly multiple localeStrings."""
        if not operating_system.isGTK():
            locale.setlocale(locale.LC_ALL, "")
        # Set the wxPython locale:
        for localeString in self._localeStrings(language):
            languageInfo = wx.Locale.FindLanguageInfo(localeString)
            if languageInfo:
                self.__locale = wx.Locale(
                    languageInfo.Language
                )  # pylint: disable=W0201
                # Add the wxWidgets message catalog. This is really only for
                # py2exe'ified versions, but it doesn't seem to hurt on other
                # platforms...
                localeDir = os.path.join(
                    wx.StandardPaths_Get().GetResourcesDir(), "locale"
                )
                self.__locale.AddCatalogLookupPathPrefix(localeDir)
                self.__locale.AddCatalog("wxstd")
                break
        if operating_system.isGTK():
            try:
                locale.setlocale(locale.LC_ALL, "")
            except locale.Error:
                # Mmmh. wx will display a message box later, so don't do anything.
                pass
        self._fixBrokenLocales()

    def _fixBrokenLocales(self):
        current_language = locale.getlocale(locale.LC_TIME)[0]
        if current_language and "_NO" in current_language:
            # nb_BO and ny_NO cause crashes in the wx.DatePicker. Set the
            # time part of the locale to some other locale. Since we don't
            # know which ones are available we try a few. First we try the
            # default locale of the user (''). It's probably *_NO, but it
            # might be some other language so we try just in case. Then we try
            # English (GB) so the user at least gets a European date and time
            # format if that works. If all else fails we use the default
            # 'C' locale.
            for lang in ["", "en_GB.utf8", "C"]:
                try:
                    locale.setlocale(locale.LC_TIME, lang)
                except locale.Error:
                    continue
                current_language = locale.getlocale(locale.LC_TIME)[0]
                if current_language and "_NO" in current_language:
                    continue
                else:
                    break

    def _localeStrings(self, language):
        """Extract language and language_country from language if possible."""
        localeStrings = []
        if language:
            localeStrings.append(language)
            if "_" in language:
                localeStrings.append(language.split("_")[0])
        return localeStrings

    def _languageFromPoFilename(self, poFilename):
        return os.path.splitext(os.path.basename(poFilename))[0]

    def translate(self, string):
        """Look up string in the current language dictionary. Return the
        passed string if no language dictionary is available or if the
        dictionary doesn't contain the string."""
        try:
            return self.__language[string].decode(self.__encoding)
        except (AttributeError, KeyError):
            return string


def currentLanguageIsRightToLeft():
    return wx.GetApp().GetLayoutDirection() == wx.Layout_RightToLeft


def translate(string):
    return Translator().translate(string)


_ = translate  # This prevents a warning from pygettext.py

# Inject into builtins for 3rdparty packages
import builtins

builtins.__dict__["_"] = _
