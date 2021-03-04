from ping3 import ping
import csv


def pinger():
    with open('external_data/ping_list.csv', 'r', newline='', encoding="utf-8") as ping_list_file:
        ping_list = csv.reader(ping_list_file)
        for name, ip in ping_list:
            yield name, ping(ip)
