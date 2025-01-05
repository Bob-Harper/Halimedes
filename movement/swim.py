from picrawler import Picrawler
from time import sleep
from robot_hat import TTS
import socket
import json

tts = TTS()
crawler = Picrawler()
##"[[right front], [left front], [right rear], [left rear]]")


def swimming(speed):
    for i in range(100):
        crawler.do_step([[100-i,i,0],[100-i,i,0],[0,120,-60+i/5],[0,100,-40-i/5]],speed)


def beta(speed):
    crawler.do_action('look up',1,speed)
    sleep(0.5)
    crawler.do_action('look down',1,speed)
    sleep(0.5)
    crawler.do_action('look up',1,speed)
    sleep(0.5)
    crawler.do_action('look down',1,speed)
    sleep(0.5)
    crawler.do_action('look left',1,speed)
    sleep(0.5)
    crawler.do_action('look right',1,speed)
    sleep(2)
    crawler.do_action('wave',2,speed)
    sleep(0.5)
    crawler.do_action('push up',3,speed)
    sleep(0.5)
    crawler.do_action('sit',1,speed)


def send_to_server(text, source, host='192.168.0.101', port=5000):
    data = json.dumps({"source": source, "text": text})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data.encode('utf-8'))
        response = s.recv(1024)
    # Decode the JSON response
    response_data = json.loads(response.decode('utf-8'))
    return response_data["response"]

def speech(spoken_text):
    print("AI LLM Generation Test begin")
    tts.lang("en-US")
    # Send the text to the server and get the response
    response_text = send_to_server(spoken_text, "Hal")  # Specify "Hal" or "Stygia" as the source
    print(f"Response from server: {response_text}")
    # Use TTS to speak the response
    tts.say(response_text)


# main
def main():
    speed = 100
    spoken_text = "I love to swim!"  # This should be the result of speech-to-text processing
    speech(spoken_text)
    swimming(speed)
    swimming(speed)
    swimming(speed)
    sleep(0.05)
    spoken_text = "This is so exciting!  What shall we do next??"  # This should be the result of speech-to-text processing
    speech(spoken_text)
    beta(speed)



if __name__ == "__main__":
    main()
