#!/usr/bin/python3
# -*- coding: utf-8 -*-

#   ffripper - Audio-CD ripper.
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
import os, shutil
import ffripper
from distutils.core import setup

def install_desktop():
    """
    Copy the ffripper.desktop file to /usr/share/applications/
    """
    shutil.copyfile("data/ffripper.desktop", "/usr/share/applications/ffripper.desktop")

if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again using 'sudo python3 setup.py install'")

data_files = [# ('share/applications/', ['data/ffripper.desktop']),
              ('share/icons/hicolor/scalable/apps/', ['data/ffripper.svg']),
              ('share/icons/hicolor/scalable/emblems/', ['data/cd-case.svg']),
              ('share/ffripper/', ['data/ffripper.glade']),
              ('share/ffripper/', ['data/settings.yaml'])
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
    keywords=['rip', 'file format', 'audio', 'ffmpeg', 'cd', 'ffripper'],
    install_requires=['rich'],
)

install_desktop()

if os.path.exists('/usr/share/ffripper/'):
    os.chmod('/usr/share/ffripper/settings.yaml', 0o777)
elif os.path.exists('/usr/local/share/ffripper/'):
    os.chmod('/usr/local/share/ffripper/settings.yaml', 0o777)