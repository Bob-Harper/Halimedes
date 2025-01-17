from classes.picrawler import Picrawler
import time
crawler = Picrawler()


def main():
    """
    crawler.move_list.angle = x
    the angle of declared turn is in the movelist class which is INSIDE the picrawlerclass.
    hence crawler, then move_list.  like going to a subfolder.  a subclass, as it were.
    """
    speed= 50

    crawler.move_list.angle = 5  # Tight turn
    crawler.do_action("turn_left_angle", 1, speed)

    time.sleep(2)  # Another delay

    crawler.move_list.angle = 66  # Set another custom angle
    crawler.do_action('turn_right_angle', 1, speed)  # Uses the custom angle for turning

    time.sleep(2)  # Another delay

    crawler.do_action('sit',1,speed) 


if __name__ == "__main__":
    main()
