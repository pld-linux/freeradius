# FIXME: find a way of getting rid of "-" on versions ... rpm will be happy
Summary:	High-performance and highly configurable RADIUS server
Summary(pl):	Szybki i wysoce konfigurowalny serwer RADIUS
Name:		freeradius
Version:	0.1
Release:	0
License:	GPL
Group:		Networking/Daemons
Group(de):	Netzwerkwesen/Server
Group(pl):	Sieciowe/Serwery
Source0:	ftp://ftp.freeradius.org/pub/radius/%{name}-%{version}.tar.gz
URL:		http://www.freeradius.org/
Prereq:		/sbin/chkconfig
# FIXME: snmpwalk, snmpget and rusers POSSIBLY needed by checkrad
Requires:	libtool
BuildRequires:	libltdl-devel
BuildRequires:	openldap-devel
#someone's help needed:split&test into %{name}-{mysql,pgsql,common,devel,static,ldap,pam?} hunter.
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRequires:	pam-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	cistron-radius

%define         _localstatedir  /var/radius

# FIXME: won't be good to include these contrib examples?
# Source1:	http://www.ping.de/~fdc/radius/radacct-replay
# Source2:	http://www.ping.de/~fdc/radius/radlast-0.03
# Source3:	ftp://ftp.freeradius.org/pub/radius/contrib/radwho.cgi

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

# FIXME: some folks prefer -dist files ... rename them or not?
#cd raddb
#chmod 640 clients naspasswd radiusd.conf.in
#cd ..

%build
#libtoolize --copy --force
#aclocal
#autoconf
#automake -a -c

%configure2_13 --localstatedir=%{_localstatedir} \
	--with-threads \
	--with-thread-pool \
	--with-gnu-ld \
	--disable-ltdl-install
%{__make}

libtool --finish %{_libdir}

%install
# prepare $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/{logrotate.d,pam.d,rc.d/init.d}

# install files
%{__make} install R=$RPM_BUILD_ROOT
# done here & put noreplace in %files to avoid messing up existing installations
for i in radutmp radwtmp  radius.log radwatch.log checkrad.log
do
  touch  $RPM_BUILD_ROOT%{_localstatedir}/log/$i
  echo  $RPM_BUILD_ROOT%{_localstatedir}/log/$i
  #who the hell should own logfiles/ and what sgid should have radiusd ?
# do we need %{_sysconfdir}/shadow do be +r for wheel ? or better use PAM ?
  # Hunter
done


# remove unneeded stuff
rm -f $RPM_BUILD_ROOT%{_prefix}/{man/man8/builddbm.8,sbin/rc.radiusd}

cd redhat
install -m 555 rc.radiusd-redhat $RPM_BUILD_ROOT/etc/rc.d/init.d/radiusd
install radiusd-logrotate $RPM_BUILD_ROOT/etc/logrotate.d/radiusd
install radiusd-pam       $RPM_BUILD_ROOT/etc/pam.d/radius
cd ..

gzip -9nf doc/ChangeLog doc/README* COPYRIGHT

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add radiusd.init

%preun
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del radiusd.init
fi

%files
%defattr(644,root,root,755)
%doc doc/ChangeLog.gz doc/README*.gz todo COPYRIGHT.gz
%config /etc/pam.d/radius
%config /etc/logrotate.d/radiusd
%config /etc/rc.d/init.d/radiusd
%config %{_sysconfdir}/raddb/*
%{_mandir}/*
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%{_libdir}/*
%dir %{_localstatedir}/log/radacct/
%config(missingok noreplace) %{_localstatedir}/log/checkrad.log
%config(missingok noreplace) %{_localstatedir}/log/radwatch.log
%config(missingok noreplace) %{_localstatedir}/log/radius.log
%config(missingok noreplace) %{_localstatedir}/log/radwtmp
%config(missingok noreplace) %{_localstatedir}/log/radutmp
