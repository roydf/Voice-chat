from threading import Thread
import socket

# thread class but with daemon at the init
class MeDaemon(Thread):
    def __init__(self, daemon=False, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.daemon = daemon


# returns host ipv4 address
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP