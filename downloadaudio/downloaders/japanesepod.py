# -*- mode: python; coding: utf-8 -*-
#
# Copyright © 2012 Roland Sieker, ospalh@gmail.com
# Inspiration and source of the URL: Tymon Warecki
#
# License: GNU AGPL, version 3 or later;
# http://www.gnu.org/copyleft/agpl.html


'''
Download Japanese pronunciations from Japanesepod
'''

import urllib

from .downloader import AudioDownloader


class JapanesepodDownloader(AudioDownloader):
    """Download audio from Japanesepod"""
    def __init__(self):
        AudioDownloader.__init__(self)
        self.file_extension = u'.mp3'
        self.icon_url = 'http://www.japanesepod101.com/'
        self.url = 'http://assets.languagepod101.com/' \
            'dictionary/japanese/audiomp3.php?'

    def download_files(self, word, base, ruby):
        """
        Downloader functon.

        Get text for the base and ruby (kanji and kana) when
        self.language is ja.
        """
        self.maybe_get_icon()
        self.downloads_list = []
        self.set_names(word, base, ruby)
        # We return (without adding files to the list) at the slightes
        # provocation: wrong language, no kanji, problems with the
        # download, ...
        if not self.language.startswith('ja'):
            return
        if not base:
            return
        # Only get the icon when we are using Japanese.
        self.maybe_get_icon()
        # Reason why we don't just do the get_data_.. bit inside the
        # with: Like this we don't have to clean up the temp file.
        word_data = self.get_data_from_url(self.query_url(base, ruby))
        word_file_path, word_file_name = self.get_file_name()
        with open(word_file_path, 'wb') as word_file:
            word_file.write(word_data)
        # We have a file, but not much to say about it.
        self.downloads_list.append(
            (word_file_path, word_file_name, dict(Source='JapanesePod')))

    def query_url(self, kanji, kana):
        qdict = {}
        qdict['kanji'] = kanji.encode('utf-8')
        if kana:
            qdict['kana'] = kana.encode('utf-8')
        return self.url + urllib.urlencode(qdict)

    def set_names(self, text, base, ruby):
        """
        Set the display text and file base name variables.
        """
        self.base_name = base
        self.display_text = base
        if ruby:
            self.base_name += u'_' + ruby
            self.display_text += u' (' + ruby + u')'