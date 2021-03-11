import time
import datetime

def main():
    while True:
        time.sleep(5)
        print(f"[{datetime.datetime.now().isoformat()}] Running")
        

if __name__ == "__main__":
    main()
