# - Find PROJ (Cartographic Projections Library)
# Fallback find-module used when PROJ's upstream CMake config package
# (proj-config.cmake, shipped in PROJ 8+) is unavailable.
#
# Once done this will define:
#  PROJ_FOUND       - system has PROJ
#  PROJ_INCLUDE_DIR - the PROJ include directory
#  PROJ_LIBRARY     - the PROJ library
#
# Supported platforms: Ubuntu, Alpine, macOS (Homebrew/MacPorts), Fedora, FreeBSD

find_package(PkgConfig QUIET)
if(PKG_CONFIG_FOUND)
    pkg_check_modules(PC_PROJ QUIET proj)
endif()

find_path(PROJ_INCLUDE_DIR proj.h
    HINTS
        ${PC_PROJ_INCLUDEDIR}
        ${PC_PROJ_INCLUDE_DIRS}
        ${PROJ_DIR}/include
        $ENV{PROJ_DIR}/include
    PATHS
        /usr/include
        /usr/local/include
        /opt/local/include          # MacPorts
        /opt/homebrew/include       # Homebrew ARM
        /usr/local/opt/proj/include # Homebrew x86
)

find_library(PROJ_LIBRARY
    NAMES proj
    HINTS
        ${PC_PROJ_LIBDIR}
        ${PC_PROJ_LIBRARY_DIRS}
        ${PROJ_DIR}/lib
        $ENV{PROJ_DIR}/lib
    PATHS
        /usr/lib
        /usr/lib64
        /usr/local/lib
        /usr/local/lib64
        /opt/local/lib              # MacPorts
        /opt/homebrew/lib           # Homebrew ARM
        /usr/local/opt/proj/lib     # Homebrew x86
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(PROJ DEFAULT_MSG PROJ_LIBRARY PROJ_INCLUDE_DIR)

mark_as_advanced(PROJ_INCLUDE_DIR PROJ_LIBRARY)
