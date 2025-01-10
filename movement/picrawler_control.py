from classes.ios_controller import SunFounderController
from classes.new_movements import NewMovements
from picrawler import Picrawler
from robot_hat import Pin, Ultrasonic, utils
from vilib import Vilib
import os
from time import sleep, time

utils.reset_mcu()
sleep(0.5)

# IP address
def getIP():
    wlan0 = os.popen("ifconfig wlan0 |awk '/inet/'|awk 'NR==1 {print $2}'").readline().strip('\n')
    eth0 = os.popen("ifconfig eth0 |awk '/inet/'|awk 'NR==1 {print $2}'").readline().strip('\n')

    if wlan0 == '':
        wlan0 = None
    if eth0 == '':
        eth0 = None

    return wlan0, eth0

def main():
    sc = SunFounderController()
    sc.set_name('picrawler-002')
    sc.set_type('Picrawler')
    sc.start()
    crawler = Picrawler([10, 11, 12, 4, 5, 6, 1, 2, 3, 7, 8, 9])
    new_moves = NewMovements(Picrawler)
    sonar = Ultrasonic(Pin("D2"), Pin("D3"))

    wlan0, eth0 = getIP()
    if wlan0 is not None:
        ip = wlan0
    else:
        ip = eth0
    print('ip : %s' % ip)

    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=False, web=True)

    while True:
        # send data
        distance = sonar.read()
        sc.set("D", [0, distance])
        sc.set('video', 'http://' + ip + ':9000/mjpg')

        # get data
        recv = sc.getall()

        i_val = sc.get('I')
        if i_val is not None:
            print("i_val:", i_val)
            crawler.do_action('forward', 2, A_val)

        m_val = sc.get('M')
        if m_val is not None:
            print("m_val:", m_val)
            crawler.do_action('turn left', 2, A_val)

        q_val = sc.get('I')
        if q_val is not None:
            print("q_val:", q_val)
            crawler.do_action('backward', 2, A_val)

        r_val = sc.get('I')
        if r_val is not None:
            print("r_val:", r_val)
            crawler.do_action('turn right', 2, A_val)

        s_val = sc.get('S')
        if s_val is not None:
            print("s_val:", s_val)
            new_moves.sit_down()

        A_val = sc.get('A')
        if A_val is not None:
            print("A_val:", A_val)

        sleep(1)

if __name__ == "__main__":
    main()
