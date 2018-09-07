#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class DateConan(ConanFile):
    name = "date"
    version = "2.4.1"
    url = "https://github.com/bincrafters/conan-date"
    homepage = "https://github.com/HowardHinnant/date"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "A date and time library based on the C++11/14/17 <chrono> header"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "use_system_tz_db": [True, False], "use_tz_db_in_dot": [True, False]}
    default_options = ("shared=False", "fPIC=True", "use_system_tz_db=True", "use_tz_db_in_dot=False")
    source_subfolder = "source_folder"
    build_folder = "build_folder"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def requirements(self):
        if not self.options.use_system_tz_db:
            self.requires("libcurl/7.56.1@bincrafters/stable")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_DATE_TESTING"] = False
        cmake.definitions["USE_SYSTEM_TZ_DB"] = self.options.use_system_tz_db
        cmake.definitions["USE_TZ_DB_IN_DOT"] = self.options.use_tz_db_in_dot
        cmake.configure(build_folder=self.build_folder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        use_system_tz_db = 0 if self.options.use_system_tz_db else 1
        defines = ["USE_AUTOLOAD={}".format(use_system_tz_db),
                   "HAS_REMOTE_API={}".format(use_system_tz_db)]
        self.cpp_info.defines.extend(defines)
