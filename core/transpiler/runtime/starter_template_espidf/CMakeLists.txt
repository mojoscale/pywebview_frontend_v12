cmake_minimum_required(VERSION 3.16)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Explicitly set component directories, making src the main
set(COMPONENT_DIRS "src" "components" "$ENV{IDF_PATH}/components")
set(EXTRA_COMPONENT_DIRS "components")

set(COMPONENT_EMBED_TXTFILES "")
set(COMPONENT_EMBED_FILES "")

project(starter_template_espidf)