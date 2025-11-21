cmake_minimum_required(VERSION 3.5)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Explicitly set component directories, making src the main
set(COMPONENT_DIRS "src" "components" "$ENV{IDF_PATH}/components")
set(EXTRA_COMPONENT_DIRS "components")

project(starter_template_espidf)