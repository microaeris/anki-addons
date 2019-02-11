# -*- mode: python ; coding: utf-8 -*-
#
# Copyright © 2012–15 Roland Sieker <ospalh@gmail.com>
#
# License: GNU AGPL, version 3 or later;
# http://www.gnu.org/copyleft/agpl.html

u"""
One just moves files and isn’t used. The other does simple audio
processing and nmoves the files.
"""

from sys import path
from os.path import dirname
path.append('/usr/local/lib/python2.7/dist-packages/') # Hack, but append anki's python path to find locally installed pydub
path.append(dirname(__file__))

try:
    from pydub.silence import detect_nonsilent
    # Look for a reasonable new pydub
except ImportError as e:
    processor = None
else:
    from audio_processor import AudioProcessor
    processor = AudioProcessor()
