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
