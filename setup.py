#   ffripper-1.0 - Audio-CD ripper.
#   Copyright 2020-2021 Stefan Garlonta
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; version 3 of the License.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#   USA
#

import ffripper
from setuptools import setup

data_files = [('share/applications/', ['data/ffripper.desktop']),
              ('share/icons/hicolor/scalable/apps/', ['data/ffripper.svg'])
              ('share/icons/hicolor/scalable/emblems/', ['data/cd-case.svg'])
              ]

setup(
    name=ffripper.__name__,
    packages=[ffripper.__name__],
    scripts=['bin/ffripper'],
    data_files=data_files,
    version=ffripper.__version__,
    description=ffripper.__description__,
    author=ffripper.__author__,
    author_email=ffripper.__author_email__,
    license=ffripper.__license__,
    platforms=ffripper.__platforms__,
    url=ffripper.__url__,
    download_url=ffripper.__download_url__,
    keywords=['rip', 'file format', 'audio', 'ffmpeg', 'cd']
)
