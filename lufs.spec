# TODO: build UP+SMP
#	longer descriptions
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
Summary:	Linux Userland File System - utilities
Summary(pl):	System plików w przestrzeni u¿ytkownika - narzêdzia
Name:		lufs
Version:	0.9.7
%define		_rel	1
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
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

#package -n kernel-smp-...
#Summary:	Linux SMP driver for ...
#Summary(pl):	Sterownik dla Linuksa SMP do ...
#Release:	%{_rel}@%{_kernel_ver_str}
#Group:		Base/Kernel
#{?with_dist_kernel:%requires_releq_kernel_smp}
#Requires(post,postun):	/sbin/depmod
#{?with_dist_kernel:Requires(postun):	kernel-smp}

%prep
%setup -q
%patch0 -p1

%build
%if %{with userspace}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--disable-kernel-support \
	--enable-static \
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
cd -
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post	-n kernel-fs-lufs
%depmod %{_kernel_ver}

%postun -n kernel-fs-lufs
%depmod %{_kernel_ver}

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

%files -n kernel-fs-lufs
%defattr(644,root,root,755)
/lib/modules/*/*/*/*
