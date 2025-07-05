%global gitname    ryzen_smu
%global giturl     https://github.com/amkillam/%{gitname}
%global gitcommit  9f9569f889935f7c7294cc32c1467e5a4081701a
%global gitshortcommit %(c=%{gitcommit}; echo ${c:0:7})
%global gitsnapinfo .20250608git%{gitshortcommit}

%if 0%{?fedora}
%global buildforkernels akmod
%global debug_package %{nil}
%endif

Name:     ryzen-smu-kmod
Version:  0.1.6
Release:  0%{?gitsnapinfo}%{?dist}
Summary:  A Linux kernel driver that exposes access to the SMU
License:  GPLv2
URL:      https://github.com/amkillam/ryzen_smu

Source0:  %{giturl}/archive/%{gitcommit}.tar.gz#/%{name}-%{version}-%{gitshortcommit}.tar.gz
%define   SHA256SUM0 79629fd88cdf66776d65c3cdb88a7e9c0d67f51b6eb99a2d317de9511b977e6d

BuildRequires: kmodtool
BuildRequires: make
BuildRequires: gcc

%description
A Linux kernel driver that exposes access to the SMU (System Management Unit) for certain AMD Ryzen Processors

# Define the userspace tools package
%package -n ryzen-smu
Summary: Userspace tools for ryzen-smu kernel module
Provides: ryzen-smu-kmod-common = %{version}
Requires: ryzen-smu-kmod >= %{version}

%description -n ryzen-smu
Userspace tools and utilities for the ryzen-smu kernel module that provide access to the SMU (System Management Unit) for certain AMD Ryzen Processors.

%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%prep
echo "%SHA256SUM0  %SOURCE0" | sha256sum -c -
%autosetup -n %{gitname}-%{gitcommit} -p 1

# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

find . -type f -name '*.c' -exec sed -i "s/#VERSION#/%{version}/" {} \+

for kernel_version  in %{?kernel_versions} ; do
  mkdir -p _kmod_build_${kernel_version%%___*}
  cp -a *.c _kmod_build_${kernel_version%%___*}/
  cp -a *.h _kmod_build_${kernel_version%%___*}/
  cp -a Makefile _kmod_build_${kernel_version%%___*}/
done

%build
# Build kernel modules
for kernel_version  in %{?kernel_versions} ; do
  make V=1 %{?_smp_mflags} -C ${kernel_version##*___} M=${PWD}/_kmod_build_${kernel_version%%___*} VERSION=v%{version} modules
done

# Build userspace tools
make -C userspace

%install
# Install kernel modules
for kernel_version in %{?kernel_versions}; do
 mkdir -p %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
 install -D -m 755 _kmod_build_${kernel_version%%___*}/ryzen_smu.ko %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
 chmod a+x %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/ryzen_smu.ko
done
%{?akmod_install}

# Install userspace tools
mkdir -p %{buildroot}%{_bindir}
mv userspace/monitor_cpu %{buildroot}%{_bindir}/monitor_cpu

# Files for userspace package
%files -n ryzen-smu
%{_bindir}/monitor_cpu
%doc README.md
%license LICENSE

%changelog
* Sun Jun 08 2025 offlinehq
- Initial release
* Sun Jul 05 2025 offlinehq
- Fix version
