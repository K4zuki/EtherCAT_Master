#import gevent.monkey
#gevent.monkey.patch_socket()
from pyEtherCAT import MasterEtherCAT
import time
import os
import psutil



#============================================================================#
# C95用の簡易EtherCATパッケージです。
# 本来は細かいパケットに付いて理解を深めた上で仕組みを構築していきますが、
# 説明も実験も追いつかず、ひとまずGPIOで高速にON/OFF出来る部分だけを纏めました。
# 動作は Linux(RaspberryPi含む) にて Python3　で動作します。
# sudo python3 test03.py
#============================================================================#
# ここから簡易ライブラリ
#============================================================================#
def EtherCAT_Init():
    cat = MasterEtherCAT.MasterEtherCAT("enp0s25")  #ネットワークカードのアドレスを記載
    
    return cat
def EtherCAT_SetUp(cat):
    cat.EEPROM_SetUp(cat.ADP) # EEPROMの設定、特に変更不要
    cat.EEPROM_Stasus(enable=0x00,command=0x04) # EEPROMの設定、特に変更不要
    ADDR = 0x0120 # AL 制御レジスタ
    data = 0x0002 # 2h: 動作前ステートを要求する
    cat.APWR(IDX=0x00,ADP=cat.ADP,ADO=ADDR,DATA=[data&0xFF,(data>>8)&0xFF])
    (DATA,WKC) = cat.socket_read()
    print("[0x{:04x}]= 0x{:04x}".format(ADDR,DATA[0]|DATA[1]<<8))
    ADDR = 0x0120 # AL 制御レジスタ
    data = 0x0002 # 2h: 動作前ステートを要求する
    cat.APWR(IDX=0x00,ADP=cat.ADP,ADO=ADDR,DATA=[data&0xFF,(data>>8)&0xFF])
    (DATA,WKC) = cat.socket_read()
    print("[0x{:04x}]= 0x{:04x}".format(ADDR,DATA[0]|DATA[1]<<8))
    ADDR = 0x0120 # AL 制御レジスタ
    data = 0x0004 # 4h: 安全動作ステートを要求する
    cat.APWR(IDX=0x00,ADP=cat.ADP,ADO=ADDR,DATA=[data&0xFF,(data>>8)&0xFF])
    (DATA,WKC) = cat.socket_read()
    print("[0x{:04x}]= 0x{:04x}".format(ADDR,DATA[0]|DATA[1]<<8))
    ADDR = 0x0120 # AL 制御レジスタ
    data = 0x0008 # 8h: 動作ステートを要求する
    cat.APWR(IDX=0x00,ADP=cat.ADP,ADO=ADDR,DATA=[data&0xFF,(data>>8)&0xFF])
    (DATA,WKC) = cat.socket_read()
    print("[0x{:04x}]= 0x{:04x}".format(ADDR,DATA[0]|DATA[1]<<8))
def EtherCAT_GPIOMode(cat,data):
    ADDR = 0x0F00 # デジタル I/O 出力データレジスタ
    #data = 0x00FF # 出力データ
    cat.APWR(IDX=0x00,ADP=cat.ADP,ADO=ADDR,DATA=[data&0xFF,(data>>8)&0xFF])
    (DATA,WKC) = cat.socket_read()
    print("[0x{:04x}]= 0x{:04x}".format(ADDR,DATA[0]|DATA[1]<<8))
def EtherCAT_GPIO_Out(cat,data):
    ADDR = 0x0F10
    cat.APWR(IDX=0x00,ADP=cat.ADP,ADO=ADDR,DATA=[data&0xFF,(data>>8)&0xFF])
    #(DATA,WKC) = cat.socket_read()
#============================================================================#
# ここまで　簡易ライブラリ
#============================================================================#



cat = EtherCAT_Init()    # EtherCATのネットワーク初期設定

#-- EtherCATのステートマシンを実行に移す処理
cat.ADP = 0x0000
EtherCAT_SetUp(cat)         # EtherCATスレーブの初期設定
EtherCAT_GPIOMode(cat,0xFFFF)         # EtherCATスレーブのGPIO方向設定　0:入力 1:出力
cat.ADP = 0x0000

import signal
import time

flag = 0
CNT = 0
STEP = 0
DATA = [0x01,0x00,0x00,0x01]
def RUN(arg1, arg2):
    global flag
    global CNT
    global STEP
    #print(time.time())
    #print(flag)
    if  (STEP == 0):
        EtherCAT_GPIO_Out(cat,DATA[0])
        STEP = STEP +1
    elif(STEP == 1):
        EtherCAT_GPIO_Out(cat,DATA[1])
        STEP = STEP +1
    elif(STEP == 2):
        EtherCAT_GPIO_Out(cat,DATA[2])
        STEP = STEP +1
    elif(STEP == 3):
        EtherCAT_GPIO_Out(cat,DATA[3])
        STEP =0
    else:
        EtherCAT_GPIO_Out(cat,0x0000)
        flag =1
        CNT = CNT+1

Hz = 8
TIME = 1.0/Hz
signal.signal(signal.SIGALRM, RUN)
signal.setitimer(signal.ITIMER_REAL,TIME/2, TIME/2)
while 1:
    pass

while True:
    #Hz = Hz+1
    #TIME = 1.0/Hz    
    #signal.signal(signal.SIGALRM, RUN)
    #signal.setitimer(signal.ITIMER_REAL,TIME/2, TIME/2)
    time.sleep(1)

try:
    while 1:
        #time.sleep(TIME)
        cat.ADP = 0x0000 -0
        EtherCAT_GPIO_Out(cat,0xFFFF);
        time.sleep(TIME)
        #for i in range(16):
            #time.sleep(TIME)
            #EtherCAT_GPIO_Out(cat,0x0001<<i);
        #for i in range(3):
        EtherCAT_GPIO_Out(cat,0x0000);
        time.sleep(TIME)
            #EtherCAT_GPIO_Out(cat,0x0000);

        #for i in range(0xFFFF):
        #    EtherCAT_GPIO_Out(cat,i);
except KeyboardInterrupt:
    EtherCAT_GPIO_Out(cat,0x0000);
    print("")
    print("End.")
