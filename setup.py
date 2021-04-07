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

import os
import ffripper
import sys

try:
    import DistUtilsExtra.auto
except ImportError:
    sys.stderr.write('You need python-distutils-extra\n')
    sys.exit(1)

import DistUtilsExtra.auto


class Install(DistUtilsExtra.auto.install_auto):
    def run(self):
        DistUtilsExtra.auto.install_auto.run(self)
        print("Changing mode of settings.yaml to 777")
        if os.path.exists('/usr/share/ffripper/'):
            os.chmod('/usr/share/ffripper/settings.yaml', 0o777)
        elif os.path.exists('/usr/local/share/ffripper/'):
            os.chmod('/usr/local/share/ffripper/settings.yaml', 0o777)


DistUtilsExtra.auto.setup(
    name="ffripper",
    version=ffripper.__version__,
    description=(
        ffripper.__description__
    ),
    license=ffripper.__license__,
    data_files=[
        ('share/icons/hicolor/scalable/emblems/', ['data/cd-case.svg']),
        ('share/icons/hicolor/scalable/apps/', ['data/ffripper.svg'])
    ],
    cmdclass={
        'install': Install
    },
    url=ffripper.__url__,
    download_url=ffripper.__download_url__,
    author=ffripper.__author__,
    author_email=ffripper.__author_email__
)
