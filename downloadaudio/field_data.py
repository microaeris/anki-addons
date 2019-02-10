# -*- mode: python ; coding: utf-8 -*-
#
# Copyright © 2015 Roland Sieker <ospalh@gmail.com>
#
# License: GNU AGPL, version 3 or later;
# http://www.gnu.org/copyleft/agpl.html

"""
Two classes to store information for the downloader
"""

from anki.sound import stripSounds
from anki.template import furigana
from anki.utils import stripHTML

import re

# Apparently some people use a 「・」 between the kana for different
# kanji. Make it easier to switch removing them for the downloads on
# or off
strip_interpunct = False
# Do or do not remove katakana interpuncts 「・」 before sending requests.


class FieldData(object):
    def __init__(self, w_field, a_field, word):
        self.word_field_name = w_field
        self.audio_field_name = a_field
        # This is taken from aqt/browser.py.
        self.word = word.replace(u'<br>', u' ')
        self.word = self.word.replace(u'<br />', u' ')
        if strip_interpunct:
            self.word = self.word.replace(u'・', u'')
        self.word = stripHTML(self.word)
        self.word = stripSounds(self.word)
        # Reformat so we have exactly one space between words.
        self.word = u' '.join(self.word.split())

    @property
    def empty(self):
        return not self.word

    @property
    def split(self):
        return False


class JapaneseFieldData(FieldData):
    def __init__(self, w_field, a_field, word):
        FieldData.__init__(self, w_field, a_field, word)
        self._sanitize_field_data()
        self.kanji = furigana.kanji(self.word)
        self.kana = furigana.kana(self.word)

    @property
    def empty(self):
        return not self.kanji

    @property
    def split(self):
        return True

    def _sanitize_field_data(self):
        '''
        Additional cleanup for Japanese field data.
        Remove any symbols such as `~` and remove everything in parenthesis,
        and finally, remove anything alphabetical.
        '''
        bad_chars = ['…', '~', '〜']
        for char in bad_chars:
            self.word = self.word.replace(char, '')

        # Sick regex bro. What does it do?
        # Selects for characters in parenthesis and remove it.
        # Parenthesis can be `()` or `（）`. The second set of parenthesis are
        # used with kana and has a preceding space and a proceeding space.
        #
        # Examples
        # 静[しず]か（な）
        # 頂[いただ]く(もらう)
        # （〜を）ください
        # ~から　( goes withまで）
        # （〜を）おねがいします
        #
        # Selects
        # 静[しず]か`（な）`
        # 頂[いただ]く`(もらう)`
        # `（〜を）`ください
        # ~から　`( goes withまで）`
        # `（〜を）`おねがいします
        self.word = re.sub("([（(]{1}.+?[）)]{1})", "", self.word)

        # Remove any alphanumeric characters left.
        # Examples
        # あまり+ negative
        self.word = re.sub(" ?([0-9a-zA-Z_]+) ?", "", self.word)

        # Remove `+` and any of its surrounding white space
        self.word = re.sub("( ?\+ ?)", "", self.word)
