'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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
'''

import textwrap, changetypes, re


# Change (bugs fixed, features added, etc.) converters:

class ChangeConverter(object):
    def convert(self, change):
        result = self.preProcess(change.description)
        if hasattr(change, 'url'):
            result += ' (%s)'%self.convertURL(change.url)
        if change.changeIds:
            convertedIds = self.convertChangeIds(change)
            result += ' (%s)'%', '.join(convertedIds)
        return self.postProcess(result)
    
    def preProcess(self, changeToBeConverted):
        return changeToBeConverted

    def postProcess(self, convertedChange):
        return convertedChange

    def convertChangeIds(self, change):
        return [self.convertChangeId(change, id) for id in change.changeIds]

    def convertChangeId(self, change, changeId):
        return changeId

    def convertURL(self, url):
        return url
    

class ChangeToTextConverter(ChangeConverter):
    def __init__(self):
        self._textWrapper = textwrap.TextWrapper(initial_indent='- ', 
                subsequent_indent='  ', width=78)
        # Regular expression to remove multiple spaces, except when on
        # the start of a line:
        self._multipleSpaces = re.compile(r'(?<!^) +', re.M)

    def postProcess(self, convertedChange):
        convertedChange = self._textWrapper.fill(convertedChange)
        # Somehow the text wrapper introduces multiple spaces within
        # lines, this is a work around:
        convertedChange = self._multipleSpaces.sub(' ', convertedChange)
        return convertedChange

    def convertChangeId(self, change, changeId):
        return changeId if changeId.startswith('http') else 'SF#%s'%changeId
        

class ChangeToHTMLConverter(ChangeConverter):

    LinkToSourceForge = '<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=%%(id)s&group_id=130831&atid=%(atid)s">%%(id)s</A>'
    LinkToSourceForgeBugReport = LinkToSourceForge%{'atid': '719134'}
    LinkToSourceForgeFeatureRequest = LinkToSourceForge%{'atid': '719137'}
    LinkToURL = '<A HREF="%(id)s">%(id)s</A>'
    NoLink = '%(id)s'

    def preProcess(self, changeToBeConverted):
        changeToBeConverted = re.sub('<', '&lt;', changeToBeConverted)
        changeToBeConverted = re.sub('>', '&gt;', changeToBeConverted)
        return changeToBeConverted
    
    def postProcess(self, convertedChange):
        listOfUrlAndTextFragments = re.split('(http://[^\s()]+[^\s().])', convertedChange)
        listOfConvertedUrlsAndTextFragments = []
        for fragment in listOfUrlAndTextFragments:
            if fragment.startswith('http://'):
                fragment = self.convertURL(fragment)
            listOfConvertedUrlsAndTextFragments.append(fragment)
        convertedChange = ''.join(listOfConvertedUrlsAndTextFragments)
        return '<LI>%s</LI>'%convertedChange

    def convertChangeId(self, change, changeId):
        if changeId.startswith('http'):
            template = self.LinkToURL
        elif isinstance(change, changetypes.Bug):
            template = self.LinkToSourceForgeBugReport    
        elif isinstance(change, changetypes.Feature):
            template = self.LinkToSourceForgeFeatureRequest
        else:
            template = self.NoLink
        return template%{'id': changeId}

    def convertURL(self, url):
        return '<A HREF="%s">%s</A>'%(url, url)


# Release converters:

class ReleaseConverter(object):
    def __init__(self):
        self._changeConverter = self.ChangeConverterClass()

    def _addS(self, listToCount):
        multiple = len(listToCount) > 1
        return dict(s='s' if multiple else '',
                    y='ies' if multiple else 'y')

    def convert(self, release, greeting=''):
        result = [self.summary(release, greeting)]
        if not greeting:
            result.insert(0, self.header(release))
        for section, list in [('Bug%(s)s fixed', release.bugsFixed),
                ('Feature%(s)s added', release.featuresAdded),
                ('Feature%(s)s changed', release.featuresChanged),
                ('Feature%(s)s removed', release.featuresRemoved),
                ('Implementation%(s)s changed', release.implementationChanged),
                ('Dependenc%(y)s changed', release.dependenciesChanged),
                ('Distribution%(s)s changed', release.distributionsChanged),
                ('Website change%(s)s', release.websiteChanges)]:
            if list:
                result.append(self.sectionHeader(section, list))
                for change in list:
                    result.append(self._changeConverter.convert(change))
                result.append(self.sectionFooter(section, list))
        result = [line for line in result if line]
        return '\n'.join(result)+'\n\n'

    def header(self, release):
        return 'Release %s - %s'%(release.number, release.date)

    def summary(self, release, greeting=''):
        return ' '.join([text for text in greeting, release.summary if text])
    
    def sectionHeader(self, section, list):
        return '\n%s:'%(section%self._addS(list))
        
    def sectionFooter(self, section, list):
        return ''


class ReleaseToTextConverter(ReleaseConverter):
    ChangeConverterClass = ChangeToTextConverter

    def summary(self, *args, **kwargs):
        summary = super(ReleaseToTextConverter, self).summary(*args, **kwargs)
        wrapper = textwrap.TextWrapper(initial_indent='', 
            subsequent_indent='', width=78)
        multipleSpaces = re.compile(r'(?<!^) +', re.M)
        summary = wrapper.fill(summary)
        # Somehow the text wrapper introduces multiple spaces within
        # lines, this is a work around:
        summary = multipleSpaces.sub(' ', summary)
        return summary


class ReleaseToHTMLConverter(ReleaseConverter):
    ChangeConverterClass = ChangeToHTMLConverter

    def header(self, release):
        return '<H4>%s</H4>'%super(ReleaseToHTMLConverter, self).header(release)

    def sectionHeader(self, section, list):
        return super(ReleaseToHTMLConverter, self).sectionHeader(section, 
            list) + '\n<UL>'

    def sectionFooter(self, section, list):
        return '</UL>'

    def summary(self, release, greeting=''):
        summaryText = super(ReleaseToHTMLConverter, self).summary(release)
        if summaryText:
            return '<P>%s</P>'%summaryText
        else:
            return ''