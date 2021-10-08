%define name scheduler
%define version 0.0.1
%define unmangled_version 0.0.1
%define release 1

Summary: Hardware Test and Inventory Automation API
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: Source Code Corporation
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: UNKNOWN <UNKNOWN>

%description
## scli: Command Line Interface to interact with Scheduler API

```bash
[user@ubuntu]$ scli -h
usage: scli API CLI [-h] {license} ...

positional arguments:
  {license}
    license   manage sum license keys

optional arguments:
  -h, --help  show this help message and exit
```

```bash
[user@ubuntu]$ scli license -h
usage: scli license [-h] [-a | -r RANGE RANGE] serial

positional arguments:
  serial                serial number

optional arguments:
  -h, --help            show this help message and exit
  -a, --all             get license for all system
  -r RANGE RANGE, --range RANGE RANGE
                        range of systems system
```


%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
