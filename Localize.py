#!/usr/bin/env python

import os
import sys
import gettext
import re
from operator import itemgetter

from Debug import *  # dprint()



g_Translations = {}

def getTranslation(language):
    global g_Translations
    if language not in g_Translations:
        filename = os.path.join(sys.path[0], 'assets', 'locales', language, 'plexconnect.mo')
        try:
            fp = open(filename, 'rb')
            g_Translations[language] = gettext.GNUTranslations(fp)
            fp.close()
        except IOError:
            g_Translations[language] = gettext.NullTranslations()
    return g_Translations[language]



def pickLanguage(languages):
    language = 'en'
    language_aliases = {
        'zh_TW': 'zh_Hant',
        'zh_CN': 'zh_Hans'
    }
    
    languages = re.findall('(\w{2}(?:[-_]\w{2,})?)(?:;q=(\d+(?:\.\d+)?))?', languages)
    languages = [(lang.replace('-', '_'), float(quot) if quot else 1.) for (lang, quot) in languages]
    languages = [(language_aliases.get(lang, lang), quot) for (lang, quot) in languages]
    languages = sorted(languages, key=itemgetter(1), reverse=True)
    for lang, quot in languages:
        if os.path.exists(os.path.join(sys.path[0], 'assets', 'locales', lang, 'plexconnect.mo')):
                language = lang
                break
    dprint(__name__, 1, "aTVLanguage: "+language)
    return(language)



def replaceTEXT(textcontent, language):
    translation = getTranslation(language)
    for msgid in set(re.findall(r'\{\{TEXT\((.+?)\)\}\}', textcontent)):
        msgstr = translation.ugettext(msgid).replace('\"', '\\\"')
        textcontent = textcontent.replace('{{TEXT(%s)}}' % msgid, msgstr)
    return textcontent



if __name__=="__main__":
    languages = "de;q=0.9, en;q=0.8"
    language = pickLanguage(languages)
    
    Text = "Hello World"  # doesn't translate
    print getTranslation(language).ugettext(Text)
    
    Text = "Library"  # translates
    print getTranslation(language).ugettext(Text)
    
    Text = "{{TEXT(Channels)}}"  # translates
    print replaceTEXT(Text, language).encode('ascii', 'replace')
