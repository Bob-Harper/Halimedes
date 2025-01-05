from picrawler import Picrawler
from time import sleep

crawler = Picrawler()

## [right front],[left front],[left rear],[right rear]
new_step = [[45, 45, -120], [45, 45, -120], [45, 45, -120], [45, 45, -120]]
stand_step = crawler.move_list['stand'][0]

def taptap():
    tap_front_right = [[45, 45, -44], [45, 45, -30], [45, 45, -30], [45, 45, -30]]
    tap_front_left = [[45, 45, -30], [45, 45, -44], [45, 45, -30], [45, 45, -30]]
    tap_rear_left = [[45, 45, -30], [45, 45, -30], [45, 45, -44], [45, 45, -30]]
    tap_rear_right = [[45, 45, -30], [45, 45, -30], [45, 45, -30], [45, 45, -44]]
    crawler.do_step(tap_front_right, speed=80)
    crawler.do_step(tap_front_left, speed=80)
    crawler.do_step(tap_rear_left, speed=80)
    crawler.do_step(tap_rear_right, speed=80)

def main():
    speed = 80
    while True:
        print(f"stand step: {stand_step}")
        crawler.do_step(stand_step, speed)
        sleep(1)
        print(f"new step: {new_step}")
        crawler.do_step(new_step, speed)
        sleep(1)

        for _ in range(6):
            taptap()


if __name__ == "__main__":
    main()
