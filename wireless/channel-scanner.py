from scapy.all import *
import sys
import time
import os
from threading import Thread
import pandas

networks = pandas.DataFrame(columns=["BSSID", "SSID", "dBm_Signal", "Channel", "Crypto"])
# set the index BSSID (MAC address of the AP)
networks.set_index("BSSID", inplace=True)
def print_all():
    while True:
        os.system("clear")
        print(networks)
        time.sleep(0.5)                      
try:
	iface = sys.argv[1]
except:
	print('[!] no iface specified, defaulting to wlan0mon')
	iface = 'wlan0mon'




def switch_channels(iface=iface):
        ch = 1
        while True:
                print(f'changing to channel: {ch}')
                os.system(f'sudo iwconfig {iface} channel {ch}')
                time.sleep(0.5)
                ch = ch % 233 + 1

devices = set()
def PacketHandler(pkt):
        if pkt.haslayer(Dot11Beacon):
                dot11_layer = pkt[Dot11]
                bssid = dot11_layer.addr2
                ssid = pkt[Dot11Elt].info.decode()
                
                try:
                        dbm_signal = pkt.dBm_AntSignal
                except:
                        dbm_signal = 'N/A'
                stats = pkt[Dot11Beacon].network_stats()
                
                channel = stats.get('channel')
                
                crypto = stats.get('crypto')
                networks.loc[bssid] = (ssid, dbm_signal, channel, crypto)
                
                




printer = Thread(target=print_all)
printer.daemon = True
printer.start()

channel_changer = Thread(target=switch_channels)
channel_changer.daemon = True



sniff(iface=iface, prn=PacketHandler)


