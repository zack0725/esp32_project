# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "D:/Programs/esp/Espressif/frameworks/esp-idf-v5.2.2/components/bootloader/subproject"
  "F:/project/esp32_project/ov2640/build/bootloader"
  "F:/project/esp32_project/ov2640/build/bootloader-prefix"
  "F:/project/esp32_project/ov2640/build/bootloader-prefix/tmp"
  "F:/project/esp32_project/ov2640/build/bootloader-prefix/src/bootloader-stamp"
  "F:/project/esp32_project/ov2640/build/bootloader-prefix/src"
  "F:/project/esp32_project/ov2640/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "F:/project/esp32_project/ov2640/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "F:/project/esp32_project/ov2640/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
