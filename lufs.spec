%define		smpstr		%{?_with_smp:-smp}
%define		smp		%{?_with_smp:1}%{!?_with_smp:0}

Summary:	Linux Userland File System
Summary(pl):	System plików w przestrzeni u¿ytkownika
Name:		lufs
Version:	0.9.3
Release:	1
License:	GPL
Group:		Base/Kernel
Source0:	http://ftp1.sourceforge.net/lufs/%{name}-%{version}.tar.gz
Patch0:		%{name}-fix_install.patch
%{!?no_dist_kernel:BuildRequires:	kernel-headers >= 2.4}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Blahblahblah

%description -l pl
Blablabla

%package -n kernel%{smpstr}-fs-lufs
Summary:	FTP File System - kernel module
Summary(pl):	System plików FTP - modu³ j±dra
Release:	%{release}@%{_kernel_ver_str}
Group:		Base/Kernel
Prereq:		/sbin/depmod
Obsoletes:	lufs
Provides:	lufs = %{version}

%description -n kernel%{smpstr}-fs-lufs
FTP File System is a Linux kernel module, enhancing the VFS with FTP
volume mounting capabilities. That is, you can "mount" FTP shared
directories in your very personal file system and take advantage of
local files ops. This package contains ftpfs kernel module.

%description -n kernel%{smpstr}-fs-lufs -l pl
System plików FTP jest modu³em j±dra rozszerzaj±cym VFS o mo¿liwo¶æ
montowania wolumenów FTP. Oznacza to, ¿e mo¿esz podmontowaæ katalogi
FTP do swojego systemu plików i korzystaæ z nich jak z plików
lokalnych. Ten pakiet zawiera modu³ j±dra do ftpfs.

%prep
%setup -q
%patch0 -p1

%build

%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}

%configure \
	--with-kheaders=/usr/src/linux/include

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install DESTDIR=$RPM_BUILD_ROOT

#install -D ftpfs/ftpfs.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/ftpfs.o
#install -D ftpmount/ftpmount $RPM_BUILD_ROOT%{_sbindir}/ftpmount

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{smpstr}-fs-lufs
/sbin/depmod -a

%postun -n kernel%{smpstr}-fs-lufs
/sbin/depmod -a

%files -n kernel%{smpstr}-fs-lufs
%defattr(644,root,root,755)
/lib/modules/*/*/*/*

%files
%defattr(644,root,root,755)
%doc docs/{*.html,*.txt} TODO ChangeLog AUTHORS Contributors README THANKS
%{_mandir}/man1/*
/etc/lufsd.conf

%defattr(755,root,root)

/usr/bin/lufsd
/usr/bin/lussh
/usr/bin/lufsmount

/usr/bin/auto.sshfs
/usr/bin/auto.ftpfs

%{_libdir}/lib*.so.*.*.*

# These are SUID root...

%defattr(4755,root,root)
/usr/bin/lufsmnt
/usr/bin/lufsumount
