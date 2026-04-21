cmake_minimum_required(VERSION 3.5)

project(qore-proj-module)

set(VERSION_MAJOR 1)
set(VERSION_MINOR 1)
set(VERSION_PATCH 0)

# where to look first for cmake modules, before ${CMAKE_ROOT}/Modules/ is checked
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)

find_package(Qore 0.9 REQUIRED)

# Try PROJ's own CMake config package first (PROJ 8+). Falls back to our
# FindPROJ.cmake which uses pkg-config (works for distro-packaged 6.x/7.x).
find_package(PROJ CONFIG QUIET)
if(PROJ_FOUND AND TARGET PROJ::proj)
    set(PROJ_LIBRARY PROJ::proj)
    message(STATUS "Found PROJ via CMake config: ${PROJ_VERSION}")
else()
    find_package(PROJ REQUIRED)
    include_directories(${PROJ_INCLUDE_DIR})
    set(PROJ_LIBRARY ${PROJ_LIBRARY})
endif()

# ensure qdx can find the proj binary module and user modules when processing .qc files
set(QORE_MODULE_DIR_FOR_DOCS "${CMAKE_BINARY_DIR}:${CMAKE_SOURCE_DIR}/qlib")

include_directories(${CMAKE_SOURCE_DIR}/src)

set(QPP_SRC
    src/ql_proj.qpp
    src/QC_ProjTransformer.qpp
)

set(CPP_SRC
    src/proj-module.cpp
)

set(QMOD
    qlib/ProjGeos
)

# C++17 required
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++17" COMPILER_SUPPORTS_CXX17)
if(COMPILER_SUPPORTS_CXX17)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")
else()
    message(FATAL_ERROR "The compiler ${CMAKE_CXX_COMPILER} has no C++17 support. Please use a different C++ compiler.")
endif()

qore_wrap_qpp_value(QPP_SOURCES METALIST QPP_META_SOURCES ${QPP_SRC})

set(module_name "proj")

set(QORE_DOX_TMPL_SRC
    docs/mainpage.doxygen.tmpl
)

add_library(${module_name} MODULE ${CPP_SRC} ${QPP_SOURCES})

if(WIN32 AND MINGW AND MSYS)
    target_compile_definitions(${module_name} PUBLIC BUILDING_DLL)
endif()

if(DEFINED ENV{DOXYGEN_EXECUTABLE})
    set(DOXYGEN_EXECUTABLE $ENV{DOXYGEN_EXECUTABLE})
endif()

qore_external_binary_module(${module_name} "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}" ${PROJ_LIBRARY})

if(COMMAND qore_install_qpp_metadata)
    qore_install_qpp_metadata(${module_name} ${QPP_META_SOURCES})
else()
    install(FILES ${QPP_META_SOURCES}
            DESTINATION ${CMAKE_INSTALL_DATADIR}/qore/metadata)
endif()

qore_user_modules("${QMOD}")

qore_external_user_module("qlib/ProjGeos" "")

qore_dist("${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}")

qore_config_info()

if(DOXYGEN_FOUND)
    qore_wrap_dox(QORE_DOX_SRC ${QORE_DOX_TMPL_SRC})
    add_custom_target(QORE_MOD_DOX_FILES DEPENDS ${QORE_DOX_SRC})
    add_dependencies(docs-module QORE_MOD_DOX_FILES)
endif()
