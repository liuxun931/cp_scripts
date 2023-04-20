#!/opt/CPsuite-R81.10/fw1/Python/bin/python3
# -*- coding: UTF-8 -*-

'''
//
// (c) Copyright 1993-2013 Check Point Software Technologies Ltd.
// All rights reserved.
//
// This is proprietary information of Check Point Software Technologies
// Ltd., which is provided for informational purposes only and for use
// solely in conjunction with the authorized use of Check Point Software
// Technologies Ltd. products.  The viewing and use of this information is
// subject, to the extent appropriate, to the terms and conditions of the
// license agreement that authorizes the use of the relevant product.
//
'''

## not allowed to publish as SK document ##

import os
import threading

# part1 list connection table in readable decimal

conn_list = os.popen('fw tab -t 8158 -u | awk -F\'<\' \'{print $2}\' | awk -F\'>\' \'{print $1}\'| awk -F\';\' \'{print $1}\'').read().split('\n')

def hex_to_dec(hex_ip):
    ip = ''
    p1 = int(hex_ip[0:2], 16)
    p2 = int(hex_ip[2:4], 16)
    p3 = int(hex_ip[4:6], 16)
    p4 = int(hex_ip[6:8], 16)
    ip = ('%d' %p1) + '.' + ('%d' %p2) + '.' + ('%d' %p3) + '.' + ('%d' %p4)
    return ip


## save connections table to a local txt file, in order to check connections before clean. ##
print("Saving connections to local file : connection_tab_before_drop.txt")
os.system("touch ./connection_tab_before_drop.txt;")
f = open("connection_tab_before_drop.txt", "w")

for conn in conn_list:
    if conn != '':
        factor_list = conn.split(',')
        direction = factor_list[0]
        s_ip =      factor_list[1].strip()
        s_port =    factor_list[2]
        d_ip =      factor_list[3].strip()
        d_port =    factor_list[4]
        tcp_ptcl =  factor_list[5]
        new_conn = ('%s, %s, %s, %s, %s, %s' %(int(direction), hex_to_dec(s_ip), int(s_port, 16), hex_to_dec(d_ip), int(d_port,16), int(tcp_ptcl)))
        #print(new_conn)
        f.write(new_conn + '\n')

f.close()
os.system("cat connection_tab_before_drop.txt")



# part2 interact with user

def def_factor():
    factor = '0'
    value = '0'
    while (factor not in ['1', '2', '3', '4', '5']):
        try:
            factor = input("\n Selected connections will be removed on both inbound and outbound directions; \n Select & drop connection by factor : \n 1. source ip \n 2. source port \n 3. destination ip \n 4. destination port \n 5. IP pocotol number \n If you are managing a cluster, please run this script on same member together. \n")
        except Exception as e : 
            print("Please set factor number in range 1-5.")
        else:
            print("factor = %s" %factor)

 # set value for factor:
    if factor == '1':
        value = input("Please input source IP address, one IP for each time to drop (xxx.xxx.xxx.xxx) :")
        print("Source IP addresss : %s " %value)
    if factor == '2':
        value = input("Please input source IP port (1-65535) :  ")
        print("IP source port : %s " %value)
    if factor == '3':
       value = input("Please input destination IP address, one IP for each time to drop : xxx.xxx.xxx.xxx ")
       print("Destination IP addresss : %s " %value)
    if factor == '4':
       value = input("Please input destination IP port (1-65535) :  ")
       print("IP destination port : %s " %value)
    if factor == '5':
       value = input("Please input IP potocol number(0-256), such as TCP=6, EGP=8, IGP=9, UDP=17, RDP=27, OSPF=89 : ")
       print("IP pocotol number : %s " %value)
       return(factor, value)
    return factor, value

f,v = def_factor()

def value_clean(f, v):
    not_valid = 1
    while not_valid:
        if f == '1' or f == '3':
            try:
                ip = v.split('.')
                not_valid = 0
                for a in ip:
                    if int(a) > 255 and int(a)<0:
                        print('ip address value is invalid.')
                        not_valid = 1
            except Exception as e : 
                v = input("Please input source IP address, one IP for each time to drop (xxx.xxx.xxx.xxx) :")

        if f == '2' or f =='4':
            try:
                if int(v) <= 65535 and int(v) >0:
                    print('value is valid.')
                    not_valid = 0
            except:
                v = input("Please input destination IP port (1-65535) :")

        if f =='5':
            try:
                if int(v) <= 255 or int(v) >0:
                    print('value is valid.')
                    not_valid = 0
            except Exception as e:
                v = input("Please input IP potocol number(0-256), such as TCP=6, EGP=8, IGP=9, UDP=17, RDP=27, OSPF=89 : ")
 
    return f, v

f,v = value_clean(f,v)

# part3 action to remove connections in table

def hex_ip(v):
    ip=''
    for i in v.split('.'):
        if 'x' in hex(int(i))[-2:]:
            ip = ip + hex(int(i))[-2:].replace('x', '0')
        else:
            ip = ip + hex(int(i))[-2:]
    return ip 



def get_tup_conns(f, v):
    print("conn tuple to drop:")
    direction = '00000000'
    src_ip = '00000000'
    src_port = '00000000' 
    dst_ip = '00000000'
    dst_port = '00000000'
    tcp_ptcl  = '00000000'
    filter = ''
    
    if f in ['1', '3']:
        src_ip = hex_ip(v)
        filter = src_ip
    if f in ['2', '4']:
        v = hex(int(v))[2:]
        for c in range(0,len(v)):
            src_port = src_port[1:]
            src_port = src_port + v[c]
        filter = src_port
        print("filer_port = %s" %src_port) 
    
    if f in ['5']:
        v = hex(int(v))[2:]
        for c in range(0, len(v)):
            tcp_ptcl = tcp_ptcl[1:]
            tcp_ptcl = tcp_ptcl + v[c]
        filter = tcp_ptcl    

    tup_list = os.popen('fw tab -t connections -u | awk -F\'<\' \'{print $2}\' | awk -F\'>\' \'{print $1}\'| awk -F\';\' \'{print $1}\'| grep \'%s\' ' %filter).read().split('\n')
    tup_list.remove('')
    
    print("connections tuple to drop: ")
    for i in tup_list:
        print(i)
    return tup_list    

drop_conn = get_tup_conns(f, v)

def drop_conns(tup):
    print("droping connections:")
    for c in tup:
        cmd = "fw tab -t connections -x -e %s" %c.replace(' ', '')
        print(cmd)
        t = threading.Thread(target=os.system(cmd), args=(''))
        t.start()
	#os.system(cmd)

def main():
    drop_conns(drop_conn)

