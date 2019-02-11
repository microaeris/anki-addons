# -*- mode: python ; coding: utf-8 -*-
#
# Copyright © 2012–2015 Roland Sieker <ospalh@gmail.com>
#
# License: GNU AGPL, version 3 or later;
# http://www.gnu.org/copyleft/agpl.html


"""
Download pronunciations from Forvo.
"""

import os
import urllib

try:
    import simplejson as json
except ImportError:
    import json

from download_entry import DownloadEntry
from downloader import AudioDownloader


# When downloading Japanese audio, set a preference for audio from
# a user called `strawberrybrown`. She has uploaded 23k+ recordings
# and speaks with a standard Japanese accent.
PREFERRED_USERNAME = 'strawberrybrown'
KEY_FILE_NAME = 'forvokey.py'
API_KEY_LEN = 32


class ForvoDownloader(AudioDownloader):
    """Download audio from Forvo"""

    def __init__(self):
        AudioDownloader.__init__(self)
        # Keep these two in sync
        self.file_extension = u'.ogg'
        self.path_code = 'pathogg'
        # Get the API key if the key is valid
        api_key_file_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        api_key_file_path = os.path.join(api_key_file_path, KEY_FILE_NAME)
        api_key_file = open(api_key_file_path)
        self.api_key = api_key_file.read()
        self._is_api_key_valid()
        api_key_file.close()
        # Build the query URL
        self.url = 'http://apifree.forvo.com/action/word-pronunciations/' \
            'format/json/order/rate-desc/limit/1/' \
            'key/%s/word/' % (self.api_key)
        self.icon_url = 'http://www.forvo.com/'
        self.gender_dict = {'f': u'♀', 'm': u'♂'}
        self.field_data = None

    def _is_api_key_valid(self):
        # Check that the user supplied key seems valid.
        # If the key is not valid, skip downloading files from Forvo.
        if (len(self.api_key) != API_KEY_LEN) or \
                not self.api_key.isalnum():
            self.api_key = None

    def download_files(self, field_data):
        """
        Get pronunciations of a word from Forvo
        """
        if self.api_key is None:
            # Please note, you are not using a valid Forvo API key.
            # If you want to download audio from Forvo using their API,
            # you can purchase one at https://api.forvo.com/
            return
        self.downloads_list = []
        self.field_data = field_data
        # if field_data.split:
        #     return
        if not field_data.kanji or not field_data.word:
            return
        self.maybe_get_icon()

        # First query for preferred user's reading
        # Caveat! The old code used Json.load(response) with a
        # file-like object.  now we use Json.loads(get_data()) with a
        # string. Don't confuse load() with loads()!
        reply_dict = json.loads(self.get_data_from_url(
                                self.query_url(PREFERRED_USERNAME)))
        print(reply_dict)
        if reply_dict['attributes']['total'] != 0:
            # Found reading from preferred user.
            self.get_items(reply_dict['items'])
            return

        # If not available, grab the top rating reading from Forvo.
        reply_dict = json.loads(self.get_data_from_url(self.query_url()))
        self.get_items(reply_dict['items'])

    def get_items(self, items_list):
        for itm in items_list:
            extras = dict(Source='Forvo.com')
            try:
                user_str = itm['username']
            except KeyError:
                pass
            else:
                try:
                    user_str += u' ({0})'.format(self.gender_dict[itm['sex']])
                except KeyError:
                    pass
                extras['User'] = user_str
            try:
                extras['Language'] = itm['langname']
            except KeyError:
                pass
            try:
                extras['Rating'] = itm['rate']
            except KeyError:
                pass
            try:
                file_path = self.get_tempfile_from_url(itm[self.path_code])
                # I guess the try is not really necessary. Anyway.
            except (ValueError, KeyError):
                continue
            entry = DownloadEntry(
                self.field_data, file_path, extras, self.site_icon)
            entry.file_extension = self.file_extension
            self.downloads_list.append(entry)
        # No clean-up

    def query_url(self, preferred_username=None):
        term = self.field_data.kanji if self.field_data.kanji else self.field_data.word
        built_url = self.url + urllib.parse.quote(term.encode('utf-8'))
        if self.language:
            built_url += '/language/' + self.language
        if preferred_username is not None:
            built_url += '/username/' + preferred_username
        print(built_url)
        return built_url + '/'
