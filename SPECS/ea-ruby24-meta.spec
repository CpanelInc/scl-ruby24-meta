# Defining the package namespace
%global ns_name ea
%global ns_dir /opt/cpanel

%global _scl_prefix      %{ns_dir}
%global scl_name_prefix  %{ns_name}-
%global scl_name_base    ruby
%global scl_name_version 24
%global scl              %{scl_name_prefix}%{scl_name_base}%{scl_name_version}
%scl_package %scl

# Do not produce empty debuginfo package.
%global debug_package %{nil}

# Support SCL over NFS.
%global nfsmountable 1

# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4586 for more details
%define release_prefix 1

%{!?install_scl: %global install_scl 1}

Summary: Package that installs %scl
Name:    %scl_name
Version: 2.4.7
Release: %{release_prefix}%{?dist}.cpanel
Vendor:  cPanel, Inc.
License: GPLv2+

Source0: README
Source1: LICENSE
%if 0%{?install_scl}
Requires: %{scl_prefix}ruby
%endif
BuildRequires: help2man
BuildRequires: scl-utils-build

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Requires: scl-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%post
scl enable %{scl} 'gem install bundler' || :

%preun

if [ $1 = 0 ]; then
    scl enable %{scl} 'gem uninstall bundler'  || :
fi

%package build
Summary: Package shipping basic build configuration
Requires: scl-utils-build
Requires: %{scl_prefix}scldevel

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl
Provides: scldevel(%{scl_name_base})

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -T -c

cat <<EOF | tee enable
export PATH=%{_bindir}:%{_sbindir}\${PATH:+:\${PATH}}
export LD_LIBRARY_PATH=%{_libdir}:/opt/cpanel/ea-openssl/%{_lib}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export MANPATH=%{_mandir}:\$MANPATH
export PKG_CONFIG_PATH=%{_libdir}/pkgconfig\${PKG_CONFIG_PATH:+:\${PKG_CONFIG_PATH}}
# For SystemTap.
export XDG_DATA_DIRS=%{_datadir}:\${XDG_DATA_DIRS:-/usr/local/share:/usr/share}
EOF

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat > README << EOF
%{expand:%(cat %{SOURCE0})}
EOF

cp %{SOURCE1} .

%build
# Generate a helper script that will be used by help2man.
cat > h2m_help << 'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_help

# Generate the man page from include.h2m and ./h2m_help --help output.
help2man -N --section 7 ./h2m_help -o %{scl_name}.7

%install
%scl_install

install -D -m 644 enable %{buildroot}%{_scl_scripts}/enable

# Some gems install scripts/bnaries into /opt/cpanel/ea-ruby24/root/usr/local/bin
sed -i 's|PATH=|PATH=%{_bindir}/../local/bin:|' %{buildroot}%{_scl_scripts}/enable

cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

# Install generated man page.
mkdir -p %{buildroot}%{_mandir}/man7/
install -p -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/

# Create directory for pkgconfig files, originally provided by pkgconfig
# package, but not for SCL.
mkdir -p %{buildroot}%{_libdir}/pkgconfig

%files

%files runtime
%doc README LICENSE
%scl_files
# Own the manual directories (rhbz#1073458, rhbz#1072319).
%dir %{_mandir}/man7
%dir %{_libdir}/pkgconfig
%{_mandir}/man7/%{scl_name}.*

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Fri Sep 20 2019 Tim Mullin <tim@cpanel.net> - 2.4.7-1
- EA-8663: Update Ruby to 2.4.7

* Tue May 21 2019 Cory McIntire <cory@cpanel.net> - 2.4.6-1
- EA-8466: Update Ruby to 2.4.6

* Wed May 08 2019 Daniel Muey <dan@cpanel.net> - 2.4.4-2
- ZC-5085: Get `bundle` gem (and gems in general) working under `scl`

* Tue Jun 12 2018 Rishwanth Yeddula <rish@cpanel.net> 2.4.4-1
- EA-7221: Update ruby to 2.4.4

* Wed Mar 28 2018 Rishwanth Yeddula <rish@cpanel.net> 2.4.3-2
- EA-7341: Add ea-openssl to the LD_LIBRARY_PATH to ensure ruby
  can find the openssl libs.

* Tue Feb 06 2018 Jacob Perkins <jacob.perkins@cpanel.net> 2.4.3-1
- EA-7221: Update ruby to 2.4.3

* Thu Sep 28 2017 Rishwanth Yeddula <rish@cpanel.net> 2.4.2-1
- EA-6847: Update ruby to 2.4.2

* Mon Apr 3 2017 Rishwanth Yeddula <rish@cpanel.net> 2.4.1-1
- initial packaging
