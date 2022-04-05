import pyaudio
import socket
import datetime
import ui
import Queue
import ip_giver
from threading import Thread


# user class for easy control over and the users that connect the server
class User(object):

    def __init__(self):
        self.name = ""
        self.socket = None
        self.is_admin = False


# the main server class
class Server(object):

    def __init__(self):
        self.ip = "0.0.0.0"
        self.port = 5000
        self.p = pyaudio.PyAudio()
        self.CHUNK = 512
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 20000
        self.socket = socket.socket()
        self.socket.bind((self.ip, self.port))
        self.message_queue = Queue.Queue()
        self.user_list = []
        self.admin_list = ["roy"]

    # wait for users to connect
    def get_connection(self):
        while True:
            self.socket.listen(5)
            login_client, log_addr = self.socket.accept()
            self.message_queue.put("someone entered to the login screen")
            login = False
            # until the client doesnt log in he cant proceed to join the server
            try:
                while not login:
                    log_msg = login_client.recv(1024)
                    login, user_name = self.authentication(log_msg, login_client)
                    # create a user class and add all of his attributes
                new_user = User()
                new_user.name = user_name
                new_user.socket = login_client
                self.is_admin(new_user)
                self.message_queue.put(user_name + " joined the server " + "his address :" + str(log_addr))
                self.user_list.append(new_user)
                Thread(target=self.session, args=(new_user,)).start()
            except TypeError or socket.error:
                self.message_queue.put("someone left during login")

    # send voice to all the users except the user that send the data
    def send_voice(self, data, sender):
        for user in self.user_list:
            # do not send the voice to the user who sent it
            if user != sender:
                try:
                    user.socket.sendall(data)
                except socket.error:
                    if user in self.user_list:
                        self.user_list.remove(user)

    # send the text to anyone
    def send_text(self, data, sender):
        for user in self.user_list:
            if user != sender:
                try:
                    message = self.create_message(data, sender.name, "1")
                    user.socket.send(message)
                except socket.error:
                    if user in self.user_list:
                        self.user_list.remove(user)

    # main session with a user get his text messages
    def session(self, user):
            while user in self.user_list:
                try:
                    # split the message using the protocol I decided on [msg_type$%data]
                    msg = user.socket.recv(1049)
                    try:
                        msg_type, data = msg.split("$%")
                        # 1 means text
                        if msg_type == "1":
                            # check if its a whisper command
                            if data[:8] == "/whisper":
                                self.whisper(user, data)
                            # check if its a kick command
                            elif data[:5] == "/kick":
                                self.kick_user(data, user)
                            # normal message
                            else:
                                self.send_text(data, user)

                        # 2 means voice
                        elif msg_type == "2":
                            self.send_voice(msg, user)
                    except ValueError:
                        pass
                except socket.error:
                    self.message_queue.put(user.name + " has left the server. ")
                    if user in self.user_list:
                        self.user_list.remove(user)
                        print self.user_list

    # do the authentication between the client and the server
    def authentication(self, login_message, client_socket):
        try:
            # split the message to username password and register/login mode
            login_info = login_message.split("$")
            user_name = login_info[0]
            pass_word = login_info[1]
            reg_mode = login_info[2]
            exist = False
            did_login = False
            inside_server = False
            # if the user is in register mode
            if reg_mode == "1":
                # check if the user name is existing
                with open("data_base.txt", "r") as f:
                    for line in f:
                        user_info = line.split(",")
                        if user_info[0] == user_name:
                            client_socket.send("User name is already taken")
                            exist = True
                            break
                # if the user name doesnt exist register him
                if not exist:
                    with open("data_base.txt", "a") as f:
                        f.write(user_name + "," + pass_word + "\n")
                        client_socket.send("Registered successfully")
            # if the user is in login mode
            elif reg_mode == "0":
                with open("data_base.txt", "r") as f:
                    for line in f:
                        user_info = line.split(",")
                        # find if the user name and password is identical to the client input and he isn't in the server
                        if user_info[0] == user_name and user_info[1][:-1] == pass_word:
                            if not self.in_server(user_info[0]):
                                client_socket.send("Login successfully")
                                did_login = True
                                break
                            else:
                                client_socket.send("user already connected")
                                inside_server = True
                if not did_login and not inside_server:
                    client_socket.send("Wrong username or password")
            return (did_login, user_name)
        except IndexError:
            self.message_queue.put("someone left during login")

    # get current time
    def get_time(self):
        now = datetime.datetime.now()
        return datetime.time(now.hour, now.minute, now.second)

    # check if the user is an admin
    def is_admin(self, user):
        for admin in self.admin_list:
            if user.name == admin:
                user.is_admin = True

    # send a message that only the target and the sender can see
    def whisper(self, sender, message):
        whisper_msg = message.split(" ")
        target_name = whisper_msg[1]
        data = " "
        # create the message
        for msg in whisper_msg[2:]:
            data += msg + " "
        # check that the client didn't whisper himself
        if sender.name == target_name:
            sender.socket.send(self.create_message("you cant whisper yourself", "system", "1"))
        # check if the target is in the server
        elif self.in_server(target_name):
            target = self.get_user(target_name)
            message = self.create_message(data, sender.name, "2")
            message2 = self.create_message(data, target.name, "3")
            self.message_queue.put("[{}]{} whispered to {}: " + data.format(str(self.get_time()), sender, target_name))
            target.socket.send(message)
            sender.socket.send(message2)
        else:
            sender.socket.send("1$%user not online")

    # get the user object using his name
    def get_user(self, name):
        for user in self.user_list:
            if user.name == name:
                return user

    # check if a user in the server
    def in_server(self, name):
        for user in self.user_list:
            if user.name == name:
                return True
        return False

    # get the message and the sender and create a message format
    def create_message(self, data, sender, flg_type):
        time_now = self.get_time()
        # normal message
        if flg_type == "1":
            self.message_queue.put("[{}]{} : " + data.format(str(time_now), sender))
            return ("1$%" + "[{}]{} : " + data).format(str(time_now), sender)
        # whisper
        elif flg_type == "2":
            return ("1$%" + "[{}]{} whispered: " + data).format(str(time_now), sender)
        # to whisper target
        elif flg_type == "3":
            return ("1$%" + "[{}]to {}: " + data).format(str(time_now), sender)
        # kick message wih special flag
        elif flg_type == "4":
            return ("3$%" + "[{}]{} whispered: " + data).format(str(time_now), sender)

    # kick a target user if the user requested the kick is an admin
    def kick_user(self, data, requester):
        # get the target object
        target_name = data.split()[1]
        target = self.get_user(target_name)
        # check if the user tried to kick is an admin
        if requester.is_admin:
            # check if the target user is in the server
            if target in self.user_list:
                target.socket.send(self.create_message("You have been kicked from the server", "system", "4"))
                self.message_queue.put(target_name + " has been kicked from the server")
                self.user_list.remove(target)
                requester.socket.send(self.create_message("User has been kicked from the server", "system", "1"))
            else:
                requester.socket.send(self.create_message("User not connected", "system", "1"))
        else:
            requester.socket.send(self.create_message("You are not an admin!", "system", "1"))


if __name__ == "__main__":
    host_win = ui.server_win()
    host_win.open()
    if host_win.did_host:
        server = Server()
        server_ui = ui.server_console(server)
        ip_giver.MeDaemon(target=server.get_connection, daemon=True).start()
        server_ui.open()
