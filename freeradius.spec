%include        /usr/lib/rpm/macros.python
%include        /usr/lib/rpm/macros.perl
# FIXME: won't be good to include these contrib examples?
# Source1:	http://www.ping.de/~fdc/radius/radacct-replay
# Source2:	http://www.ping.de/~fdc/radius/radlast-0.03
# Source3:	ftp://ftp.freeradius.org/pub/radius/contrib/radwho.cgi
Summary:	High-performance and highly configurable RADIUS server
Summary(pl):	Szybki i wysoce konfigurowalny serwer RADIUS
Name:		freeradius
Version:	0.7
Release:	0
License:	GPL
Group:		Networking/Daemons
Source0:	ftp://ftp.freeradius.org/pub/radius/%{name}-%{version}.tar.gz
# Source0-md5:	04e4026a1f4bb08e8db20a16d9834b71
Source1:	%{name}.logrotate
Source2:	%{name}.init
Source3:	%{name}.pam
URL:		http://www.freeradius.org/
BuildRequires:	gdbm-devel
BuildRequires:	libltdl-devel
BuildRequires:	mysql-devel
BuildRequires:	openldap-devel
BuildRequires:	openssl-devel >= 0.9.7
BuildRequires:	pam-devel
BuildRequires:	perl-devel
BuildRequires:	postgresql-backend-devel
BuildRequires:	postgresql-devel
BuildRequires:	python-devel
BuildRequires:	ucd-snmp-devel
BuildRequires:	ucd-snmp-utils
BuildRequires:	unixODBC-devel
BuildRequires:	rpm-perlprov
BuildRequires:	rpm-pythonprov
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
Requires:	libtool
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	cistron-radius

%define         _localstatedir  %{_var}/lib/freeradius

%description
The FreeRADIUS Server Project is an attempt to create a
high-performance and highly configurable GPL'd RADIUS server. It is
generally similar to the Livingston 2.0 RADIUS server, but has a lot
more features, and is much more configurable.

%description -l pl
Projekt FreeRadius ma na celu stworzenie szybkiego i wysoce
konfigurowalnego serwera RADIUS na licencji GPL. Ten jest podobny do
Livingston 2.0 RADIUS server ale ma o wiele wiêcej ficzersów i jest
bardziej podatny na konfiguracjê.

%prep
%setup -q

%build
touch src/modules/rlm_eap/types/rlm_eap_tls/config.h

%configure2_13 \
	--with-system-libtool \
	--enable-strict-dependencies \
	--with-logdir=%{_var}/log/freeradius \
	--with-experimental-modules \
	--with-threads \
	--with-thread-pool \
	--with-gnu-ld \
	--with-ltdl-include=%{_includedir}/none \
	--with-ltdl-lib=%{_libdir} \
	--disable-ltdl-install \
	--without-rlm_krb5
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/raddb \
	$RPM_BUILD_ROOT/etc/{logrotate.d,pam.d,rc.d/init.d} \
	$RPM_BUILD_ROOT%{_var}/log/radius

%{__make} install \
	R=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT{%{_mandir}/man8/builddbm.8,%{_sbindir}/rc.radiusd}
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/raddb/{clients,*.pl}

install %{SOURCE1}	$RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install %{SOURCE2}	$RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE3}	$RPM_BUILD_ROOT/etc/pam.d/radius

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`id -u radius 2>/dev/null`" ]; then
        if [ "`id -u radius`" != "29" ]; then
                echo "Error: user radius doesn't have uid=29. Correct this before installing radius server." 1>&2
                exit 1
        fi
else
        /usr/sbin/useradd -u 29 -d %{_localstatedir} -s /bin/false -M -r -c "%{name}" -g nobody radius 1>&2
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
        /usr/sbin/userdel %{name}
fi

%files
%defattr(644,root,root,755)
%doc doc/*
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_libdir}/*.so
%{_libdir}/*.la

%dir %{_sysconfdir}/raddb
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/raddb/*

%dir %{_var}/log/%{name}
%dir %{_var}/log/%{name}/radacct

%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 size mtime) /etc/pam.d/*
%attr(640,root,root) %config(noreplace) /etc/logrotate.d/*

%{_mandir}/man?/*
