#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class LibnameConan(ConanFile):
    name = "date"
    version = "2.4.1"
    url = "https://github.com/bincrafters/conan-date"
    description = "A date and time library based on the C++11/14/17 <chrono> header "

    # Indicates License type of the packaged library
    license = "MIT"

    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]

    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "use_system_tz_db": [True, False],
               "use_tz_db_in_dot": [True, False], }
    default_options = ("shared=False", "use_system_tz_db=True", "use_tz_db_in_dot=False")

    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_folder"
    build_folder = "build_folder"

    # Use version ranges for dependencies unless there's a reason not to
    def requirements(self):
        if not self.options.use_system_tz_db:
            self.requires("libcurl/[>=7.52.1]@bincrafters/stable")

    def source(self):
        source_url = "https://github.com/HowardHinnant/date"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)

        # Helper method for common CMake configurations

        self.wrap_cmake()

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = False # example
        cmake.definitions["USE_SYSTEM_TZ_DB"] = self.options.use_system_tz_db
        cmake.definitions["USE_TZ_DB_IN_DOT"] = self.options.use_tz_db_in_dot
        cmake.definitions["BUILD_TZ_STATIC"] = not self.options.shared
        cmake.configure(source_folder=self.source_subfolder, build_folder=self.build_folder)
        cmake.build()
        cmake.install()

    def package(self):
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can replace all the steps below with the word "pass"
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="LICENSE")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)


    # Helper method for common CMake configurations
    def wrap_cmake(self):
        with tools.chdir(self.source_subfolder):
            os.rename("CMakeLists.txt", "CMakeListsOriginal.txt")

        cmake_wrapper_new = os.path.join(self.source_subfolder, "CMakeLists.txt")
        os.rename("CMakeLists.txt", cmake_wrapper_new)
