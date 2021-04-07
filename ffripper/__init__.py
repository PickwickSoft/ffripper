#!/usr/bin/python3

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

"""
A fast, powerful and simple-to-use graphical CD ripper
"""

__major__ = 0
__minor__ = 1
__release__ = 0
__prerelease__ = ""  # alpha, beta, rc etc.

# package information
__name__ = "ffripper".encode('utf-8')
if __release__ == 0:
    __version__ = "{0}.{1}".format(__major__, __minor__)
else:
    __version__ = "{0}.{1}.{2}".format(__major__, __minor__, __release__)
__version__ += __prerelease__
__version__.encode('utf-8')
__description__ = "Fast audio-cd ripper".encode('utf-8')
__author__ = "Stefan Garlonta".encode('utf-8')
__author_email__ = "stefan.garlonta@gmail.com".encode('utf-8')
__license__ = "GNU GPL3".encode('utf-8')
__platforms__ = ["Linux"]
__url__ = "https://github.com/ThePickwickClub/ffripper".encode('utf-8')
__download_url__ = "".encode('utf-8')
