from picrawler import Picrawler
from time import sleep

# Define the smaller turn movements
def get_adjust_left_movements(picrawler):
    X_DEFAULT = 45
    X_TURN = 70
    Y_DEFAULT = 45
    Y_START = 0
    Z_UP = -30
    TURN_X1 = 45
    TURN_Y1 = 22.5
    TURN_X0 = -22.5
    TURN_Y0 = -22.5
    z_current = picrawler.move_list.Z_UP

    return [
        [[X_DEFAULT, Y_DEFAULT, z_current], [X_DEFAULT, Y_START, z_current], [X_TURN, Y_START, Z_UP], [X_DEFAULT, Y_DEFAULT, z_current]],
        [[TURN_X1, TURN_Y1, z_current], [TURN_X1, TURN_Y1, z_current], [TURN_X0, TURN_Y0, Z_UP], [TURN_X0, TURN_Y0, z_current]],
        [[TURN_X1, TURN_Y1, z_current], [TURN_X1, TURN_Y1, z_current], [TURN_X0, TURN_Y0, z_current], [TURN_X0, TURN_Y0, z_current]],
        [[TURN_X1, TURN_Y1, z_current], [TURN_X1, TURN_Y1, z_current], [TURN_X0, TURN_Y0, z_current], [TURN_X0, TURN_Y0, Z_UP]],
        [[X_DEFAULT, Y_START, z_current], [X_DEFAULT, Y_DEFAULT, z_current], [X_DEFAULT, Y_DEFAULT, z_current], [X_TURN, Y_START, Z_UP]],
        [[X_DEFAULT, Y_START, z_current], [X_DEFAULT, Y_DEFAULT, z_current], [X_DEFAULT, Y_DEFAULT, z_current], [X_DEFAULT, Y_START, z_current]],
    ]

def get_adjust_right_movements(picrawler):
    X_DEFAULT = 45
    X_TURN = 70
    Y_DEFAULT = 45
    Y_START = 0
    Z_UP = -30
    TURN_X1 = 45
    TURN_Y1 = 22.5
    TURN_X0 = -22.5
    TURN_Y0 = -22.5
    z_current = picrawler.move_list.Z_UP

    return [
        [[X_DEFAULT, Y_DEFAULT, z_current], [X_TURN, Y_START, Z_UP], [X_DEFAULT, Y_START, z_current], [X_DEFAULT, Y_DEFAULT, z_current]],
        [[TURN_X0, TURN_Y0, z_current], [TURN_X0, TURN_Y0, Z_UP], [TURN_X1, TURN_Y1, z_current], [TURN_X1, TURN_X1, z_current]],
        [[TURN_X0, TURN_Y0, z_current], [TURN_X0, TURN_Y0, z_current], [TURN_X1, TURN_Y1, z_current], [TURN_X1, TURN_X1, z_current]],
        [[TURN_X0, TURN_Y0, Z_UP], [TURN_X0, TURN_Y0, z_current], [TURN_X1, TURN_Y1, z_current], [TURN_X1, TURN_X1, z_current]],
        [[X_TURN, Y_START, Z_UP], [X_DEFAULT, Y_DEFAULT, z_current], [X_DEFAULT, Y_DEFAULT, z_current], [X_DEFAULT, Y_START, z_current]],
        [[X_DEFAULT, Y_START, z_current], [X_DEFAULT, Y_DEFAULT, z_current], [X_DEFAULT, Y_DEFAULT, z_current], [X_DEFAULT, Y_START, z_current]],
    ]

def main():
    crawler = Picrawler()
    speed = 80

    while True:
        print("Calling adjust left")
        for step in get_adjust_left_movements(crawler):
            crawler.do_step(step, speed)
        sleep(0.05)

        print("Calling adjust right")
        for step in get_adjust_right_movements(crawler):
            crawler.do_step(step, speed)
        sleep(0.05)

        print("Calling stand")
        crawler.do_step('stand', speed)
        sleep(1)

if __name__ == "__main__":
    main()
