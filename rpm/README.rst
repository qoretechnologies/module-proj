RPM packaging
=============

Copyright 2026 Qore Technologies, s.r.o.

The canonical qore-proj-module.spec supports Fedora, Enterprise Linux and
openSUSE. It requires the Qore 3.0 SDK and qore-rpm-macros from the same repository.
The default build includes module tests and a separate documentation package.
Dependencies on the installed Qore ABI and SDK version are generated from the
built module; do not replace them with an unversioned qore dependency.

Prepare a pinned source bundle with qore-packaging, then build it in the target
distribution with networking disabled::

    python3 tools/packaging.py prepare --repo ../module-proj --ref COMMIT \
      --name qore-proj-module --version 1.1.0 \
      --spec qore-proj-module.spec --output work/proj-source
    python3 tools/build-local.py --source work/proj-source \
      --image TARGET_SDK_IMAGE --output results/proj-build --jobs 2

These commands run from the qore-packaging repository. Source preparation uses
the committed tree. Install the SDK's language documentation index for complete
Doxygen cross-references. --without docs and --without tests are available for
local diagnosis; repository qualification uses the defaults and also runs the
suite against installed RPMs outside the checkout. Native modules retain the
distribution's normal ELF stripping and separate debug packages.

The package includes native and AOT modules, source fallbacks and separate debug
information. RPM post-processing preserves the AOT dependency trailers.

ProjGeos requires the GEOS module at build and run time. The default checks
exercise native and AOT APIs; the optional Python interoperability case also
runs when that module is installed and reports an explicit skip otherwise.

EPSG transforms require the PROJ CRS database in addition to its shared library.
The RPM depends on ``proj`` on openSUSE and ``proj-data`` on Fedora and
Enterprise Linux, both during the build and at runtime. Minimal installations
therefore retain the same coordinate-system lookup support as the build tests.

Documentation builds require the exported ``/usr/share/qore/tags/geos.tag``
file from ``qore-geos-module-doc``. This expresses the required feature without
comparing distribution release suffixes, which OBS rewrites. OBS projects must
map this file with ``FileProvides: /usr/share/qore/tags/geos.tag qore-geos-module-doc``
because their dependency solver does not import complete RPM file lists.

The file BuildRequires uses the literal system path. OBS resolves build dependencies
before the build root exists and does not expand ``%{_datadir}`` there. The
installed documentation remains under the usual RPM data-directory macro.

Release 5 uses CMake policies through 3.31, provides the standard manifest-based
uninstall target, and tests staged removal, missing manifests, directories and
dangling symlinks. Module paths come from the Qore SDK; unused CMAKE_INSTALL_LIBDIR
and FetchContent options are omitted. Optional Java generation is disabled
because these RPMs ship no Java artifact. Native, AOT and documentation builds
remain enabled with normal compiler flags.

AOT debugger compatibility
--------------------------

RPMs retain full DWARF, debug source and Qore compiler metadata. They omit
LLVM's optional precomputed name index, which distribution GDB ignores and
debugedit cannot process. This uses the configuration approved on 2026-10-06;
initial debugger loading may be slower. Leap requires debugedit 5.1 for the
remaining DWARF forms. Package checks verify metadata and separate debug links;
paired controls verify all other DWARF sections and symbols remain identical.

The four deliberate invalid-CRS cases retain PROJ's three exact stderr messages
for an unknown EPSG code, an unknown projection and an empty CRS. These were
approved on 2026-10-06 after standalone controls verified rejection, recovery
and zero Valgrind errors or retained allocations on all three distributions.
Other diagnostics remain qualification failures.
