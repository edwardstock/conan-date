#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def is_sudo_enabled(self):
        if "CONAN_SYSREQUIRES_SUDO" not in os.environ:
            if os.name == 'posix' and os.geteuid() == 0:
                return False
            if os.name == 'nt':
                return False
        return os.getenv("CONAN_SYSREQUIRES_SUDO", True)

    def copy_utc(self):
        if tools.os_info.is_linux:
            zoneinfo_dir = os.path.join(os.sep, "usr", "share", "zoneinfo")
            if not os.path.exists(os.path.join(zoneinfo_dir, "UTC")):
                sudo = "sudo " if self.is_sudo_enabled() else ""
                try:
                    if not os.path.exists(zoneinfo_dir):
                        self.run("{} mkdir -p {}".format(sudo, zoneinfo_dir))
                    self.run("{} cp UTC {}".format(sudo, os.path.join(zoneinfo_dir, "UTC")))
                except:
                    pass
        elif tools.os_info.is_macos:
            zoneinfo_dir = os.path.join(os.sep, "etc", "zoneinfo")
            if not os.path.exists(os.path.join(zoneinfo_dir, "UTC")):
                try:
                    if not os.path.exists(zoneinfo_dir):
                        self.run("mkdir -p {}".format(zoneinfo_dir))
                    self.run("cp UTC {}".format(os.path.join(zoneinfo_dir, "UTC")))
                except:
                    pass
        elif tools.os_info.is_windows:
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                zoneinfo_dir = winreg.QueryValueEx(key, downloads_guid)[0]

            with tools.chdir(zoneinfo_dir):
                if os.path.isfile("tzdata2018g.tar.gz"):
                    os.unlink("tzdata2018g.tar.gz")
                if not os.path.exists(os.path.join("tzdata", "version")):
                    tools.get("https://data.iana.org/time-zones/releases/tzdata2018g.tar.gz", destination="tzdata")
                if not os.path.exists(os.path.join("tzdata", "windowsZones.xml")):
                    tools.download("http://unicode.org/repos/cldr/trunk/common/supplemental/windowsZones.xml",
                                   os.path.join("tzdata", "windowsZones.xml"))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        self.copy_utc()

    def test(self):
        with tools.environment_append({"TZ": "America/Los_Angeles"}):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
