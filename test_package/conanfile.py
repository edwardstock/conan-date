#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def copy_utc(self):
        if tools.os_info.is_linux:
            zoneinfo_dir = os.path.join(os.sep, "usr", "share", "zoneinfo")
            try:
                if not os.path.exists(zoneinfo_dir):
                    self.run("sudo mkdir {}".format(zoneinfo_dir))
                self.run("sudo cp UTC {}".format(os.path.join(zoneinfo_dir, "UTC")))
            except:
                pass
        elif tools.os_info.is_osx:
            zoneinfo_dir = os.path.join(os.sep, "etc", "zoneinfo")
            try:
                if not os.path.exists(zoneinfo_dir):
                    self.run("mkdir {}".format(zoneinfo_dir))
                self.run("cp UTC {}".format(os.path.join(zoneinfo_dir, "UTC")))
            except:
                pass

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        self.copy_utc()

    def test(self):
        with tools.environment_append({"TZ": "America/Los_Angeles"}):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
