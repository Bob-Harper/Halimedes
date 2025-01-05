from picrawler import Picrawler
from adjust_movements import AdjustMovements
from time import sleep

def main():
    crawler = Picrawler()
    adjuster = AdjustMovements(crawler)
    speed = 80

    while True:
        print("Calling adjust right")
        for step in adjuster.adjust_right():
            crawler.do_step(step, speed)
        sleep(0.05)
        for step in adjuster.adjust_right():
            crawler.do_step(step, speed)
        sleep(0.05)
        for step in adjuster.adjust_right():
            crawler.do_step(step, speed)
        sleep(0.05)
        for step in adjuster.adjust_right():
            crawler.do_step(step, speed)
        sleep(0.05)

        crawler.do_action('turn left',2,speed)
        sleep(0.05)

        print("Calling stand")
        crawler.do_step('stand', speed)
        sleep(1)

if __name__ == "__main__":
    main()
