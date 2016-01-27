#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	gearman
Summary:	PHP wrapper to libgearman
Name:		%{php_name}-pecl-%{modname}
Version:	1.1.2
Release:	1
License:	PHP
Group:		Development/Tools
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	fb3bc8df2d017048726d5654459e8433
URL:		http://gearman.org/
BuildRequires:	%{php_name}-devel
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libgearman-devel >= 1.1.0
BuildRequires:	libtool
BuildRequires:	rpmbuild(macros) >= 1.666
Provides:	php(gearman) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This extension uses libgearman library to provide API for
communicating with gearmand, and writing clients and workers

%prep
%setup -qc
mv %{modname}-%{version}/* .

# Upstream often forgets to change this
extver=$(sed -n '/#define PHP_GEARMAN_VERSION/{s/.* "//;s/".*$//;p}' php_gearman.h)
if test "x${extver}" != "x%{version}"; then
	: Error: Upstream version is ${extver}, expecting %{version}.
	exit 1
fi

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php}
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
cp -a examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README CREDITS LICENSE ChangeLog
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
%{_examplesdir}/%{name}-%{version}
