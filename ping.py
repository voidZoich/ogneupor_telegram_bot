import csv

from ping3 import ping


def pinger():
    with open('external_data/ping_list.csv', 'r', newline='', encoding="utf-8") as ping_list_file:
        ping_list = csv.reader(ping_list_file)
        for name, ip in ping_list:
            ping_failed = True
            for _ in range(3):
                if ping(ip) is not None:
                    ping_failed = False
                    continue
            if ping_failed:
                yield name
