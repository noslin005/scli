#!/usr/bin/env python3

from app.api import API
import sys
import argparse

from concurrent.futures import ThreadPoolExecutor, as_completed

from app.utils import format_fru


API_TOKEN = 'nyUK1dn5ByEiw79r1Q4U1VRx8zyvzAbCneQV0lS7epQAvBJXC8Xr0EioBI54QRhUmCRynpsAan15qgqASDeon0mtFhfuN9NEm5XC'  # noqa


def parse_cli():
    parser = argparse.ArgumentParser('scli')
    subparser = parser.add_subparsers(dest='command')

    license = subparser.add_parser('license',
                                   help='manage sum license keys')
    license.add_argument('serial',
                         help='serial number')
    group = license.add_mutually_exclusive_group()
    group.add_argument('-a', '--all', action="store_true",
                       help='get license for all system')

    group.add_argument('-r', '--range', action="store", nargs=2,
                       help='range of systems system')
    return parser


def print_header():
    print("="*88)
    print(f"{'SERIAL #':<12} {'MAC':<15} {'USER':<8} {'PASSWORD':<14} {'SUM_KEY'}")
    print("~"*88)


def print_data(system_data):
    system_data = sorted(system_data, key=lambda i: i['system_serial'])
    for data in system_data:
        mac = data.get('mac')
        system_id = data.get('system_id')
        fru = format_fru(data.get('system_serial'))
        user = data.get('user')
        password = data.get('password')
        sum_key = data.get('sum_key')
        print(f"{fru:<12} {mac:<15} {user:<8} {password:<14} {sum_key}")


def get_all_threaded(system_serial):
    scheduler = API(auth_token=API_TOKEN)
    systems = scheduler.get_all_system_id(system_serial)
    if not systems:
        return
    threads = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        for nodes in systems:
            serial, system_id = nodes
            threads.append(executor.submit(
                scheduler.get_license_by_system_id, system_id, serial))

        system_data = []
        for task in as_completed(threads):
            data = task.result()
            if isinstance(data, dict):
                print(f"{data.get('system_serial')}: Done")
                system_data.append(data)

        if system_data:
            print_header()
            print_data(system_data)


def get_licenses_from_range(serial, start, end):
    threads = []
    scheduler = API(auth_token=API_TOKEN)
    with ThreadPoolExecutor(max_workers=20) as executor:
        for x in range(start, end):
            sn = f"{serial}-{x}"
            threads.append(executor.submit(
                scheduler.get_license_by_system_serial, sn))

        system_data = []
        for task in as_completed(threads):
            data = task.result()
            if isinstance(data, dict):
                print(f"System {data.get('system_serial')}: Completed")
                system_data.append(data)

        if system_data:
            print_header()
            print_data(system_data)


def main():
    parser = parse_cli()
    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()

    if args.command == 'license':
        system_serial = args.serial
        if args.all:
            get_all_threaded(system_serial)
        elif args.range:
            first = int(args.range[0])
            last = int(args.range[-1]) + 1
            get_licenses_from_range(system_serial, first, last)
        else:
            get_all_threaded(system_serial)


if __name__ == '__main__':
    sys.exit(main())
