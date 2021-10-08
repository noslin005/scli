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
