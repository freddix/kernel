# LATEST VERSION CHECKER:
# curl -s http://www.kernel.org/kdist/finger_banner

%include	/usr/lib/rpm/macros.perl

%bcond_with	doc		# kernel-doc package
%bcond_with	source		# kernel-source package
%bcond_with	verbose		# verbose build (V=1)

%bcond_with	perf		# performance tool
%bcond_with	uheaders	# sanitised kernel headers

%bcond_with	bfs		# BFS by C.Kolivas
%bcond_with	bfq		# BFQ (Budget Fair Queueing) scheduler
%bcond_with	rt		# build RT kernel
%bcond_with	stats		# enable infrastructure required for bootchart, powertop, etc.

%bcond_without	kernel_build	# skip kernel build (for perf, etc.)

%define		basever		3.7
%define		postver		.9
%define		rel		1

%if %{with perf}
%unglobal	with_kernel_build
%endif

%if %{with uheaders}
%unglobal	with_kernel_build
%endif

%if %{with rt}
%define		alt_kernel	rt%{?with_stats:_stats}
%endif
%if %{with bfs}
%define		alt_kernel	bfs%{?with_stats:_stats}
%endif
%if !%{with rt} && !%{with bfs}
%define		alt_kernel	std%{?with_stats:_stats}
%endif

# kernel release (used in filesystem and eventually in uname -r)
# modules will be looked from /usr/lib/modules/%{kernel_release}
# localversion is just that without version for "> localversion"
%define		localversion	%{rel}
%define		kernel_release	%{version}%{_alt_kernel}-%{localversion}

Summary:	The Linux kernel (the core of the Linux operating system)
Name:		kernel%{_alt_kernel}
Version:	%{basever}%{postver}
Release:	%{rel}
Epoch:		3
License:	GPL v2
Group:		Base/Kernel
Source0:	ftp://www.kernel.org/pub/linux/kernel/v3.x/linux-%{basever}.tar.xz
# Source0-md5:	21223369d682bcf44bcdfe1521095983
%if "%{postver}" != ".0"
Source1:	ftp://www.kernel.org/pub/linux/kernel/v3.x/patch-%{version}.xz
# Source1-md5:	375fa67b3daba9e6040f13a0a29bf543
%endif
#
Source3:	kernel-autoconf.h
Source4:	kernel-config.h
Source6:	kernel-config.awk
Source7:	kernel-module-build.pl
Source8:	kernel-track-config-change.awk
Source10:	kernel.make
# RT
#Source100:	http://www.kernel.org/pub/linux/kernel/projects/rt/3.6/patch-3.6.10-rt22.patch.xz
# Source100-md5:	7dc95a7cf92335b9a2ed12208b9a1b15
#
# patches
Patch0:		kernel-modpost.patch
# based on http://livenet.selfip.com/ftp/debian/overlayfs/
Patch1:		kernel-overlayfs.patch
# http://algo.ing.unimo.it/people/paolo/disk_sched/patches/
Patch100:	0001-block-cgroups-kconfig-build-bits-for-BFQ-v5r1-3.7.patch
Patch101:	0002-block-introduce-the-BFQ-v5r1-I-O-sched-for-3.7.patch
# http://ck.kolivas.org/patches/bfs/3.0/3.7
Patch110:	3.7-sched-bfs-426.patch
#
URL:		http://www.kernel.org/
BuildRequires:	binutils
BuildRequires:	/usr/sbin/depmod
AutoReqProv:	no
%if %{with perf}
BuildRequires:	asciidoc
BuildRequires:	binutils-devel
BuildRequires:	docbook-dtd45-xml
BuildRequires:	elfutils-devel
BuildRequires:	gtk+-devel
BuildRequires:	libunwind-devel
BuildRequires:	newt-devel
BuildRequires:	python-devel
BuildRequires:	rpm-perlprov
BuildRequires:	rpm-pythonprov
BuildRequires:	slang-devel
BuildRequires:	xmlto
%endif
%if %{with kernel_build}
BuildRequires:	inetutils-hostname
BuildRequires:	perl-base
%endif
Requires(post):	coreutils
Requires(post):	kmod
Requires:	coreutils
Requires:	kmod
Provides:	%{name}(vermagic) = %{kernel_release}
Provides:	kernel(ureadahead) = %{kernel_release}
ExclusiveOS:	Linux
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_enable_debug_packages	0
%define		target_arch_dir		x86
%define		defconfig		arch/%{target_arch_dir}/defconfig

# No ELF objects there to strip (skips processing 27k files)
%define		_noautostrip	\\(.*%{_kernelsrcdir}/.*\\|.*/vmlinux.*\\)
%define		_noautochrpath	.*%{_kernelsrcdir}/.*

%define		objdir		%{topdir}/%{targetobj}
%define		srcdir		%{topdir}/linux-%{basever}
%define		targetobj	%{_target_cpu}-gcc-%(%{kgcc} -dumpversion)
%define		topdir		%{_builddir}/%{name}-%{version}

%define		_kernelsrcdir	/usr/src/linux%{_alt_kernel}-%{version}

%define		DepMod		/usr/sbin/depmod
%define		MakeOpts	ARCH=%{_target_base_arch} CC="%{__cc}" HOSTCC="%{__cc}"

%if %{with perf}
%define		_libexecdir	%{_libdir}/perf-core
%endif

%description
This package contains the Linux kernel that is used to boot and run
your system. It contains few device drivers for specific hardware.
Most hardware is instead supported by modules loaded after booting.

%package vmlinux
Summary:	vmlinux - uncompressed kernel image
Group:		Base/Kernel

%description vmlinux
vmlinux - uncompressed kernel image.

%package drm
Summary:	DRM kernel modules
Group:		Base/Kernel
Requires(postun):	%{name} = %{epoch}:%{version}-%{release}
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description drm
DRM kernel modules.

%package pcmcia
Summary:	PCMCIA modules
Group:		Base/Kernel
Requires(postun):	%{name} = %{epoch}:%{version}-%{release}
Requires:	%{name} = %{epoch}:%{version}-%{release}
AutoReqProv:	no

%description pcmcia
PCMCIA modules.

%package sound-alsa
Summary:	ALSA kernel modules
Group:		Base/Kernel
Requires(postun):	%{name} = %{epoch}:%{version}-%{release}
Requires:	%{name} = %{epoch}:%{version}-%{release}
AutoReqProv:	no

%description sound-alsa
ALSA (Advanced Linux Sound Architecture) sound drivers.

%package headers
Summary:	Header files for the Linux kernel
Group:		Development/Building
Provides:	%{name}-headers(netfilter) = %{netfilter_snap}
AutoReqProv:	no

%description headers
These are the C header files for the Linux kernel, which define
structures and constants that are needed when rebuilding the kernel or
building kernel modules.

%package module-build
Summary:	Development files for building kernel modules
Group:		Development/Building
Requires:	%{name}-headers = %{epoch}:%{version}-%{release}
AutoReqProv:	no

%description module-build
Development files from kernel source tree needed to build Linux kernel
modules from external packages.

%package source
Summary:	Kernel source tree
Group:		Development/Building
Requires:	%{name}-module-build = %{epoch}:%{version}-%{release}
AutoReqProv:	no

%description source
This is the source code for the Linux kernel. You can build a custom
kernel that is better tuned to your particular hardware.

%package doc
Summary:	Kernel documentation
Group:		Documentation
AutoReqProv:	no

%description doc
This is the documentation for the Linux kernel, as found in
/usr/src/linux/Documentation directory.

%package -n linux-libc-headers
Summary:	Sanitised kernel headers
Group:		Development
AutoReqProv:	no
Requires(pre):	coreutils
Provides:	alsa-driver-devel
Provides:	glibc-kernel-headers = %{epoch}:%{version}-%{release}

%description -n linux-libc-headers
This package includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs. The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package -n perf
Summary:	Performance analysis tools for Linux
Group:		Applications/System
Requires:	gtk+

%description -n perf
Performance counters for Linux are are a new kernel-based subsystem
that provide a framework for all things performance analysis. It
covers hardware level (CPU/PMU, Performance Monitoring Unit) features
and software features (software counters, tracepoints) as well.

%prep
%setup -qc
ln -s %{SOURCE7} kernel-module-build.pl
ln -s %{SOURCE10} Makefile
cd linux-%{basever}

%if "%{postver}" != ".0"
xz -dc %{SOURCE1} | patch -p1 -s
%endif

%patch0 -p1
%patch1 -p1

%if %{with bfq}
%patch100 -p1
%patch101 -p1
%endif

%if %{with bfs}
%patch110 -p1
%endif

%if %{with rt}
xz -dc %{SOURCE100} | patch -p1 -s
%{__rm} localversion-rt
%endif

# Fix EXTRAVERSION in main Makefile
sed -i 's#EXTRAVERSION =.*#EXTRAVERSION = %{_alt_kernel}#g' Makefile

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' -o -name '.gitignore' ')' -print0 | xargs -0 -r -l512 rm -f

echo "#!/usr/bin/sh" > scripts/depmod.sh

%build
%if %{with perf}
%{__make} -C linux-%{basever}/tools/perf	\
	%{?with_verbose:V=1}			\
	bindir="%{_bindir}"			\
	mandir="%{_mandir}"			\
	perfexecdir="%{_libexecdir}"		\
	DESTDIR=$RPM_BUILD_ROOT
%endif

%if %{with kernel_build}
install -d %{objdir}
cat > %{targetobj}.mk <<'EOF'
# generated by %{name}.spec
KERNELSRC	:= %{_builddir}/%{name}-%{version}/linux-%{basever}
KERNELOUTPUT	:= %{objdir}

SRCARCH		:= %{target_arch_dir}
ARCH		:= %{_target_base_arch}
Q		:= %{!?with_verbose:@}
MAKE_OPTS	:= %{MakeOpts}
DEFCONFIG	:= %{defconfig}
EOF

BuildConfig() {
	cat <<-EOCONFIG > local.config
	LOCALVERSION="-%{localversion}"
	CONFIG_OVERLAYFS_FS=m
%if %{with rt}
	CONFIG_PREEMPT_RT_BASE=y
	CONFIG_HAVE_PREEMPT_LAZY=y
	CONFIG_PREEMPT_LAZY=y
	CONFIG_PREEMPT__LL=n
	CONFIG_PREEMPT_RTB=n
	CONFIG_PREEMPT_RT_FULL=y
%endif
%if %{with bfs}
	CONFIG_SCHED_BFS=y
%endif
%if %{with bfq}
	CONFIG_CGROUP_BFQIO=y
	CONFIG_DEFAULT_BFQ=y
	CONFIG_DEFAULT_CFQ=n
	CONFIG_DEFAULT_IOSCHED="bfq"
	CONFIG_IOSCHED_BFQ=y
%else
	CONFIG_DEFAULT_CFQ=y
	CONFIG_DEFAULT_IOSCHED="cfq"
%endif
%if %{with stats}
	CONFIG_BINARY_PRINTF=y
	CONFIG_BRANCH_PROFILE_NONE=y
	CONFIG_CONTEXT_SWITCH_TRACER=y
	CONFIG_DEBUG_KERNEL=y
	CONFIG_DEBUG_RODATA=y
	CONFIG_ENABLE_DEFAULT_TRACERS=y
	CONFIG_EVENT_POWER_TRACING_DEPRECATED=y
	CONFIG_EVENT_TRACING=y
	CONFIG_FTRACE=y
	CONFIG_HAVE_DEBUG_KMEMLEAK=y
	CONFIG_NOP_TRACER=y
	CONFIG_RING_BUFFER=y
	CONFIG_SCHEDSTATS=y
	CONFIG_SCHED_DEBUG=y
	CONFIG_STACKTRACE=y
	CONFIG_TIMER_STATS=y
	CONFIG_TRACING=y
%else
	CONFIG_DEBUG_KERNEL=n
	CONFIG_BINARY_PRINTF=n
%endif
EOCONFIG

	# prepare kernel-style config file from multiple config files
	%{__awk} -v arch="all %{target_arch_dir} %{_target_base_arch} %{_target_cpu}" -f %{SOURCE6} \
%ifarch %{x8664}
	$RPM_SOURCE_DIR/kernel-x86_64.config \
%endif
%ifarch %{ix86}
	$RPM_SOURCE_DIR/kernel-x86.config \
%endif
	local.config
}

cd %{objdir}
install -d arch/%{target_arch_dir}
BuildConfig > %{defconfig}
ln -sf %{defconfig} .config
cd -

%{__make} \
	TARGETOBJ=%{targetobj} \
	%{?with_verbose:V=1} \
	oldconfig

%{__awk} %{?debug:-v dieOnError=1} -v infile=%{objdir}/%{defconfig} -f %{SOURCE8} %{objdir}/.config

# build kernel
%{__make} \
	TARGETOBJ=%{targetobj} \
	%{?with_verbose:V=1} \
	all
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with perf}
cd linux-%{basever}/tools/perf
%{__make} install			\
	bindir="%{_bindir}"		\
	mandir="%{_mandir}"		\
	perfexecdir="%{_libexecdir}"	\
	DESTDIR=$RPM_BUILD_ROOT

%{__make} install-man			\
	%{?with_verbose:V=1} \
	bindir="%{_bindir}"		\
	mandir="%{_mandir}"		\
	perfexecdir="%{_libexecdir}"	\
	DESTDIR=$RPM_BUILD_ROOT
%endif

%if %{with kernel_build}
%{__make} %{MakeOpts} -j1 %{!?with_verbose:-s} modules_install firmware_install \
	-C %{objdir} \
	%{?with_verbose:V=1} \
	DEPMOD=%{DepMod} \
	INSTALL_MOD_PATH=$RPM_BUILD_ROOT%{_prefix} \
	INSTALL_FW_PATH=$RPM_BUILD_ROOT%{_prefix}/lib/firmware/%{kernel_release} \
	KERNELRELEASE=%{kernel_release}

# depmod.sh is too clever
/usr/sbin/depmod -aeb $RPM_BUILD_ROOT -F %{objdir}/System.map %{kernel_release}

touch $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/modules.dep

install -d $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/misc

# create directories which may be missing, to simplyfy %files
install -d $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/kernel/{arch,sound,mm}

# rpm obeys filelinkto checks for ghosted symlinks, convert to files
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/{build,source}
touch $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/{build,source}

# no point embed content for %ghost files. empty them
for a in \
	dep{,.bin} \
	alias{,.bin} \
	symbols{,.bin} \
	devname	\
	softdep	\
; do
	test -f $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/modules.$a
	> $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/modules.$a
done

# /boot
install -d $RPM_BUILD_ROOT/boot
cp -a %{objdir}/System.map $RPM_BUILD_ROOT/boot/System.map-%{kernel_release}
cp -a %{objdir}/arch/%{target_arch_dir}/boot/bzImage $RPM_BUILD_ROOT/boot/vmlinuz-%{kernel_release}
install %{objdir}/vmlinux $RPM_BUILD_ROOT/boot/vmlinux-%{kernel_release}

# /usr/src/linux
install -d $RPM_BUILD_ROOT%{_kernelsrcdir}/include/generated
# test if we can hardlink -- %{_builddir} and $RPM_BUILD_ROOT on same partition
if cp -al %{srcdir}/COPYING $RPM_BUILD_ROOT/COPYING 2>/dev/null; then
	l=l
	rm -f $RPM_BUILD_ROOT/COPYING
fi

cp -a$l %{srcdir}/* $RPM_BUILD_ROOT%{_kernelsrcdir}
cp -a %{objdir}/Module.symvers $RPM_BUILD_ROOT%{_kernelsrcdir}
cp -aL %{objdir}/.config $RPM_BUILD_ROOT%{_kernelsrcdir}
cp -a %{objdir}/include $RPM_BUILD_ROOT%{_kernelsrcdir}
# copy arch/x86/include/generated
for dir in $(cd %{objdir} && find arch -name generated -type d); do
cp -a %{objdir}/$dir $RPM_BUILD_ROOT%{_kernelsrcdir}/$dir
find $RPM_BUILD_ROOT%{_kernelsrcdir}/$dir -name '.*.cmd' -exec rm "{}" ";"
done

# version.h location changed in 3.7, but a lot of external modules don't know about it
# add a compatibility symlink
ln -s ../generated/uapi/linux/version.h $RPM_BUILD_ROOT%{_kernelsrcdir}/include/linux/version.h

# disable this here, causes a lot of build-time problems and our rpm-build disables it anyway
%{__sed} -i -e 's|\(CONSTIFY_PLUGIN.*:=.*\)|# \1|' $RPM_BUILD_ROOT%{_kernelsrcdir}/Makefile

# collect module-build files and directories
# Usage: kernel-module-build.pl $rpmdir $fileoutdir
fileoutdir=$(pwd)
cd $RPM_BUILD_ROOT%{_kernelsrcdir}
%{__perl} %{topdir}/kernel-module-build.pl %{_kernelsrcdir} $fileoutdir
cd -

%if %{with doc}
# move to %{_docdir} so we wouldn't depend on any kernel package for dirs
install -d $RPM_BUILD_ROOT%{_docdir}
mv $RPM_BUILD_ROOT{%{_kernelsrcdir}/Documentation,%{_docdir}/%{name}-%{version}}

%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/dontdiff
%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/Makefile
%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/*/Makefile
%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/*/*/Makefile
%else
%{__rm} -r $RPM_BUILD_ROOT%{_kernelsrcdir}/Documentation
%endif

%endif

%if %{with uheaders}
%{__make} -C linux-%{basever} headers_install \
	INSTALL_HDR_PATH=$RPM_BUILD_ROOT%{_prefix} \
	ARCH=%{_target_base_arch}

# provided by glibc-headers
rm -rf $RPM_BUILD_ROOT%{_includedir}/scsi
rm -f $RPM_BUILD_ROOT%{_includedir}/{,*/}.*
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
mv -f /boot/vmlinuz{,.old} 2> /dev/null
mv -f /boot/vmlinuz%{_alt_kernel}{,.old} 2> /dev/null
mv -f /boot/System.map{,.old} 2> /dev/null
mv -f /boot/System%{_alt_kernel}.map{,.old} 2> /dev/null
ln -sf vmlinuz-%{kernel_release} /boot/vmlinuz
ln -sf vmlinuz-%{kernel_release} /boot/vmlinuz%{_alt_kernel}
ln -sf System.map-%{kernel_release} /boot/System.map
ln -sf System.map-%{kernel_release} /boot/System.map%{_alt_kernel}

%depmod %{kernel_release}

%post vmlinux
mv -f /boot/vmlinux{,.old} 2> /dev/null
mv -f /boot/vmlinux-%{_alt_kernel}{,.old} 2> /dev/null
ln -sf vmlinux-%{kernel_release} /boot/vmlinux
ln -sf vmlinux-%{kernel_release} /boot/vmlinux-%{_alt_kernel}

%post drm
%depmod %{kernel_release}

%postun drm
%depmod %{kernel_release}

%post pcmcia
%depmod %{kernel_release}

%postun pcmcia
%depmod %{kernel_release}

%post sound-alsa
%depmod %{kernel_release}

%postun sound-alsa
%depmod %{kernel_release}

%post headers
ln -snf %{basename:%{_kernelsrcdir}} %{_prefix}/src/linux%{_alt_kernel}

%postun headers
if [ "$1" = "0" ]; then
	if [ -L %{_prefix}/src/linux%{_alt_kernel} ]; then
		if [ "$(readlink %{_prefix}/src/linux%{_alt_kernel})" = "linux%{_alt_kernel}-%{version}" ]; then
			rm -f %{_prefix}/src/linux%{_alt_kernel}
		fi
	fi
fi

%triggerin module-build -- %{name} = %{epoch}:%{version}-%{release}
ln -sfn %{_kernelsrcdir} %{_prefix}/lib/modules/%{kernel_release}/build
ln -sfn %{_kernelsrcdir} %{_prefix}/lib/modules/%{kernel_release}/source

%triggerun module-build -- %{name} = %{epoch}:%{version}-%{release}
if [ "$1" = 0 ]; then
	rm -f %{_prefix}/lib/modules/%{kernel_release}/{build,source}
fi

%pretrans -n linux-libc-headers
[ ! -L /usr/include/linux ] || rm -f /usr/include/linux
[ ! -L /usr/include/asm ] || rm -f /usr/include/asm
[ ! -L /usr/include/sound ] || rm -f /usr/include/sound

%if %{with kernel_build}
%files
%defattr(644,root,root,755)
/boot/vmlinuz-%{kernel_release}
/boot/System.map-%{kernel_release}
%{_prefix}/lib/firmware/%{kernel_release}

%dir %{_prefix}/lib/modules/%{kernel_release}
%dir %{_prefix}/lib/modules/%{kernel_release}/kernel
%dir %{_prefix}/lib/modules/%{kernel_release}/kernel/sound
%dir %{_prefix}/lib/modules/%{kernel_release}/misc

%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/*/pcmcia
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/ata/pata_pcmcia.ko*
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/bluetooth/*_cs.ko*
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/gpu
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/net/wireless/*_cs.ko*
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/net/wireless/b43
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/net/wireless/hostap/hostap_cs.ko*
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/pcmcia/[!p]*
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/pcmcia/pd6729.ko*
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/usb/host/sl811_cs.ko*

%{_prefix}/lib/modules/%{kernel_release}/kernel/arch
%{_prefix}/lib/modules/%{kernel_release}/kernel/crypto
%{_prefix}/lib/modules/%{kernel_release}/kernel/drivers
%{_prefix}/lib/modules/%{kernel_release}/kernel/fs
%{_prefix}/lib/modules/%{kernel_release}/kernel/kernel
%{_prefix}/lib/modules/%{kernel_release}/kernel/lib
%{_prefix}/lib/modules/%{kernel_release}/kernel/mm
%{_prefix}/lib/modules/%{kernel_release}/kernel/net
%{_prefix}/lib/modules/%{kernel_release}/kernel/security
%{_prefix}/lib/modules/%{kernel_release}/kernel/sound/ac97_bus.ko*
%{_prefix}/lib/modules/%{kernel_release}/kernel/sound/sound*.ko*

# provided by build
%{_prefix}/lib/modules/%{kernel_release}/modules.order
%{_prefix}/lib/modules/%{kernel_release}/modules.builtin*

# rest modules.* are ghost (regenerated by post depmod -a invocation)
%ghost %{_prefix}/lib/modules/%{kernel_release}/modules.alias
%ghost %{_prefix}/lib/modules/%{kernel_release}/modules.alias.bin
%ghost %{_prefix}/lib/modules/%{kernel_release}/modules.dep
%ghost %{_prefix}/lib/modules/%{kernel_release}/modules.dep.bin
%ghost %{_prefix}/lib/modules/%{kernel_release}/modules.devname
%ghost %{_prefix}/lib/modules/%{kernel_release}/modules.softdep
%ghost %{_prefix}/lib/modules/%{kernel_release}/modules.symbols
%ghost %{_prefix}/lib/modules/%{kernel_release}/modules.symbols.bin

# symlinks pointing to kernelsrcdir
%ghost %{_prefix}/lib/modules/%{kernel_release}/build
%ghost %{_prefix}/lib/modules/%{kernel_release}/source

%files vmlinux
%defattr(644,root,root,755)
/boot/vmlinux-%{kernel_release}

%files drm
%defattr(644,root,root,755)
%{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/gpu

%files pcmcia
%defattr(644,root,root,755)
%{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/pcmcia/*ko*
%{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/*/pcmcia
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/pcmcia/pcmcia*ko*
%{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/bluetooth/*_cs.ko*
%{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/ata/pata_pcmcia.ko*
%{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/net/wireless/*_cs.ko*
%{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/net/wireless/b43
%{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/net/wireless/hostap/hostap_cs.ko*
%{_prefix}/lib/modules/%{kernel_release}/kernel/drivers/usb/host/sl811_cs.ko*

%files sound-alsa
%defattr(644,root,root,755)
%{_prefix}/lib/modules/%{kernel_release}/kernel/sound
%exclude %dir %{_prefix}/lib/modules/%{kernel_release}/kernel/sound
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/sound/ac97_bus.ko*
%exclude %{_prefix}/lib/modules/%{kernel_release}/kernel/sound/sound*.ko*

%files headers -f files.headers_exclude_kbuild
%defattr(644,root,root,755)
%dir %{_kernelsrcdir}
%{_kernelsrcdir}/include
%dir %{_kernelsrcdir}/arch
%dir %{_kernelsrcdir}/arch/[!K]*
%{_kernelsrcdir}/arch/*/include
%dir %{_kernelsrcdir}/security
%dir %{_kernelsrcdir}/security/selinux
%{_kernelsrcdir}/security/selinux/include
%{_kernelsrcdir}/.config
%{_kernelsrcdir}/Module.symvers

%files module-build -f files.mb_include_modulebuild_and_dirs
%defattr(644,root,root,755)
%exclude %dir %{_kernelsrcdir}/arch/um
%{_kernelsrcdir}/arch/*/kernel/asm-offsets*
%{_kernelsrcdir}/arch/*/kernel/sigframe*.h
%{_kernelsrcdir}/drivers/lguest/lg.h
%{_kernelsrcdir}/kernel/bounds.c
%dir %{_kernelsrcdir}/scripts
%{_kernelsrcdir}/scripts/Kbuild.include
%{_kernelsrcdir}/scripts/Makefile*
%{_kernelsrcdir}/scripts/basic
%{_kernelsrcdir}/scripts/kconfig
%{_kernelsrcdir}/scripts/mkcompile_h
%{_kernelsrcdir}/scripts/mkmakefile
%{_kernelsrcdir}/scripts/mod
%{_kernelsrcdir}/scripts/module-common.lds
%{_kernelsrcdir}/scripts/setlocalversion
%{_kernelsrcdir}/scripts/*.c
%{_kernelsrcdir}/scripts/*.sh
%dir %{_kernelsrcdir}/scripts/selinux
%{_kernelsrcdir}/scripts/selinux/Makefile
%dir %{_kernelsrcdir}/scripts/selinux/mdp
%{_kernelsrcdir}/scripts/selinux/mdp/Makefile
%{_kernelsrcdir}/scripts/selinux/mdp/*.c
%exclude %dir %{_kernelsrcdir}/security
%exclude %dir %{_kernelsrcdir}/security/selinux

%if %{with doc}
%files doc
%defattr(644,root,root,755)
%dir %{_docdir}/%{name}-%{version}

%{_docdir}/%{name}-%{version}/[!jkz]*
%{_docdir}/%{name}-%{version}/[jkz]*.txt
%{_docdir}/%{name}-%{version}/kbuild
%{_docdir}/%{name}-%{version}/kdump
%{_docdir}/%{name}-%{version}/kvm
%lang(ja) %{_docdir}/%{name}-%{version}/ja_JP
%lang(ko) %{_docdir}/%{name}-%{version}/ko_KR
%lang(zh_CN) %{_docdir}/%{name}-%{version}/zh_CN
%endif

%if %{with source}
%files source -f files.source_exclude_modulebuild_and_dirs
%defattr(644,root,root,755)
%{_kernelsrcdir}/arch/*/[!Mik]*
%{_kernelsrcdir}/arch/*/kernel/[!M]*
%{_kernelsrcdir}/arch/ia64/ia32/[!M]*
%{_kernelsrcdir}/arch/ia64/install.sh
%{_kernelsrcdir}/arch/m68k/ifpsp060/[!M]*
%{_kernelsrcdir}/arch/m68k/ifpsp060/MISC
%{_kernelsrcdir}/arch/m68k/install.sh
%{_kernelsrcdir}/arch/parisc/install.sh
%{_kernelsrcdir}/arch/x86/ia32/[!M]*
%{_kernelsrcdir}/arch/ia64/kvm
%{_kernelsrcdir}/arch/powerpc/kvm
%{_kernelsrcdir}/arch/s390/kvm
%{_kernelsrcdir}/arch/x86/kvm
%exclude %{_kernelsrcdir}/arch/*/kernel/asm-offsets*
%exclude %{_kernelsrcdir}/arch/*/kernel/sigframe*.h
%exclude %{_kernelsrcdir}/drivers/lguest/lg.h
%{_kernelsrcdir}/block
%{_kernelsrcdir}/crypto
%{_kernelsrcdir}/drivers
%{_kernelsrcdir}/firmware
%{_kernelsrcdir}/fs
%{_kernelsrcdir}/init
%{_kernelsrcdir}/ipc
%{_kernelsrcdir}/kernel
%exclude %{_kernelsrcdir}/kernel/bounds.c
%{_kernelsrcdir}/lib
%{_kernelsrcdir}/mm
%{_kernelsrcdir}/net
%{_kernelsrcdir}/virt
%{_kernelsrcdir}/samples
%{_kernelsrcdir}/scripts/*
%exclude %{_kernelsrcdir}/scripts/Kbuild.include
%exclude %{_kernelsrcdir}/scripts/Makefile*
%exclude %{_kernelsrcdir}/scripts/basic
%exclude %{_kernelsrcdir}/scripts/kconfig
%exclude %{_kernelsrcdir}/scripts/mkcompile_h
%exclude %{_kernelsrcdir}/scripts/mkmakefile
%exclude %{_kernelsrcdir}/scripts/mod
%exclude %{_kernelsrcdir}/scripts/module-common.lds
%exclude %{_kernelsrcdir}/scripts/setlocalversion
%exclude %{_kernelsrcdir}/scripts/*.c
%exclude %{_kernelsrcdir}/scripts/*.sh
%exclude %dir %{_kernelsrcdir}/scripts/selinux
%exclude %{_kernelsrcdir}/scripts/selinux/Makefile
%exclude %dir %{_kernelsrcdir}/scripts/selinux/mdp
%exclude %{_kernelsrcdir}/scripts/selinux/mdp/Makefile
%exclude %{_kernelsrcdir}/scripts/selinux/mdp/*.c
%{_kernelsrcdir}/sound
%{_kernelsrcdir}/security
%exclude %{_kernelsrcdir}/security/selinux/include
%{_kernelsrcdir}/tools
%{_kernelsrcdir}/usr
%{_kernelsrcdir}/COPYING
%{_kernelsrcdir}/CREDITS
%{_kernelsrcdir}/MAINTAINERS
%{_kernelsrcdir}/README
%{_kernelsrcdir}/REPORTING-BUGS
%endif

%else

%if %{with perf}
%files -n perf
%defattr(644,root,root,755)
%doc linux-%{basever}/tools/perf/Documentation/examples.txt linux-%{basever}/tools/perf/command-list.txt linux-%{basever}/tools/perf/design.txt
%attr(755,root,root) %{_bindir}/perf
%attr(755,root,root) %{_libexecdir}/perf-archive
%attr(755,root,root) %{_libexecdir}/scripts/perl/bin/*
%attr(755,root,root) %{_libexecdir}/scripts/python/bin/*

%dir %{_libexecdir}
%dir %{_libexecdir}/scripts
%dir %{_libexecdir}/scripts/perl
%dir %{_libexecdir}/scripts/perl/bin
%dir %{_libexecdir}/scripts/python
%dir %{_libexecdir}/scripts/python/bin

%{_libexecdir}/scripts/perl/*.pl
%{_libexecdir}/scripts/perl/Perf-Trace-Util
%{_libexecdir}/scripts/python/*.py
%{_libexecdir}/scripts/python/Perf-Trace-Util

%{_mandir}/man1/perf*.1*
%endif

%if %{with uheaders}
%files -n linux-libc-headers
%defattr(644,root,root,755)
%{_includedir}/asm
%{_includedir}/asm-generic
%{_includedir}/drm
%{_includedir}/linux
%{_includedir}/mtd
%{_includedir}/rdma
%{_includedir}/sound
%{_includedir}/video
%endif

%endif

