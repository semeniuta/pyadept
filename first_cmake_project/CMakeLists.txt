cmake_minimum_required(VERSION 2.8)

project(my_project)

find_package(OpenCV REQUIRED)
find_package(OpenGL REQUIRED)

include_directories(src/myapp src/mylib) # search for include files in here
#include_directories(/usr/local/include/aravis-0.4 /usr/include/glib-2.0 /usr/lib/x86_64-linux-gnu/glib-2.0/include) # for Aravis
include_directories( ${OpenCV_INCLUDE_DIRS} )
#link_directories(/usr/local/lib)

add_subdirectory(src/mylib) # search for CMake project in here

add_executable(firstapp src/myapp/main.cpp)
add_executable(display src/myapp/display_image.cpp)

target_link_libraries(firstapp alex)
#target_link_libraries(firstapp libaravis-0.4.so)
target_link_libraries(display ${OpenCV_LIBS})

install(TARGETS firstapp DESTINATION bin)
install(TARGETS display DESTINATION bin)
