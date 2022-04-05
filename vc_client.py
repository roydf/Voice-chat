import pyaudio
import socket
from threading import Thread
import Queue
import ip_giver


# the client object
class Client(object):

    # the init of the client object create the session with the server with 2 sockets one for voice and one for text
    def __init__(self, ip, socket):
        self.ip = ip
        self.port = 5000
        self.p = pyaudio.PyAudio()
        self.CHUNK = 512
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 20000
        self.socket = socket
        self.connected = True
        self.voice_data = ""
        self.chat_data = ""
        self.message_queue = Queue.Queue()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  output=True,
                                  frames_per_buffer=self.CHUNK)
        ip_giver.MeDaemon(target=self.send_voice, daemon=True).start()
        Thread(target=self.session).start()
        ip_giver.MeDaemon(target=self.play_voice, daemon=True).start()
        ip_giver.MeDaemon(target=self.read_it, daemon=True).start()

    # the write voice function
    def send_voice(self):
        input_stream = self.p.open(format=self.FORMAT,
                                   channels=self.CHANNELS,
                                   rate=self.RATE,
                                   input=True,
                                   frames_per_buffer=self.CHUNK)
        while self.connected:
            try:
                data = "2$%" + input_stream.read(self.CHUNK)
                try:
                    self.socket.send(data)
                except socket.error:
                    print "you got disconnected"
                    self.close()
            except IOError:
                print "stream closed"
        input_stream.stop_stream()
        input_stream.close()

    # the read voice function
    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()

    def play_voice(self):
        while self.connected:
            if self.voice_data != "":
                self.stream.write(self.voice_data)
                self.voice_data = ""

    # read function of text
    def read_it(self):
        while self.connected:
            try:
                # get the message and try split it using the protocol I decided to use in the server [type$%data]
                msg = self.socket.recv(1049)
                try:
                    msg_type, data = msg.split("$%")
                except ValueError:
                    # if its not in the protocol ignore it
                    continue
                # 1 means its a text
                if msg_type == "1":
                    self.message_queue.put(data)
                # 2 means its a voice
                elif msg_type == "2":
                    self.voice_data = data
                # 3 means special messages from the server
                if msg_type == "3":
                    if "You have been kicked from the server" in data:
                        # if you got a system message you got kicked close the client
                        self.message_queue.put(data)
                        self.close()
            except socket.error:
                print "you got disconnected"
                self.close()

    # write function of text
    def write_it(self, message_input):
        msg = "1$%" + message_input
        # check if you tried use whisper command right
        if message_input[:8] == "/whisper":
            if len(message_input.split(" ")) > 2:
                self.socket.send(msg)
            else:
                self.message_queue.put("whisper format invalid use this format:/whisper <target name> <message>")
        # check if you tried use kick command
        elif message_input[:5] == "/kick":
            if len(message_input.split(" ")) == 2:
                self.socket.send(msg)
            else:
                self.message_queue.put("kick format invalid use this format:/kick <target name>")
        # else its send a normal message to everyone
        else:
            try:
                self.socket.send(msg)
            except socket.error:
                print "you got disconnected"
                self.close()

    # main thread to run in the background
    def session(self):
        while self.connected:
            pass
        print "s"

    # close everything in a proper way after exiting the code
    def close(self):
        self.connected = False
        self.p.terminate()
        self.socket.close()

if __name__ == "__main__":
    c = Client("127.0.0.1")

