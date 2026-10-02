# Copyright (C) 2026 Qore Technologies, s.r.o.
# SPDX-License-Identifier: MIT
# Use the pinned source epoch for RPM headers and installed file timestamps.
%global source_date_epoch_from_changelog 1
%global use_source_date_epoch_as_buildtime 1
%if v"%{rpmversion}" >= v"4.20"
%global build_mtime_policy clamp_to_source_date_epoch
%else
%global clamp_mtime_to_source_date_epoch 1
%endif
%bcond_without tests
%bcond_without docs
Name: qore-proj-module
Version: 1.1.0
Release: 3%{?dist}
Summary: Coordinate transformations and geometry projection for Qore
License: MIT
URL: https://github.com/qoretechnologies/module-proj
Source0: %{name}-%{version}.tar.xz
%global _find_debuginfo_dwz_opts %{nil}
BuildRequires: cmake >= 3.21
BuildRequires: make
BuildRequires: gcc-c++
BuildRequires: pkgconfig(proj) >= 8.0
# The CRS database is required for EPSG lookups, not only the shared library.
%if 0%{?suse_version}
BuildRequires: proj
Requires: proj
%else
BuildRequires: proj-data
Requires: proj-data
%endif
BuildRequires: qore-geos-module >= 1.0.0
Requires: qore-geos-module%{?_isa} >= 1.0.0
BuildRequires: qore-devel >= 3.0.0~
BuildRequires: qore-rpm-macros >= 3.0.0~
%if %{with docs}
BuildRequires: doxygen
BuildRequires: qore-geos-module-doc >= 1.0.0
# Require the exported index itself; OBS rewrites distribution release suffixes.
BuildRequires: %{_datadir}/qore/tags/geos.tag
%if 0%{?suse_version}
BuildRequires: util-linux
%else
BuildRequires: util-linux-core
%endif
%endif
%{?qore_enable_aot_post}

%description
Coordinate reference systems, batch transformations, geodesic calculations and
GEOS geometry projection through PROJ and ProjGeos. Uses the distribution
coordinate database and PROJ library.

%if %{with docs}
%package doc
Summary: PROJ module reference documentation
BuildArch: noarch
Requires: qore-geos-module-doc >= 1.0.0
%description doc
API reference and examples for Qore's PROJ module.
%endif

%prep
%autosetup
%build
%{?set_build_flags}
. %{_rpmconfigdir}/qore/module-env.sh
qore_set_source_prefix_maps "%{qore_debug_source_dir}"
cmake -S . -B build -G 'Unix Makefiles' \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE=-DNDEBUG \
  -DCMAKE_INSTALL_PREFIX=%{_prefix} -DCMAKE_INSTALL_LIBDIR=%{_lib} \
  -DCMAKE_SKIP_RPATH=ON -DCMAKE_IGNORE_PREFIX_PATH=/usr/local \
  -DQore_DIR=%{_libdir}/cmake/Qore -DQORE_EXECUTABLE=/usr/bin/qore \
  -DQORE_QPP_EXECUTABLE=/usr/bin/qpp -DQORE_QCC_EXECUTABLE=/usr/bin/qcc \
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
  -DGEOS_DOXYGEN_TAGFILE:FILEPATH=%{_datadir}/qore/tags/geos.tag \
  -DGEOS_DOXYGEN_TAG_URL:STRING=../../../../qore-geos-module-doc/docs/geos/html \
  -DQORE_BUILD_AOT_MODULES=ON -DQORE_AOT_LINK_SOURCE_MODULES=OFF \
  -DQORE_QM_METADATA_ENV:STRING="QORE_MODULE_DIR=$QORE_MODULE_DIR:$PWD/qlib;QORE_MODULE_DIR_ONLY=1;QORE_INCLUDE_DIR=;LD_LIBRARY_PATH=" \
  -DCMAKE_DISABLE_FIND_PACKAGE_Doxygen=%{!?with_docs:ON}%{?with_docs:OFF}
cmake --build build -- %{?_smp_mflags}
%if %{with docs}
cmake --build build --target docs -- %{?_smp_mflags}
%endif
%install
DESTDIR=%{buildroot} cmake --install build
%qore_install_aot_sources qlib
find %{buildroot}%{_libdir}/qore-modules -type f -name '*.qmod' -exec chmod 755 {} +
%if %{with docs}
install -d %{buildroot}%{_docdir}/%{name}-doc
cp -a build/docs %{buildroot}%{_docdir}/%{name}-doc/
hardlink -t -O %{buildroot}%{_docdir}/%{name}-doc
%endif
%check
%if %{with tests}
. %{_rpmconfigdir}/qore/module-env.sh
for test in test/*.qtest; do
  timeout 180 /usr/bin/qore -b --enable-debug \
    -l "$PWD/build/proj-api-$(/usr/bin/qore --latest-module-api).qmod" \
    -l "$PWD/build/qlib-qmod/ProjGeos/ProjGeos.qmod" "$test" -v
done
%endif
%files
%license COPYING.MIT
%doc README
%{_libdir}/qore-modules/proj-api-*.qmod
%{_libdir}/qore-modules/ProjGeos/
%{_datadir}/qore-modules/ProjGeos/
%dir %{_datadir}/qore/metadata/proj
%{_datadir}/qore/metadata/proj/*.meta.json
%if %{with docs}
%files doc
%license COPYING.MIT
%doc %{_docdir}/%{name}-doc/
%endif
%changelog
* Fri Oct 02 2026 David Nichols <david@qore.org> - 1.1.0-3
- Require the exported GEOS documentation index independently of release suffixes.

* Thu Oct 01 2026 David Nichols <david@qore.org> - 1.1.0-2
- Require the distribution CRS database for build tests and installed transforms.

* Thu Oct 01 2026 David Nichols <david@qore.org> - 1.1.0-1
- Package coordinate transformations and GEOS integration with offline tests.
