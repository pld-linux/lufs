#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
# TODO:		- longer descriptions
#		- optional support for: wavfs, cefs, cardfs
#
Summary:	Linux Userland File System - utilities
Summary(pl):	System plików w przestrzeni u¿ytkownika - narzêdzia
Name:		lufs
Version:	0.9.7
%define		_rel	2
Release:	%{_rel}
License:	GPL v2
Group:		Applications/System
Source0:	http://dl.sourceforge.net/lufs/%{name}-%{version}.tar.gz
# Source0-md5:	23f58fe232254a65df6eb4736a81d524
Source1:	%{name}-Makefile
Patch0:		%{name}-fix_install.patch
URL:		http://lufs.sourceforge.net/lufs/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
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

%package -n kernel-fs-lufs
Summary:	Linux Userland File System - kernel module
Summary(pl):	System plików w przestrzeni u¿ytkownika - modu³ j±dra
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel}
Provides:	kernel-fs(lufs) = %{version}

%description -n kernel-fs-lufs
Linux Userland File System - kernel module.

%description -n kernel-fs-lufs -l pl
System plików w przestrzeni u¿ytkownika - modu³ j±dra.

%package -n kernel-smp-fs-lufs
Summary:	Linux Userland File System - kernel SMP module
Summary(pl):	System plików w przestrzeni u¿ytkownika - modu³ j±dra SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel-smp}

%description -n kernel-smp-fs-lufs
Linux Userland File System - kernel SMP module.

%description -n kernel-smp-fs-lufs -l pl
System plików w przestrzeni u¿ytkownika - modu³ j±dra SMP.

%prep
%setup -q
%patch0 -p1

%build
%if %{with userspace}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
export CFLAGS="%{rpmcflags} -fPIC"
export CXXFLAGS="%{rpmcflags} -fPIC"
%configure \
	--disable-kernel-support \
	--enable-shared
#	--enable-wavfs
#	--enable-cefs
#	--enable-cardfs

%{__make} -C filesystems
%{__make} -C lufsd
%{__make} -C util
%endif

%if %{with kernel}
cd kernel/Linux/2.6
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
    if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
	exit 1
    fi
    rm -rf include
    install -d include/{linux,config}
    ln -sf %{_kernelsrcdir}/config-$cfg .config
    ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
    ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
    touch include/config/MARKER

    install %{SOURCE1} Makefile

    %{__make} -C %{_kernelsrcdir} clean \
	RCS_FIND_IGNORE="-name '*.ko' -o" \
	M=$PWD O=$PWD \
	%{?with_verbose:V=1}
    %{__make} -C %{_kernelsrcdir} modules \
	CC="%{__cc}" CPP="%{__cpp}" \
	M=$PWD O=$PWD \
	%{?with_verbose:V=1}

    mv lufs{,-$cfg}.ko
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/fs/lufs
cd kernel/Linux/2.6
install lufs-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/fs/lufs/lufs.ko
%if %{with smp} && %{with dist_kernel}
install lufs-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/fs/lufs/lufs.ko
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post	-n kernel-fs-lufs
%depmod %{_kernel_ver}

%postun	-n kernel-fs-lufs
%depmod %{_kernel_ver}

%post	-n kernel-smp-fs-lufs
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-fs-lufs
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc docs/{*.html,*.txt} AUTHORS README THANKS TODO ChangeLog Contributors
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/lufsd.conf
%attr(755,root,root) %{_bindir}/auto.sshfs
%attr(755,root,root) %{_bindir}/auto.ftpfs
%attr(755,root,root) %{_bindir}/lufsd
%attr(755,root,root) %{_bindir}/lufsmount
%attr(755,root,root) %{_bindir}/lussh
# These are SUID root...
%attr(4755,root,root) %{_bindir}/lufsmnt
%attr(4755,root,root) %{_bindir}/lufsumount
#
%attr(755,root,root) %{_libdir}/liblufs-ftpfs.so.*.*.*
%attr(755,root,root) %{_libdir}/liblufs-gnetfs.so.*.*.*
%attr(755,root,root) %{_libdir}/liblufs-localfs.so.*.*.*
%attr(755,root,root) %{_libdir}/liblufs-locasefs.so.*.*.*
%attr(755,root,root) %{_libdir}/liblufs-sshfs.so.*.*.*
%{_mandir}/man1/lufsmount*
%{_mandir}/man1/lufsumount*

%files devel
%defattr(644,root,root,755)
%{_libdir}/liblufs-ftpfs.la
%attr(755,root,root) %{_libdir}/liblufs-ftpfs.so
%{_libdir}/liblufs-gnetfs.la
%attr(755,root,root) %{_libdir}/liblufs-gnetfs.so
%{_libdir}/liblufs-localfs.la
%attr(755,root,root) %{_libdir}/liblufs-localfs.so
%{_libdir}/liblufs-locasefs.la
%attr(755,root,root) %{_libdir}/liblufs-locasefs.so
%{_libdir}/liblufs-sshfs.la
%attr(755,root,root) %{_libdir}/liblufs-sshfs.so
%{_includedir}/lufs
%endif

%if %{with kernel}
%files -n kernel-fs-lufs
%defattr(644,root,root,755)
%dir /lib/modules/%{_kernel_ver}/kernel/fs/lufs
/lib/modules/%{_kernel_ver}/kernel/fs/lufs/lufs.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-fs-lufs
%defattr(644,root,root,755)
%dir /lib/modules/%{_kernel_ver}smp/kernel/fs/lufs
/lib/modules/%{_kernel_ver}smp/kernel/fs/lufs/lufs.ko*
%endif
%endif
