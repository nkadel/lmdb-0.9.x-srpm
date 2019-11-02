# The files themselves are in several subdirectories and need to be prefixed wit this.
%global archive_path libraries/lib%{name}

Name:           lmdb
Version:        0.9.22
Release:        2%{?dist}
Summary:        Memory-mapped key-value database

License:        OpenLDAP
URL:            http://symas.com/mdb/
Source0:        https://github.com/LMDB/lmdb/archive/LMDB_%{version}.tar.gz
Source1:        lmdb.pc.in
# Patch description in the corresponding file
Patch0: lmdb-make.patch
Patch1: lmdb-s390-check.patch

%if 0%{?rhel} > 0
# Addresses python36- versus python3- dependencies
BuildRequires: epel-rpm-macros
%endif

BuildRequires: doxygen
BuildRequires: gcc
BuildRequires: make

%description
LMDB is an ultra-fast, ultra-compact key-value embedded data
store developed by Symas for the OpenLDAP Project. By using memory-mapped files,
it provides the read performance of a pure in-memory database while still
offering the persistence of standard disk-based databases, and is only limited
to the size of the virtual address space.

%package        libs
Summary:        Shared libraries for %{name}

%description    libs
The %{name}-libs package contains shared libraries necessary for running
applications that use %{name}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        doc
Summary:        Documentation files for %{name}
BuildArch:      noarch
Group:          Documentation

%description    doc
The %{name}-doc package contains automatically generated documentation for %{name}.


%prep
%setup -q -n %{name}-LMDB_%{version}
%patch0 -p1 -b .make
%patch1 -p1 -b .s390-check


%build
pushd %{archive_path}
make XCFLAGS="%{optflags}" %{?_smp_mflags}
# Build doxygen documentation
doxygen
# remove unpackaged files
rm -f Doxyfile
rm -rf man # Doxygen generated manpages
popd

%install
pushd %{archive_path}
# make install expects existing directory tree
mkdir -m 0755 -p %{buildroot}{%{_bindir},%{_includedir}}
mkdir -m 0755 -p %{buildroot}{%{_libdir}/pkgconfig,%{_mandir}/man1}
make DESTDIR=%{buildroot} prefix=%{_prefix} libdir=%{_libdir} mandir=%{_mandir} install
popd

# Install pkgconfig file
sed -e 's:@PREFIX@:%{_prefix}:g' \
    -e 's:@EXEC_PREFIX@:%{_exec_prefix}:g' \
    -e 's:@LIBDIR@:%{_libdir}:g' \
    -e 's:@INCLUDEDIR@:%{_includedir}:g' \
    -e 's:@PACKAGE_VERSION@:%{version}:g' \
    %{SOURCE1} >lmdb.pc
install -Dpm 0644 -t %{buildroot}%{_libdir}/pkgconfig lmdb.pc

%check
%if 0%{?rhel} == 6 && %{_arch} == "ppc64"
  # rhel6 ppc64: skip unit tests
  exit 0
%endif

pushd %{archive_path}
rm -rf testdb
LD_LIBRARY_PATH=$PWD make test
popd

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig


%files
%{_bindir}/*
%{_mandir}/man1/*

%files libs
%doc %{archive_path}/COPYRIGHT
%doc %{archive_path}/CHANGES
%license %{archive_path}/LICENSE
%{_libdir}/*.so.*

%files devel
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%files doc
%doc %{archive_path}/html
%doc %{archive_path}/COPYRIGHT
%doc %{archive_path}/CHANGES
%license %{archive_path}/LICENSE


%changelog
* Mon Apr 23 2018 Florin Asavoaie <florin.asavoaie@gmail.com> - 0.9.22-2
- Fixed Build Dependencies
- Made build work on CentOS 7 for EPEL

* Tue Apr 10 2018 Jan Staněk <jstanek@redhat.com> - 0.9.22-1
- Updated to 0.9.22

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.21-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.21-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.21-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jun 02 2017 Jan Stanek <jstanek@redhat.com> - 0.9.21-1
- Update to 0.9.21

* Mon Mar 20 2017 Jan Stanek <jstanek@redhat.com> - 0.9.20-3
- Add pkgconfig file to devel subpackage

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Jan Stanek <jstanek@redhat.com> - 0.9.20-1
- Update to 0.9.20

* Wed Jan 04 2017 Jan Stanek <jstanek@redhat.com> - 0.9.19-1
- Update to 0.9.19

* Wed Feb 10 2016 Jan Stanek <jstanek@redhat.com> - 0.9.18-1
- Update to 0.9.18

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.17-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 28 2015 Jan Vcelak <jvcelak@fedoraproject.org> 0.9.17-2
- Make liblmdb.so a symbolic link to (not a copy of) the versioned DSO

* Thu Dec 03 2015 Jan Staněk <jstanek@redhat.com> - 0.9.17-1
- Update to 0.9.17

* Wed Nov 25 2015 Jan Staněk <jstanek@redhat.com> - 0.9.16-2
- Return the name 'Symas' into description

* Fri Aug 14 2015 Jan Staněk <jstanek@redhat.com> - 0.9.16-1
- Updated to 0.9.16

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.14-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Dec 11 2014 Jan Staněk <jstanek@redhat.com> - 0.9.14-1
- Updated to 0.9.14

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jul 18 2014 Jan Stanek <jstanek@redhat.com> - 0.9.13-1
- Updated to 0.9.13

* Mon Jul 14 2014 Jan Stanek <jstanek@redhat.com> - 0.9.11-4
- Changed install instruction to be compatible with older coreutils (#1119084)

* Thu Jun 26 2014 Jan Stanek <jstanek@redhat.com> - 0.9.11-3
- Added delay in testing which was needed on s390* arches (#1104232)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 27 2014 Jan Stanek <jstanek@redhat.com> - 0.9.11-1
- Initial Package
