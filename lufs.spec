#
# Conditional build:
# _without_dist_kernel	- without kernel from distribution
#
# TODO: build UP+SMP
#	longer descriptions
%define		smpstr		%{?_with_smp:-smp}
%define		smp		%{?_with_smp:1}%{!?_with_smp:0}

Summary:	Linux Userland File System - utilities
Summary(pl):	System plików w przestrzeni u¿ytkownika - narzêdzia
Name:		lufs
Version:	0.9.5
Release:	1
License:	GPL
Group:		Base/Kernel
Source0:	http://ftp1.sourceforge.net/lufs/%{name}-%{version}.tar.gz
Patch0:		%{name}-fix_install.patch
BuildRequires:	autoconf
BuildRequires:	automake
%{!?_without_dist_kernel:BuildRequires:	kernel-headers >= 2.4}
BuildRequires:	libtool
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Linux Userland File System - utilities.

%description -l pl
System plików w przestrzeni u¿ytkownika - narzêdzia.

%package devel
Summary:	Linux Userland File System - development files
Summary(pl):	System plików w przestrzeni u¿ytkownika - pliki dla deweloperów
Group:		Development/Libraries

%description devel
Linux Userland File System - development files.

%description devel -l pl
System plików w przestrzeni u¿ytkownika - pliki dla deweloperów.

%package -n kernel%{smpstr}-fs-lufs
Summary:	Linux Userland File System - kernel module
Summary(pl):	System plików w przestrzeni u¿ytkownika - modu³ j±dra
Release:	%{release}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
Provides:	lufs = %{version}
Obsoletes:	lufs

%description -n kernel%{smpstr}-fs-lufs
Linux Userland File System - kernel module.

%description -n kernel%{smpstr}-fs-lufs -l pl
System plików w przestrzeni u¿ytkownika - modu³ j±dra.

%prep
%setup -q
%patch0 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}

%configure \
	--with-kheaders=%{_kernelsrcdir}/include \
	--with-debug \
	--with-kdebug

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post	-n kernel%{smpstr}-fs-lufs
/sbin/depmod -a %{!?_without_dist_kernel:-F /boot/System.map-%{_kernel_ver} }%{_kernel_ver}

%postun -n kernel%{smpstr}-fs-lufs
/sbin/depmod -a %{!?_without_dist_kernel:-F /boot/System.map-%{_kernel_ver} }%{_kernel_ver}

%files
%defattr(644,root,root,755)
%doc docs/{*.html,*.txt} TODO ChangeLog AUTHORS Contributors README THANKS
%attr(755,root,root) %{_bindir}/auto.sshfs
%attr(755,root,root) %{_bindir}/auto.ftpfs
%attr(755,root,root) %{_bindir}/lufsd
%attr(755,root,root) %{_bindir}/lussh
%attr(755,root,root) %{_bindir}/lufsmount
# These are SUID root...
%attr(4755,root,root) %{_bindir}/lufsmnt
%attr(4755,root,root) %{_bindir}/lufsumount
%attr(755,root,root) %{_libdir}/lib*.so.*.*
%config(noreplace) %verify(not size mtime md5) /etc/lufsd.conf
%{_mandir}/man1/*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so
%{_libdir}/lib*.la
%{_includedir}/*

%files -n kernel%{smpstr}-fs-lufs
%defattr(644,root,root,755)
/lib/modules/*/*/*/*
