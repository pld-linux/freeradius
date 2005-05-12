#
%include	/usr/lib/rpm/macros.perl
# FIXME: won't be good to include these contrib examples?
# Source1:	http://www.ping.de/~fdc/radius/radacct-replay
# Source3:	ftp://ftp.freeradius.org/pub/radius/contrib/radwho.cgi
Summary:	High-performance and highly configurable RADIUS server
Summary(pl):	Szybki i wysoce konfigurowalny serwer RADIUS
Name:		freeradius
Version:	1.0.2
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	ftp://ftp.freeradius.org/pub/radius/%{name}-%{version}.tar.gz
# Source0-md5:	f5dfce4efbb03bbc47ceae08270a875e
Source1:	%{name}.logrotate
Source2:	%{name}.init
Source3:	%{name}.pam
Patch0:		%{name}-autoconf_mysql.patch
Patch1:		%{name}-makefile.patch
Patch2:		%{name}-smbencrypt.patch
Patch3:		%{name}-linking.patch
Patch4:		%{name}-moduledir.patch
Patch5:		%{name}-rundir.patch
Patch6:		%{name}-config.patch
URL:		http://www.freeradius.org/
Provides:	user(radius)
Provides:	group(radius)
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cyrus-sasl-devel
BuildRequires:	gdbm-devel
BuildRequires:	libltdl-devel
BuildRequires:	libtool
BuildRequires:	mysql-devel
BuildRequires:	openldap-devel
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	pam-devel
BuildRequires:	perl-devel
BuildRequires:	postgresql-backend-devel
BuildRequires:	postgresql-devel
BuildRequires:	python
BuildRequires:	python-devel
BuildRequires:	net-snmp-devel
BuildRequires:	unixODBC-devel
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.202
PreReq:		rc-scripts
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/usermod
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
Requires(post,preun):	/sbin/chkconfig
Requires:	libtool
Requires:	perl(DynaLoader) = %(%{__perl} -MDynaLoader -e 'print DynaLoader->VERSION')
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	cistron-radius

%description
The FreeRADIUS Server Project is an attempt to create a
high-performance and highly configurable GPL'd RADIUS server. It is
generally similar to the Livingston 2.0 RADIUS server, but has a lot
more features, and is much more configurable.

%description -l pl
Projekt FreeRadius ma na celu stworzenie szybkiego i wysoce
konfigurowalnego serwera RADIUS na licencji GPL. Ten jest podobny do
Livingston 2.0 RADIUS server ale ma o wiele wi�cej funkcji i posiada
wi�ksze mo�liwo�ci konfigurowania.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

awk 'BEGIN { printit=0; } { if (printit) print $0; } /## end libtool.m4/ { printit=1;}' \
	< aclocal.m4 > acinclude.m4

%build
maindir="$(pwd)"
for d in rlm_attr_rewrite rlm_checkval rlm_counter rlm_dbm \
	rlm_eap/types/rlm_eap_{md5,mschapv2,peap,sim,tls,ttls} \
	rlm_eap rlm_example rlm_ippool rlm_krb5 rlm_ldap rlm_pam rlm_perl rlm_python \
	rlm_radutmp rlm_smb \
	rlm_sql/drivers/rlm_sql_{db2,iodbc,mysql,oracle,postgresql,unixodbc} \
	rlm_sql rlm_sqlcounter rlm_unix rlm_x99_token ; do

	cd src/modules/${d}
	%{__aclocal} -I ${maindir}
	%{__autoconf}
	if [ -f config.h.in ]; then
		%{__autoheader}
	fi
	cd ${maindir}
done
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%configure \
	SNMPGET="/usr/bin/snmpget" \
	SNMPWALK="/usr/bin/snmpwalk" \
	--enable-strict-dependencies \
	--with-logdir=%{_var}/log/freeradius \
	--with-experimental-modules \
	--with-threads \
	--with-thread-pool \
	--with-gnu-ld \
	--with-ltdl-include=%{_includedir}/none \
	--with-ltdl-lib=%{_libdir} \
	--disable-ltdl-install \
	--without-rlm_krb5 \
	--without-rlm_dbm
%{__make} \
	LIBTOOL="`pwd`/libtool --tag=CC"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/raddb,%{_libdir}/%{name}} \
	$RPM_BUILD_ROOT/etc/{logrotate.d,pam.d,rc.d/init.d} \
	$RPM_BUILD_ROOT%{_var}/log/radius

%{__make} install \
	LIBTOOL="`pwd`/libtool --tag=CC" \
	R=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT{%{_mandir}/man8/builddbm.8,%{_sbindir}/rc.radiusd}
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/raddb/{clients,*.pl}

install %{SOURCE1}	$RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install %{SOURCE2}	$RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE3}	$RPM_BUILD_ROOT/etc/pam.d/radius

# remove useless static modules and library
# rlm*.la are used (lt_dlopen)
rm -f $RPM_BUILD_ROOT%{_libdir}/{*.a,libradius.la}
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}/{*.a,libradius.la}

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
if [ -f /var/lock/subsys/%{name} ]; then
	/etc/rc.d/init.d/%{name} restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/%{name} start\" to start %{name} daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/%{name} ]; then
		/etc/rc.d/init.d/%{name} stop 1>&2
	fi
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
%doc src/modules/rlm_sql/drivers/*/*.sql
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_libdir}/*.so
%{_libdir}/*.la
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/*.so
%{_libdir}/%{name}/*.la
%{_datadir}/freeradius

%dir %{_sysconfdir}/raddb
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/raddb/*

%attr(771,root,radius) %dir %{_var}/log/%{name}
%attr(771,root,radius) %dir %{_var}/log/%{name}/radacct
%attr(775,root,radius) %dir /var/run/%{name}

%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/pam.d/*
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/*

%{_mandir}/man?/*
