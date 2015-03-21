# FIXME:
# - won't be good to include these contrib examples?
#   Source1:	http://www.ping.de/~fdc/radius/radacct-replay
#   Source3:	ftp://ftp.freeradius.org/pub/radius/contrib/radwho.cgi
#
# Conditional build:
%bcond_with	krb5	# MIT Kerberos instead of heimdal
#
%include	/usr/lib/rpm/macros.perl
Summary:	High-performance and highly configurable RADIUS server
Summary(pl.UTF-8):	Szybki i wysoce konfigurowalny serwer RADIUS
Name:		freeradius
Version:	1.1.8
Release:	1
License:	LGPL v2.1+ (libradius), GPL v2+ (the rest)
Group:		Networking/Daemons/Radius
Source0:	ftp://ftp.freeradius.org/pub/radius/%{name}-%{version}.tar.bz2
# Source0-md5:	d367452a837bbe8d9c8731e21dc43593
Source1:	%{name}.logrotate
Source2:	%{name}.init
Source3:	%{name}.pam
Patch0:		%{name}-makefile.patch
Patch1:		%{name}-linking.patch
Patch2:		%{name}-moduledir.patch
Patch3:		%{name}-rundir.patch
Patch4:		%{name}-config.patch
Patch5:		%{name}-format.patch
URL:		http://www.freeradius.org/
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake
BuildRequires:	cyrus-sasl-devel
BuildRequires:	gdbm-devel
%{!?with_krb5:BuildRequires:	heimdal-devel}
%{?with_krb5:BuildRequires:	krb5-devel}
BuildRequires:	libcom_err-devel
BuildRequires:	libltdl-devel
BuildRequires:	libtool >= 2:2.2
BuildRequires:	mysql-devel
BuildRequires:	net-snmp-devel
BuildRequires:	openldap-devel >= 2.4.6
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	pam-devel
BuildRequires:	perl-devel
BuildRequires:	postgresql-backend-devel
BuildRequires:	postgresql-devel
BuildRequires:	python
BuildRequires:	python-devel
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	unixODBC-devel
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/usermod
Requires:	perl(DynaLoader) = %(%{__perl} -MDynaLoader -e 'print DynaLoader->VERSION')
Requires:	rc-scripts
Provides:	group(radius)
Provides:	user(radius)
Obsoletes:	cistron-radius
Conflicts:	logrotate < 3.7-4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The FreeRADIUS Server Project is an attempt to create a
high-performance and highly configurable GPL'd RADIUS server. It is
generally similar to the Livingston 2.0 RADIUS server, but has a lot
more features, and is much more configurable.

%description -l pl.UTF-8
Projekt FreeRadius ma na celu stworzenie szybkiego i wysoce
konfigurowalnego serwera RADIUS na licencji GPL. Ten jest podobny do
Livingston 2.0 RADIUS server ale ma o wiele więcej funkcji i posiada
większe możliwości konfigurowania.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%{__sed} -e '/m4_include..libtool/d' < aclocal.m4 > acinclude.m4

%build
maindir="$(pwd)"
for d in rlm_attr_rewrite rlm_checkval rlm_counter rlm_dbm \
	rlm_eap/types/rlm_eap_{md5,mschapv2,peap,sim,tls,ttls} \
	rlm_eap rlm_example rlm_ippool rlm_krb5 rlm_ldap rlm_otp \
	rlm_pam rlm_perl rlm_python rlm_radutmp rlm_smb \
	rlm_sql/drivers/rlm_sql_{db2,iodbc,mysql,oracle,postgresql,unixodbc} \
	rlm_sql rlm_sqlcounter rlm_sql_log rlm_unix ; do

	cd src/modules/${d}
	if [ -f configure.in ]; then
		%{__aclocal} -I ${maindir}
		%{__autoconf}
	fi
	if [ -f config.h.in ]; then
		%{__autoheader}
	fi
	cd ${maindir}
done
%{__libtoolize} --install
%{__aclocal}
%{__autoconf}
%{__autoheader}
%configure \
	SNMPGET="/usr/bin/snmpget" \
	SNMPWALK="/usr/bin/snmpwalk" \
	ac_cv_lib_nsl_inet_ntoa=no \
	ac_cv_lib_resolv_inet_aton=no \
	%{!?with_krb5:--enable-heimdal-krb5} \
	--disable-ltdl-install \
	--enable-strict-dependencies \
	--with-experimental-modules \
	--with-gnu-ld \
	--with-logdir=%{_var}/log/freeradius \
	--with-ltdl-include=%{_includedir}/none \
	--with-ltdl-lib=%{_libdir} \
	--with-rlm_krb5 \
	--with-threads \
	--with-thread-pool
%{__make} -j1 \
	LIBTOOL="`pwd`/libtool --tag=CC"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/raddb,%{_libdir}/%{name}} \
	$RPM_BUILD_ROOT/etc/{logrotate.d,pam.d,rc.d/init.d} \
	$RPM_BUILD_ROOT%{_var}/log/{,archive}/freeradius/radacct

%{__make} -j1 install \
	LIBTOOL="`pwd`/libtool --tag=CC" \
	R=$RPM_BUILD_ROOT

%{__rm} $RPM_BUILD_ROOT%{_sbindir}/rc.radiusd
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/raddb/{clients,*.pl}

install %{SOURCE1}	$RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install %{SOURCE2}	$RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE3}	$RPM_BUILD_ROOT/etc/pam.d/radius

install -d $RPM_BUILD_ROOT%{systemdtmpfilesdir}
cat >$RPM_BUILD_ROOT%{systemdtmpfilesdir}/freeradius.conf <<EOF
d /var/run/freeradius 0775 root radius -
EOF

# remove useless static modules and library
# rlm*.la are used (lt_dlopen)
%{__rm} $RPM_BUILD_ROOT%{_libdir}/{*.a,*.la}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/%{name}/*.a
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/freeradius

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 29 -r -f radius
%useradd -u 29 -d %{_localstatedir} -s /bin/false -M -r -c "%{name}" -g radius radius

# TODO: should be in trigger instead.
# upgrade from previous versions of the package, where radius' gid was "nobody"
if [ "`id -g radius`" = "99" ]; then
	usermod -g 29 radius
	chown radius:radius /var/log/%{name}/*.log >/dev/null 2>&1 || :
	chown radius:radius /var/log/%{name}/radacct/* >/dev/null 2>&1 || :
fi

%post
/sbin/chkconfig --add %{name}
%service %{name} restart "%{name} daemon"

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove radius
	%groupremove radius
fi

%files
%defattr(644,root,root,755)
%doc doc/*
%attr(755,root,root) %{_bindir}/radclient
%attr(755,root,root) %{_bindir}/radeapclient
%attr(755,root,root) %{_bindir}/radlast
%attr(755,root,root) %{_bindir}/radrelay
%attr(755,root,root) %{_bindir}/radsqlrelay
%attr(755,root,root) %{_bindir}/radtest
%attr(755,root,root) %{_bindir}/radwho
%attr(755,root,root) %{_bindir}/radzap
%attr(755,root,root) %{_bindir}/rlm_dbm_cat
%attr(755,root,root) %{_bindir}/rlm_dbm_parser
%attr(755,root,root) %{_bindir}/rlm_ippool_tool
%attr(755,root,root) %{_bindir}/smbencrypt
%attr(755,root,root) %{_sbindir}/check-radiusd-config
%attr(755,root,root) %{_sbindir}/checkrad
%attr(755,root,root) %{_sbindir}/radiusd
%attr(755,root,root) %{_sbindir}/radwatch
%attr(755,root,root) %{_libdir}/libeap-%{version}.so
%attr(755,root,root) %{_libdir}/libeap.so
%attr(755,root,root) %{_libdir}/libradius-%{version}.so
%attr(755,root,root) %{_libdir}/libradius.so
%dir %{_libdir}/freeradius
%attr(755,root,root) %{_libdir}/freeradius/rlm_*.so
%{_libdir}/freeradius/rlm_*.la
%{_datadir}/freeradius

%attr(754,root,root) /etc/rc.d/init.d/freeradius
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/pam.d/radius
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/freeradius
%dir %{_sysconfdir}/raddb
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/acct_users
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/attrs
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/clients.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/dictionary
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/eap.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/experimental.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/hints
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/huntgroups
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/ldap.attrmap
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/mssql.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/naslist
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/naspasswd
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/oraclesql.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/otp.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/postgresql.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/postgresqlippool.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/preproxy_users
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/proxy.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/radiusd.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/realms
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/snmp.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/sql.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/sqlippool.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/users
%dir %{_sysconfdir}/raddb/certs
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/certs/README
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/certs/cert-*
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/certs/dh
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/certs/newcert.pem
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/certs/newreq.pem
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/certs/random
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/certs/root.*
%dir %{_sysconfdir}/raddb/certs/demoCA
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/certs/demoCA/cacert.pem
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/certs/demoCA/index.txt*
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/certs/demoCA/serial*

%attr(771,root,radius) %dir %{_var}/log/freeradius
%attr(771,root,radius) %dir %{_var}/log/freeradius/radacct
%attr(771,root,radius) %dir %{_var}/log/archive/freeradius
%attr(771,root,radius) %dir %{_var}/log/archive/freeradius/radacct
%attr(775,root,radius) %dir /var/run/freeradius
%{systemdtmpfilesdir}/freeradius.conf

%{_mandir}/man1/radclient.1*
%{_mandir}/man1/radeapclient.1*
%{_mandir}/man1/radlast.1*
%{_mandir}/man1/radtest.1*
%{_mandir}/man1/radwho.1*
%{_mandir}/man1/radzap.1*
%{_mandir}/man5/acct_users.5*
%{_mandir}/man5/clients.5*
%{_mandir}/man5/clients.conf.5*
%{_mandir}/man5/dictionary.5*
%{_mandir}/man5/naslist.5*
%{_mandir}/man5/radiusd.conf.5*
%{_mandir}/man5/rlm_*.5*
%{_mandir}/man5/users.5*
%{_mandir}/man8/radiusd.8*
%{_mandir}/man8/radrelay.8*
%{_mandir}/man8/radsqlrelay.8*
%{_mandir}/man8/radwatch.8*
%{_mandir}/man8/rlm_ippool_tool.8*
