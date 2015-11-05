cmake_minimum_required(VERSION 2.8)

project(mylib)

add_library(alex STATIC alex.cpp)

install(TARGETS alex DESTINATION lib)
install(FILES alex.h DESTINATION include)
