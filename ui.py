from Tkinter import *
import socket
import hashlib
import datetime
import ip_giver


# pop up windows class
class PopUp(Toplevel):

    # pop up window init
    def __init__(self, title, message, button_text):
        Toplevel.__init__(self)
        self.title(title)
        self.mid_height = self.winfo_screenheight()/2
        self.mid_width = self.winfo_screenwidth()/2
        self.geometry("+{}+{}".format(self.mid_width-120, self.mid_height+75))
        self.grab_set()
        self.msg = Label(self, text=message, font=("Comic Sans MS", 8), fg="black")
        self.btn = Button(self, text=button_text, font=("Comic Sans MS", 10), command=self.destroy)
        self.msg.pack()
        self.btn.pack()

    # open the window
    def open(self):
        self.mainloop()


# ui class
class Master(object):

    # ui init
    def __init__(self, ip):

        self.did_connect = False
        self.name = " "
        self.ip = ip
        self.port = 5000
        self.socket = socket.socket()
        self.socket.connect((self.ip, self.port))
        self.root = Tk()
        self.screen_photo = PhotoImage(file="images/login_pic.gif")
        self.icon = "images\icon.ico"
        self.root.iconbitmap(self.icon)
        self.img_label = Label(self.root, image=self.screen_photo)
        self.img_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.mid_height = self.root.winfo_screenheight()/2
        self.mid_width = self.root.winfo_screenwidth()/2
        self.reg_flag = BooleanVar()
        self.reg_flag = FALSE
        self.root.title("Journey-opening")
        self.root.geometry("300x300+{}+{}".format(self.mid_width-150, self.mid_height-150))
        self.root.resizable(width=0, height=0)
        self.cyan = "#0990CB"
        self.username = Entry(self.root, font=("Comic Sans MS", 16), fg="black")
        self.password = Entry(self.root, font=("Comic Sans MS", 16), fg="black", show="*")
        self.user_lbl = Label(self.root, text="", font=("Comic Sans MS", 16), fg=self.cyan, bg=self.cyan)
        self.pass_lbl = Label(self.root, text="", font=("Comic Sans MS", 16), fg=self.cyan, bg=self.cyan)
        self.action_btn = Button(self.root, text="login", font=("Comic Sans MS", 9), width=10
                                          , command=lambda: self.send_user_info(self.username,self. password))
        self. register_ckbx = Checkbutton(self.root, text="register mode", font=("Comic Sans MS", 9)
                                          , variable=self.reg_flag, bg=self.cyan, activebackground=self.cyan
                                          , command=lambda: self.change_btn_name(self.action_btn))

        self.user_lbl.pack()
        self.username.pack()
        self.pass_lbl.pack()
        self.password.pack()
        self.action_btn.pack()
        self.register_ckbx.pack()

    # change the button name from login to register
    def change_btn_name(self, btn):
        self.reg_flag = not self.reg_flag
        # change to register mod from login mod
        if btn["text"] == "login":
            btn["text"] = "register"
        # change to login mod from register mod
        else:
            btn["text"] = "login"

    # send the user name and password
    def send_user_info(self, entr, entr2):
        if entr.get() and entr2.get():
            user_name = entr.get()
            pass_word = entr2.get()
            # encrypt the password
            hashobj = hashlib.sha256()
            hashobj.update(pass_word)
            pass_word = hashobj.hexdigest()
            # if its in register mod tell the server to register the info
            if self.reg_flag and "$" not in user_name and "$" not in pass_word:
                self.socket.send(user_name + "$" + pass_word + "$1")
                reg_msg = PopUp("Yay?", self.socket.recv(1024), "Close")
                reg_msg.open()
            # tell the server you try to login with the info
            elif not self.reg_flag and "$" not in user_name and "$" not in pass_word:
                self.socket.send(user_name + "$" + pass_word + "$0")
                log_msg = self.socket.recv(1024)
                # if you log in
                if log_msg == "Login successfully":
                    print 'Closing window'
                    self.name = user_name
                    self.did_connect = True
                    self.root.destroy()
                # if you fail to log in
                else:
                    log_msg = PopUp("OwO", log_msg, "Close")
                    log_msg.open()
            # you cant use $ sign in your user name and password to avoid bugs in the code
            else:
                bad_key_win = PopUp("Oops", "you cant use $ sign in the username or password field.", "Close")
                bad_key_win.open()
        else:
            # create pop up window
            no_info_win = PopUp("Oops", "fill the username and password field please.", "Close")
            no_info_win.open()

    # run the window
    def open(self):
        self.root.mainloop()


class MainWindow(Tk):

    def __init__(self, client, name, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self._client = client

        self.title("Journey-opening")

        mid_height = self.winfo_screenheight() / 2
        mid_width = self.winfo_screenwidth() / 2

        self.geometry("600x600+{}+{}".format(mid_width - 300, mid_height - 300))

        self.resizable(width=0, height=0)

        self.pack_propagate(0)

        self.config(background="khaki")

        self._left_panel = Frame(master=self, bg="red", width=400, height=600)
        self._left_panel.pack(anchor="n", side="left")

        self._left_panel.pack_propagate(0)

        self._right_panel = Frame(master=self, bg="blue", width=200, height=600)
        self._right_panel.pack(anchor="w", side="top")

        self._right_panel.pack_propagate(0)

        self._chat_box_panel = Frame(master=self._left_panel, bg="green", width=400, height=400)
        self._chat_box_panel.pack(side="top")

        self._chat_box_scrollbar = Scrollbar(self._chat_box_panel)
        self._chat_box_scrollbar.pack(side=RIGHT, fill=Y)

        self._chat_box = Text(master=self._chat_box_panel, height=30, width=50)
        self._chat_box.config(state=DISABLED, yscrollcommand=self._chat_box_scrollbar.set)
        self._chat_box.pack(side=LEFT, fill=BOTH, expand=TRUE)

        self._message_input_panel = Frame(master=self._left_panel, bg="purple", width=400, height=200)
        self._message_input_panel.pack(fill="x")

        self._message_input_scrollbar = Scrollbar(self._message_input_panel)
        self._message_input_scrollbar.pack(side=RIGHT, fill="y")

        self._message_input = Text(master=self._message_input_panel, bg="purple", width=10, height=10)
        self._message_input.config(yscrollcommand=self._message_input_scrollbar.set)
        self._message_input.pack(fill=BOTH)
        self._message_input.bind("<Return>", self.send_message)
        self._message_input.bind("<Shift-Return>", self.line_down)

        self._send_message_btn = Button(master=self._right_panel, width=10, height=5, text="Send message")
        self._send_message_btn.config(command=lambda: self.send_message())
        self._send_message_btn.pack(anchor="s", fill=X, side=BOTTOM)

        self._exit_btn = Button(master=self._right_panel, width=10, height=5, text="EXIT")
        self._exit_btn.config(command=lambda: self.destroy())
        self._exit_btn.pack(fill=X, side=BOTTOM)

        self._name_label = Label(master=self._right_panel, text="User_name: " + name,
                                 font=("Comic Sans MS", 12), bg="white")
        self._name_label.pack(side=TOP)

    # go down a line
    def line_down(self, event=None):
        self._message_input.insert(END, "\n")
        return 'break'

    def send_message(self, event=None):
        msg = self._message_input.get("1.0", "end-1c")
        if msg.strip("\n \t") != "":
            self._message_input.delete("1.0", END)
            time_now = self.get_time()
            if msg[:8] != "/whisper" and msg[:5] != "/kick":
                self.insert_message(("[{}]<You sent>: "+msg).format(str(time_now)))

            self._client.write_it(msg)
        return "break"

    # get the messages from the message queue of the client
    def read_input_queue(self):
        while True:
            data = self._client.message_queue.get()
            self.insert_message(data)

    # insert the message from the message queue
    def insert_message(self, data):
        self._chat_box.config(state=NORMAL)
        self._chat_box.insert(END, data + "\n")
        self._chat_box.config(state=DISABLED)

    # run the main loop
    def open(self):
        ip_giver.MeDaemon(target=self.read_input_queue, daemon=True).start()
        self.mainloop()

    # close the socket
    def close(self):
        self._client.close()

    # get current time
    def get_time(self):
        now = datetime.datetime.now()
        return datetime.time(now.hour, now.minute, now.second)


# server opening window to see the host ip and to start host a server
class server_win(Tk):

    def __init__(self):
        Tk.__init__(self)
        mid_height = self.winfo_screenheight() / 2
        mid_width = self.winfo_screenwidth() / 2
        self.did_host = False
        self.geometry("400x100+{}+{}".format(mid_width-200, mid_height-100))
        self.server_address = ip_giver.get_ip()
        self.config(bg="#0990CB")
        self.ip_label = Label(master=self, text="server ip address: " + self.server_address)
        self.ip_label.config(bg="white", font=("Comic Sans MS", 16))
        self.host_btn = Button(master=self, text="Host server", font=("Comic Sans MS", 10), command=self.host_server)
        self.host_btn.config(bg="white")
        self.ip_label.pack(side=TOP)
        self.host_btn.pack()

    def host_server(self):
        self.did_host = True
        self.destroy()

    def open(self):
        self.mainloop()


# server console to see the chat log and information about who connects and leave
class server_console(Tk):

    def __init__(self, server):
        Tk.__init__(self)
        mid_height = self.winfo_screenheight() / 2
        mid_width = self.winfo_screenwidth() / 2
        self.server = server
        self.running = True
        self.geometry("600x600+{}+{}".format(mid_width - 300, mid_height - 300))
        self.server_address = ip_giver.get_ip()
        self.config(bg="#0990CB")
        self.ip_label = Label(master=self, text="server ip address: " + self.server_address)
        self.ip_label.config(bg="white", font=("Comic Sans MS", 16))
        self.close_btn = Button(master=self, text="close server", font=("Comic Sans MS", 11),command=self.close_server)
        self.console = Text(master=self, height=34, width=50, state=DISABLED)
        self.ip_label.place(x=100, y=0)
        self.console.place(x=100, y=50)
        self.close_btn.place(x=0, y=10)

    def open(self):
        ip_giver.MeDaemon(target=self.read_message_queue, daemon=True).start()
        self.mainloop()

    def close_server(self):
        self.running = False
        self.destroy()

    def insert_messages(self, data):
        self.console.config(state=NORMAL)
        self.console.insert(END, data + "\n")
        self.console.config(state=DISABLED)

    # read the messages from the server to insert them to the console
    def read_message_queue(self):
        while True:
            data = self.server.message_queue.get()
            print "here"
            self.insert_messages(data)


if __name__ == "__main__":
    s = server_console()
    s.mainloop()


