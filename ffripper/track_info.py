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

class TrackInfo:

    def __init__(self, track_name, track_length, track_year, track_artist):
        self.track_name = track_name
        self.track_length = track_length
        self.track_year = track_year
        self.track_artist = track_artist

    def get_name(self):
        return self.track_name

    def get_length(self):
        return self.track_length

    def get_year(self):
        return self.track_year

    def get_artist(self):
        return self.track_artist
