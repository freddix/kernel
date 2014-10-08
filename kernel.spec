%include	/usr/lib/rpm/macros.perl

%bcond_with	doc		# kernel-doc package
%bcond_with	source		# kernel-source package
%bcond_with	verbose		# verbose build (V=1)

%bcond_with	perf		# performance tool
%bcond_with	uheaders	# sanitised kernel headers

%bcond_with	rt		# build RT kernel
%bcond_with	srv		# enable infrastructure required for bootchart, powertop, etc.

%bcond_without	kernel_build	# skip kernel build (for perf, etc.)

%define		basever		3.16
%define		postver		.4
%define		rel		1

%if %{with perf}
%unglobal	with_kernel_build
%endif

%if %{with uheaders}
%unglobal	with_kernel_build
%endif

%if %{with rt}
%define		alt_kernel	rt
%endif
%if !%{with rt}
%define		alt_kernel	std
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
# Source0-md5:	5c569ed649a0c9711879f333e90c5386
%if "%{postver}" != ".0"
Source1:	ftp://www.kernel.org/pub/linux/kernel/v3.x/patch-%{version}.xz
# Source1-md5:	38298e5acfdf188e264cc2984e50410c
%endif
#
Source3:	kernel-autoconf.h
Source4:	kernel-config.h
Source6:	kernel-config.awk
Source7:	kernel-module-build.pl
Source8:	kernel-track-config-change.awk
Source10:	kernel.make
# RT
Source100:	http://www.kernel.org/pub/linux/kernel/projects/rt/3.14/patch-3.14.3-rt5.patch.xz
# Source100-md5:	55c20f9971e1104c7e8bd45ed098555e
Patch0:		kernel-modpost.patch
Patch1:		lz4-comp-support.patch
Patch2:		lz4-config-support.patch
URL:		http://www.kernel.org/
BuildRequires:	binutils
BuildRequires:	/usr/sbin/depmod
AutoReqProv:	no
%if %{with perf}
BuildRequires:	asciidoc
BuildRequires:	bc
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

%package kbuild
Summary:	Development files for building kernel modules
Group:		Development/Building
Requires:	gcc
Requires:	make
AutoReqProv:	no

%description kbuild
Development files from kernel source tree needed to build Linux kernel
modules from external packages.

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
# lz4 for squashfs
#%patch1 -p1
#%patch2 -p1

%if %{with rt}
xz -dc %{SOURCE100} | patch -p1 -s
%{__rm} localversion-rt
%endif

# Fix EXTRAVERSION in main Makefile
%{__sed} -i 's#EXTRAVERSION =.*#EXTRAVERSION = %{_alt_kernel}#g' Makefile

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
%if %{with rt}
	CONFIG_RWSEM_GENERIC_SPINLOCK=y
	CONFIG_RWSEM_XCHGADD_ALGORITHM=n
	CONFIG_PREEMPT_RT_BASE=y
	CONFIG_HAVE_PREEMPT_LAZY=y
	CONFIG_PREEMPT_LAZY=y
	CONFIG_PREEMPT__LL=n
	CONFIG_PREEMPT_RTB=n
	CONFIG_PREEMPT_RT_FULL=y
	CONFIG_HWLAT_DETECTOR=m
	CONFIG_GENERIC_TRACER=y
	CONFIG_MISSED_TIMER_OFFSETS_HIST=y
	CONFIG_FTRACE_STARTUP_TEST=n
%else
	CONFIG_RWSEM_XCHGADD_ALGORITHM=y
%endif
	CONFIG_SQUASHFS_LZ4=y
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

# create directories which may be missing, to simplyfy %files
install -d $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/kernel/{arch,sound,mm}

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
cp -aL %{objdir}/.config $RPM_BUILD_ROOT/boot/config-%{kernel_release}

%if %{with doc}
# move to %{_docdir} so we wouldn't depend on any kernel package for dirs
install -d $RPM_BUILD_ROOT%{_docdir}
mv $RPM_BUILD_ROOT{%{_kernelsrcdir}/Documentation,%{_docdir}/%{name}-%{version}}
%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/dontdiff
%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/Makefile
%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/*/Makefile
%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/*/*/Makefile
%endif

# rpm obeys filelinkto checks for ghosted symlinks, convert to files
%{__rm} $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/{build,source}
#touch $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/{build,source}

cd linux-%{basever}
install %{objdir}/.config .

%{__make} \
	%{?with_verbose:V=1} \
	modules_prepare

install -d $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build/{arch/x86/kernel,kernel,include}
install Makefile $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build/Makefile
install kernel/Makefile $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build/kernel/Makefile
install .config $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build/.config

for i in acpi asm-generic config crypto drm generated keys linux math-emu \
	media net pcmcia scsi sound trace uapi video xen;
do
	cp -a include/${i} "$RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build/include"
done

cp -a arch/x86/include $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build/arch/x86
cp arch/x86/Makefile $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build/arch/x86
cp arch/x86/kernel/asm-offsets.s $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build/arch/x86/kernel
cp -a scripts $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build
cp -a %{objdir}/Module.symvers $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build

# clean up
%{__rm} -r $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build/scripts/{ksymoops,package,rt-tester,selinux,tracing}
find $RPM_BUILD_ROOT%{_prefix}/lib/modules/%{kernel_release}/build/scripts -name '*.o' -o -name '*.o.*' -o -name '*.cmd' -type f | xargs rm -f
%endif

%if %{with uheaders}
%{__make} -C linux-%{basever} headers_install \
	INSTALL_HDR_PATH=$RPM_BUILD_ROOT%{_prefix} \
	ARCH=%{_target_base_arch}

# provided by glibc-headers
%{__rm} -r $RPM_BUILD_ROOT%{_includedir}/scsi
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -d /boot/EFI ]; then
    kernel-install add %{kernel_release} /boot/vmlinuz-%{kernel_release}
else
    ln -sf vmlinuz-%{kernel_release} /boot/vmlinuz
    ln -sf vmlinuz-%{kernel_release} /boot/vmlinuz%{_alt_kernel}
    ln -sf System.map-%{kernel_release} /boot/System.map
    ln -sf System.map-%{kernel_release} /boot/System.map%{_alt_kernel}
fi
%depmod %{kernel_release}

%postun
if [ -d /boot/EFI ]; then
    kernel-install remove %{kernel_release} /boot/vmlinuz-%{kernel_release}
fi

%pretrans -n linux-libc-headers
[ ! -L /usr/include/linux ] || rm -f /usr/include/linux
[ ! -L /usr/include/asm ] || rm -f /usr/include/asm
[ ! -L /usr/include/sound ] || rm -f /usr/include/sound

%if %{with kernel_build}
%files
%defattr(644,root,root,755)
/boot/System.map-%{kernel_release}
/boot/config-%{kernel_release}
/boot/vmlinuz-%{kernel_release}
%{_prefix}/lib/firmware/%{kernel_release}

%dir %{_prefix}/lib/modules/%{kernel_release}
%dir %{_prefix}/lib/modules/%{kernel_release}/kernel
%{_prefix}/lib/modules/%{kernel_release}/kernel/arch
%{_prefix}/lib/modules/%{kernel_release}/kernel/crypto
%{_prefix}/lib/modules/%{kernel_release}/kernel/drivers
%{_prefix}/lib/modules/%{kernel_release}/kernel/fs
%{_prefix}/lib/modules/%{kernel_release}/kernel/lib
%{_prefix}/lib/modules/%{kernel_release}/kernel/mm
%{_prefix}/lib/modules/%{kernel_release}/kernel/net
%{_prefix}/lib/modules/%{kernel_release}/kernel/security
%{_prefix}/lib/modules/%{kernel_release}/kernel/sound

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

%files kbuild
%defattr(644,root,root,755)
%dir %{_prefix}/lib/modules/%{kernel_release}/build
%{_prefix}/lib/modules/%{kernel_release}/build/arch
%{_prefix}/lib/modules/%{kernel_release}/build/include
%{_prefix}/lib/modules/%{kernel_release}/build/kernel

%{_prefix}/lib/modules/%{kernel_release}/build/.config
%{_prefix}/lib/modules/%{kernel_release}/build/Makefile
%{_prefix}/lib/modules/%{kernel_release}/build/Module.symvers

# do we really need all that stuff to build an external module?
%dir %{_prefix}/lib/modules/%{kernel_release}/build/scripts
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/Lindent
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/asn1_compiler
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/bin2c
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/bloat-o-meter
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/cleanfile
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/cleanpatch
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/coccicheck
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/config
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/conmakehash
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/decodecode
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/diffconfig
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/extract-ikconfig
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/extract-vmlinux
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/gfp-translate
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/kallsyms
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/kernel-doc
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/makelst
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/mkcompile_h
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/mkmakefile
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/mksysmap
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/mkversion
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/patch-kernel
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/setlocalversion
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/show_delta
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/sign-file
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/sortextable
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/ver_linux
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/*.sh
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/*.c
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/*.h
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/*.lds
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/*.pl
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/*.py
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/Kbuild.include
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/Makefile*

%{_prefix}/lib/modules/%{kernel_release}/build/scripts/dtc
%dir %{_prefix}/lib/modules/%{kernel_release}/build/scripts/basic
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/basic/fixdep
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/basic/Makefile
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/basic/*.c

%dir %{_prefix}/lib/modules/%{kernel_release}/build/scripts/mod
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/mod/mk_elfconfig
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/mod/modpost
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/mod/Makefile
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/mod/*.c
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/mod/*.h
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/mod/*.s

%dir %{_prefix}/lib/modules/%{kernel_release}/build/scripts/coccinelle
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/coccinelle/locks
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/coccinelle/iterators
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/coccinelle/free
%dir %{_prefix}/lib/modules/%{kernel_release}/build/scripts/coccinelle/api
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/coccinelle/api/alloc
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/coccinelle/api/*.cocci
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/coccinelle/misc
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/coccinelle/null
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/coccinelle/tests
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/genksyms

%dir %{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/conf
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/*.sh
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/*.c
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/*.c_shipped
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/*.cc
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/*.glade
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/*.gperf
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/*.h
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/*.in
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/*.l
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/*.pl
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/*.y
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/Makefile

%dir %{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/lxdialog
%attr(755,root,root) %{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/lxdialog/*.sh
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/lxdialog/*.c
%{_prefix}/lib/modules/%{kernel_release}/build/scripts/kconfig/lxdialog/*.h

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

