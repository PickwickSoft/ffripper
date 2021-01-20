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

from gi.repository import GLib, GdkPixbuf


class Image:

    @staticmethod
    def bytes2pixbuf(data,
                     width=150,
                     height=150):  # type: (bytes, int, int) -> GdkPixbuf.Pixbuf
        """
        converts raw bytes into a GTK PixBug

        args:
            data (bytes): raw bytes
            width (int): width of image
            height (int): height of images

        returns:
            GtkPixbuf: a GTK Pixbuf

        """
        _loader = GdkPixbuf.PixbufLoader()
        _loader.set_size(width, height)
        try:
            _loader.write(data)
            _loader.close()
        except (GLib.Error, TypeError) as e:
            print(e)
        else:
            return _loader.get_pixbuf()
