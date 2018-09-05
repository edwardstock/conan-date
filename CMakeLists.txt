cmake_minimum_required(VERSION 3.0.2)

project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if (WIN32 AND BUILD_SHARED_LIBS)
    set(DATE_BUILD_DLL ON)
endif(WIN32 AND BUILD_SHARED_LIBS)

add_subdirectory(source_folder)
