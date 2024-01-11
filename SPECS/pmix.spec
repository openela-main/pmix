Name:           pmix
Version:        2.2.5
Release:        1%{?dist}
Summary:        Process Management Interface Exascale (PMIx)
License:        BSD
URL:            https://pmix.org/
Source0:        https://github.com/pmix/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.bz2

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  environment(modules)
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  libevent-devel
BuildRequires:  libtool
BuildRequires:  perl-interpreter
BuildRequires:  pkgconf
BuildRequires:  pkgconfig(hwloc)
BuildRequires:  pkgconfig(munge)

Provides:       pmi
Requires:       environment(modules)

%description
The Process Management Interface (PMI) has been used for quite some time as
a means of exchanging wireup information needed for interprocess
communication. Two versions (PMI-1 and PMI-2) have been released as part of
the MPICH effort. While PMI-2 demonstrates better scaling properties than its
PMI-1 predecessor, attaining rapid launch and wireup of the roughly 1M
processes executing across 100k nodes expected for exascale operations remains
challenging.

PMI Exascale (PMIx) represents an attempt to resolve these questions by
providing an extended version of the PMI standard specifically designed to
support clusters up to and including exascale sizes. The overall objective of
the project is not to branch the existing pseudo-standard definitions - in
fact, PMIx fully supports both of the existing PMI-1 and PMI-2 APIs - but
rather to (a) augment and extend those APIs to eliminate some current
restrictions that impact scalability, and (b) provide a reference
implementation of the PMI-server that demonstrates the desired level of
scalability.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%setup -q -n %{name}-%{version}

echo touching lexer sources to recompile them ...
find src -name \*.l -print -exec touch --no-create {} \;

%build
%{_builddir}/%{name}-%{version}/autogen.pl
%configure \
    --prefix=%{_prefix} \
    --sysconfdir=%{_sysconfdir}/%{name} \
    --disable-static \
    --disable-silent-rules \
    --enable-pmix-binaries \
    --with-tests-examples \
    --enable-shared \
    --enable-pmi-backward-compatibility \
    --with-munge

%make_build V=1

%check
%{__make} check

%install
%make_install

# remove libtool archives
find %{buildroot} -name '*.la' | xargs rm -f

# move libpmi/libpmi2 for environment module usage
install -d -m 0755 %{buildroot}%{_libdir}/%{name}/lib
mv %{buildroot}%{_libdir}/libpmi.so* %{buildroot}%{_libdir}/%{name}/lib
mv %{buildroot}%{_libdir}/libpmi2.so* %{buildroot}%{_libdir}/%{name}/lib

# set up pmix self-test infra for install
install -d -m 0755 %{buildroot}%{_datadir}/%{name}/test
for f in pmix_client pmix_regex
do
  mv test/.libs/$f %{buildroot}%{_datadir}/%{name}/$f
done
mv test/.libs/pmix_test %{buildroot}%{_datadir}/%{name}/test/pmix_test

# install pmi/pmix environment module file
install -d -m 0755 %{buildroot}%{_modulesdir}/pmi
cat >%{buildroot}%{_modulesdir}/pmi/%{name}-%{_arch} <<EOF
#%%Module 1.0
#
#  pmi/pmix module for use with 'environment-modules' package:
#
conflict         pmi
prepend-path     LD_LIBRARY_PATH    %{_libdir}/%{name}/lib
prepend-path     PKG_CONFIG_PATH    %{_libdir}/%{name}/lib/pkgconfig
EOF

# install pkgconfig file pmix.pc
install -d -m 0755 %{buildroot}%{_libdir}/pkgconfig
cat >%{buildroot}%{_libdir}/pkgconfig/%{name}.pc <<EOF
includedir=%{_includedir}
libdir=%{_libdir}

Name: %{name}
Version: %{version}
Description: PMI Exascale (PMIx) library
Cflags: -I\${includedir}
Libs: -L\${libdir} -lpmix
EOF

# install pkgconfig file pmi.pc for environment module usage
install -d -m 0755 %{buildroot}%{_libdir}/%{name}/lib/pkgconfig
cat >%{buildroot}%{_libdir}/%{name}/lib/pkgconfig/pmi.pc <<EOF
includedir=%{_includedir}
libdir=%{_libdir}/%{name}/lib

Name: pmi
Version: %{version}
Description: (PMIx) PMI compatibility library
Cflags: -I\${includedir}
Libs: -L\${libdir} -lpmi
EOF

# install pkgconfig file pmi2.pc for environment module usage
install -d -m 0755 %{buildroot}%{_libdir}/%{name}/lib/pkgconfig
cat >%{buildroot}%{_libdir}/%{name}/lib/pkgconfig/pmi2.pc <<EOF
includedir=%{_includedir}
libdir=%{_libdir}/%{name}/lib

Name: pmi2
Version: %{version}
Description: (PMIx) PMI2 compatibility library
Cflags: -I\${includedir}
Libs: -L\${libdir} -lpmi2
EOF

%ldconfig_scriptlets
%ldconfig_scriptlets devel

%files
%license LICENSE
%doc README
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/test
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/lib
%dir %{_modulesdir}/pmi
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%{_datadir}/%{name}/*.txt
%{_datadir}/%{name}/pmix_*
%{_datadir}/%{name}/test/pmix_test
%{_libdir}/libpmix.so.*
%{_libdir}/libmca_common_dstore.so.*
%{_libdir}/%{name}/*.so
%{_libdir}/%{name}/lib/*.so.*
%{_modulesdir}/pmi/*

%files devel
%{_datadir}/%{name}/*.supp
%{_includedir}/*.h
%{_libdir}/libpmix.so
%{_libdir}/libmca_common_dstore.so
%{_libdir}/%{name}/lib/*.so
%{_libdir}/%{name}/lib/pkgconfig/*.pc
%{_libdir}/pkgconfig/*.pc

%changelog
* Mon Oct 11 2021 Honggang Li <honli@redhat.com> - 2.2.5-1
- Update to 2.2.5
- Related: rhbz#2008513

* Wed Jun 03 2020 Honggang Li <honli@redhat.com> - 2.2.4rc1-1
- Update to 2.2.4rc1
- Related: rhbz#1840596

* Mon Apr 20 2020 Honggang Li <honli@redhat.com> - 2.2.3-1
- Update to 2.2.3
- Add pmix-devel into CRB repository
- Related: rhbz#1816198, rhbz#1822520

* Wed Mar 20 2019 Jarod Wilson <jarod@redhat.com> - 2.1.1-2
- Add the --with-tests-examples flag to be able to better verify functionality
- Related: rhbz#1682374

* Fri Mar 16 2018 Philip Kovacs <pkdevel@yahoo.com> - 2.1.1-1
- Update to 2.1.1

* Sun Feb 18 2018 Philip Kovacs <pkdevel@yahoo.com> - 2.1.0-3
- Add patch to remove unneeded check for C++

* Thu Feb 15 2018 Philip Kovacs <pkdevel@yahoo.com> - 2.1.0-2
- Rebuild for libevent soname bump

* Sat Feb 10 2018 Philip Kovacs <pkdevel@yahoo.com> - 2.1.0-1
- Update to 2.1.0
- Added enviromnent module for pmi/pmix
- Added pkgconfig files for pmix/pmi/pmi2
- Ensure lexer sources are rebuilt
- Removed obsolete sasl support
- Use new ldconfig_scriplets macro

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Mar 21 2017 Orion Poplawski <orion@cora.nwra.com> - 1.2.2-1
- Update to 1.2.2

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Sep 7 2016 Orion Poplawski <orion@cora.nwra.com> - 1.1.5-1
- Update to 1.1.5

* Fri Jun 10 2016 Orion Poplawski <orion@cora.nwra.com> - 1.1.4-1
- Update to 1.1.4

* Tue Mar 8 2016 Orion Poplawski <orion@cora.nwra.com> - 1.1.3-1
- Update to 1.1.3

* Mon Nov 16 2015 Orion Poplawski <orion@cora.nwra.com> - 1.1.1-1
- Update to 1.1.1

* Sat Nov 14 2015 Orion Poplawski <orion@cora.nwra.com> - 1.1.0-1
- Update to 1.1.0

* Tue Sep  1 2015 Orion Poplawski <orion@cora.nwra.com> - 1.0.0-1
- Initial version
