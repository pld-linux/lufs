#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
%bcond_without	gvfs		# no gnome vfs support
#
# TODO:		- longer descriptions
#		- optional support for: wavfs, cefs, cardfs
#
%define		_rel	5
Summary:	Linux Userland File System - utilities
Summary(pl):	System plików w przestrzeni u¿ytkownika - narzêdzia
Name:		lufs
Version:	0.9.7
Release:	%{_rel}
License:	GPL v2
Group:		Applications/System
Source0:	http://dl.sourceforge.net/lufs/%{name}-%{version}.tar.gz
# Source0-md5:	23f58fe232254a65df6eb4736a81d524
Source1:	%{name}-Makefile
Patch0:		%{name}-fix_install.patch
Patch1:		%{name}-am.patch
Patch2:		%{name}-no_buildtime_ssh.patch
Patch3:		%{name}-CFLAGS.patch
URL:		http://lufs.sourceforge.net/lufs/
%if %{with userspace}
BuildRequires:	autoconf
BuildRequires:	automake
%if %{with gvfs}
BuildRequires:	gnome-libs-devel
BuildRequires:	gnome-vfs-devel
%endif
BuildRequires:	libstdc++-devel
BuildRequires:	libtool
%endif
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.329
%endif
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

%package -n kernel%{_alt_kernel}-fs-lufs
Summary:	Linux Userland File System - kernel module
Summary(pl):	System plików w przestrzeni u¿ytkownika - modu³ j±dra
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel}
Provides:	kernel%{_alt_kernel}-fs(lufs) = %{version}

%description -n kernel%{_alt_kernel}-fs-lufs
Linux Userland File System - kernel module.

%description -n kernel%{_alt_kernel}-fs-lufs -l pl
System plików w przestrzeni u¿ytkownika - modu³ j±dra.

%package -n kernel%{_alt_kernel}-smp-fs-lufs
Summary:	Linux Userland File System - kernel SMP module
Summary(pl):	System plików w przestrzeni u¿ytkownika - modu³ j±dra SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel%{_alt_kernel}-smp}

%description -n kernel%{_alt_kernel}-smp-fs-lufs
Linux Userland File System - kernel SMP module.

%description -n kernel%{_alt_kernel}-smp-fs-lufs -l pl
System plików w przestrzeni u¿ytkownika - modu³ j±dra SMP.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%if %{with userspace}
CPPFLAGS="$CPPFLAGS -I/usr/include/libart-2.0"; export CPPFLAGS
%if %{without gvfs}
sed '/opt_fs=/s/gvfs//' -i configure.in
%endif
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--with-ssh="%{_bindir}/ssh" \
	--disable-kernel-support \
	--enable-shared \
	--enable-wavfs
#	--enable-cefs
#	--enable-cardfs

%{__make}
%endif

%if %{with kernel}
install %{SOURCE1} kernel/Linux/2.6/Makefile
%build_kernel_modules -m lufs -C kernel/Linux/2.6
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%if %{with kernel}
%install_kernel_modules -m kernel/Linux/2.6/lufs -d kernel/fs/lufs
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post	-n kernel%{_alt_kernel}-fs-lufs
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-fs-lufs
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-fs-lufs
%depmod %{_kernel_ver}smp

%postun	-n kernel%{_alt_kernel}-smp-fs-lufs
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc docs/{*.html,*.txt} AUTHORS README THANKS TODO ChangeLog Contributors
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lufsd.conf
%attr(755,root,root) %{_bindir}/auto.sshfs
%attr(755,root,root) %{_bindir}/auto.ftpfs
%attr(755,root,root) %{_bindir}/lufsd
%attr(755,root,root) %{_bindir}/lufsmount
%attr(755,root,root) %{_bindir}/lussh
# These are SUID root...
%attr(4755,root,root) %{_bindir}/lufsmnt
%attr(4755,root,root) %{_bindir}/lufsumount
# lufs dlopens non-versioned libs, *.so symlinks are required
%attr(755,root,root) %{_libdir}/liblufs-ftpfs.so.*.*.*
%attr(755,root,root) %{_libdir}/liblufs-ftpfs.so
%attr(755,root,root) %{_libdir}/liblufs-gnetfs.so.*.*.*
%attr(755,root,root) %{_libdir}/liblufs-gnetfs.so
%if %{with gvfs}
%attr(755,root,root) %{_libdir}/liblufs-gvfs.so.*.*.*
%attr(755,root,root) %{_libdir}/liblufs-gvfs.so
%endif
%attr(755,root,root) %{_libdir}/liblufs-localfs.so.*.*.*
%attr(755,root,root) %{_libdir}/liblufs-localfs.so
%attr(755,root,root) %{_libdir}/liblufs-locasefs.so.*.*.*
%attr(755,root,root) %{_libdir}/liblufs-locasefs.so
%attr(755,root,root) %{_libdir}/liblufs-sshfs.so.*.*.*
%attr(755,root,root) %{_libdir}/liblufs-sshfs.so
%attr(755,root,root) %{_libdir}/liblufs-wavfs.so.*.*.*
%attr(755,root,root) %{_libdir}/liblufs-wavfs.so
%{_mandir}/man1/lufsmount*
%{_mandir}/man1/lufsumount*

%files devel
%defattr(644,root,root,755)
%{_libdir}/liblufs-ftpfs.la
%{_libdir}/liblufs-gnetfs.la
%if %{with gvfs}
%{_libdir}/liblufs-gvfs.la
%endif
%{_libdir}/liblufs-localfs.la
%{_libdir}/liblufs-locasefs.la
%{_libdir}/liblufs-sshfs.la
%{_libdir}/liblufs-wavfs.la
%{_includedir}/lufs
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-fs-lufs
%defattr(644,root,root,755)
%dir /lib/modules/%{_kernel_ver}/kernel/fs/lufs
/lib/modules/%{_kernel_ver}/kernel/fs/lufs/lufs.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-fs-lufs
%defattr(644,root,root,755)
%dir /lib/modules/%{_kernel_ver}smp/kernel/fs/lufs
/lib/modules/%{_kernel_ver}smp/kernel/fs/lufs/lufs.ko*
%endif
%endif
