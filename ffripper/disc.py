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

import os, shlex


class Disc:

    def __init__(self):
        self.mount_point = self.get_mount_point()

    def get_mount_point(self):
        self.mount_point = self._get_point_by_desktop_session()
        return self.mount_point

    @staticmethod
    def _get_point_by_desktop_session():
        desktop_session = os.environ.get("DESKTOP_SESSION")
        if desktop_session is not None:
            desktop_session = desktop_session.lower()
            if desktop_session in ["gnome", "ubuntu"]:
                return "/run/user/1000/gvfs/cdda:host=sr0"
            elif desktop_session in ["unity", "cinnamon", "pantheon"]:
                return ""
            elif desktop_session == "mate":
                ""
            elif desktop_session == "lxde":
                ""
            elif desktop_session == "xfce" or desktop_session.startswith("xubuntu"):
                ""
            elif desktop_session in ["kde", "kde3", "trinity"]:
                ""
            elif desktop_session in ["fluxbox", "jwm", "openbox", "afterstep"]:
                ""
            elif desktop_session == "blackbox":
                ""
            elif desktop_session == "windowmaker":
                ""

    def is_disc(self):
        return bool(os.path.isdir(self.mount_point))
