import argparse
import sys
import threading
import time
import time

from client import Client



def cmdline_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("host", type=str, help="Server host")
    p.add_argument("port", type=int, help="Server port")
    p.add_argument("-c", "--clients", type=int, default=12, help="Number of clients")

    return p.parse_args()


if __name__ == '__main__':
    args = cmdline_args()
    print("Stop clients app with CTRL+C when you heed, app will hang even when all connections will be closed.")

    try:
        for i in range(args.clients):
            c = Client(f'Volosozhar_{i}', args.host, args.port)
            client_thread = threading.Thread(target=c.connect)
            client_thread.daemon = True
            client_thread.start()
            time.sleep(0.2)

        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

