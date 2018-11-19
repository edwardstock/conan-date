#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration
import os


class DateConan(ConanFile):
    name = "date"
    version = "2.4.1"
    description = "A date and time library based on the C++11/14/17 <chrono> header"
    url = "https://github.com/bincrafters/conan-date"
    homepage = "https://github.com/HowardHinnant/date"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "0001-Improved-C-17-support.patch"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "use_system_tz_db": [True, False],
               "use_tz_db_in_dot": [True, False]}
    default_options = {"shared": False, "fPIC": True, "use_system_tz_db": True, "use_tz_db_in_dot": False}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")
            self.options.remove("use_system_tz_db")
            self.options.remove("use_tz_db_in_dot")

    def configure(self):
        compiler_version = Version(self.settings.compiler.version.value)
        if self.settings.compiler == "Visual Studio" and compiler_version < "14":
            raise ConanInvalidConfiguration("date requires Visual Studio 2015 and higher")
        if self.settings.compiler == "apple-clang" and compiler_version < "8.0":
            raise ConanInvalidConfiguration("date requires Apple Clang 8 and higher")

    def requirements(self):
        if self.settings.os == "Windows" or not self.options.use_system_tz_db:
            self.requires("libcurl/7.56.1@bincrafters/stable")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version),
                  sha256="98907d243397483bd7ad889bf6c66746db0d7d2a39cc9aacc041834c40b65b98")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        # https://github.com/HowardHinnant/date/pull/373, also https://github.com/HowardHinnant/date/pull/376
        tools.patch(base_path=self._source_subfolder, patch_file="0001-Improved-C-17-support.patch")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_DATE_TESTING"] = False
        if self.settings.os == "Windows":
            cmake.definitions["USE_TZ_DB_IN_DOT"] = False
            cmake.definitions["USE_SYSTEM_TZ_DB"] = False
        else:
            cmake.definitions["USE_TZ_DB_IN_DOT"] = self.options.use_tz_db_in_dot
            cmake.definitions["USE_SYSTEM_TZ_DB"] = self.options.use_system_tz_db
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        if self.settings.os == "Windows":
            use_system_tz_db = 0
        else:
            use_system_tz_db = 0 if self.options.use_system_tz_db else 1
        defines = ["USE_AUTOLOAD={}".format(use_system_tz_db),
                   "HAS_REMOTE_API={}".format(use_system_tz_db)]
        self.cpp_info.defines.extend(defines)
