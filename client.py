import socket
from threading import Thread
import tkinter as tk
from tkinter import scrolledtext
import argparse as ap
import queue
import time
from datetime import datetime

messages = queue.Queue()
running = True

def get_timestamp():
    now = datetime.now()
    return f"{now.strftime('%H')}:{now.strftime('%M')}:{now.strftime('%S')}"

def add_to_queue(message):
    messages.put(f"{get_timestamp()} {message}")

def monitor_socket(io_sock):
    while running:
        # try:
        message = io_sock.readline()
        add_to_queue(message)
        # except BlockingIOError:
        #     time.sleep(0.1)

def main(server, port):

    sock = socket.create_connection((server, port))
    io_socket = sock.makefile("rw", encoding="utf-8")
    # sock.setblocking(0)

    t = Thread(target=monitor_socket, args=(io_socket,))
    t.start()
    
    window = tk.Tk()
    window.title("GVSU Live Chat")

    name_entry = tk.Toplevel(window)
    name_entry.title("Welcome To GVSU Live Chat!")

    prompt = tk.Label(name_entry, text="Enter your name")
    prompt.grid(row=0)

    user_input = tk.Entry(name_entry, width=40)
    user_input.grid(row=1)

    global name
    name = ""
    def get_name():
        global name
        name = user_input.get()
        name_entry.destroy()
        window.deiconify()

    submit = tk.Button(name_entry, text="Submit", command=get_name)
    submit.grid(row=2)

    chatbox = scrolledtext.ScrolledText(window, wrap="word", width=80, height=20, state="disabled")
    chatbox.grid(row=0, column=0)

    input_box = tk.Entry(window, width=80)
    input_box.grid(row=1, column=0)

    def send_message():
        global name
        message = f"{name} {input_box.get()}\n"
        add_to_queue(message)
        io_socket.write(message)
        io_socket.flush()
        input_box.delete(0, "end")

    send = tk.Button(window, text="Send", command=send_message)
    send.grid(row=1, column=1)

    def teardown():
        global running
        running = False
        # t.join()
        io_socket.write("")
        io_socket.flush()
        window.destroy()
        sock.close()

    quit = tk.Button(window, text="Quit", command=teardown)
    quit.grid(row=0, column=1)

    def get_messages():
        try:
            message = messages.get_nowait()
            chatbox.config(state="normal")
            chatbox.insert("end", message)
            chatbox.yview("end")
            chatbox.config(state="disabled")
        except queue.Empty:
            pass
        window.after(100, get_messages)

    window.after(100, get_messages)
    window.withdraw()
    window.mainloop()

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--port", default=5000)

    args = parser.parse_args()

    server = args.server
    port = args.port

    main(server, port)