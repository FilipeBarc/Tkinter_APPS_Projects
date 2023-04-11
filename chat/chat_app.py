import tkinter as tk
from tkinter import ttk
import requests
import datetime
from PIL import Image,ImageTk
import tkinter.font as font

COLOUR_LIGHT_BACKGROUND_1 = "#fff"
COLOUR_LIGHT_BACKGROUND_2 = "#f2f3f5"
COLOUR_LIGHT_BACKGROUND_3 = "#e3e5e8"

COLOUR_LIGHT_TEXT = "#aaa"

COLOUR_BUTTON_NORMAL = "#5fba7d"
COLOUR_BUTTON_ACTIVE = "#58c77c"
COLOUR_BUTTON_PRESSED = "#44e378"

MAX = 800

messages = [{'message':"Disconected",'date':15498487}]
message_labels = []

class Main(tk.Tk):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.geometry('1200x500')
        self.minsize(250,500)
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.chat_frame = Chat(self)
        self.chat_frame.grid(row=0,column=0,sticky='NSEW')


class MessWin(tk.Canvas):
    def __init__(self,container,*args,**kwargs):
        super().__init__(container,*args,**kwargs,highlightthickness=0)

        self.message_frame = ttk.Frame(self)
        self.message_frame.columnconfigure(0,weight=1)
        self.scroll_window = self.create_window((0, 0), window=self.message_frame, anchor='nw')

        def configure_scroll(event):
            self.configure(scrollregion=self.bbox('all'))

        def window_size(event):
            self.itemconfig(self.scroll_window,width=self.winfo_width())

        self.bind('<Configure>', window_size)
        self.message_frame.bind('<Configure>', configure_scroll)
        self.bind_all('<MouseWheel>',self.mousewheel)

        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.yview)
        scrollbar.grid(row=0, column=1, sticky='NS')

        self.configure(yscrollcommand=scrollbar.set)
        self.yview_moveto(1.0)

    def mousewheel(self,event):
        self.yview_scroll(-int(event.delta/120),'units')

    def update_messages(self,messages,message_labels):
        existing_labels = [
            (message["text"], time["text"]) for message, time in message_labels]
        for message in messages:
            message_time = datetime.datetime.fromtimestamp(message['date']).strftime("%d-%m-%Y %H:%M:%S")

            if (message['message'], message_time) not in existing_labels:
               self.create_message(message['message'],message_time,message_labels)



    def create_message(self,message_content,message_time,message_labels):
        container = ttk.Frame(self.message_frame)
        container.columnconfigure(1, weight=1)
        container.grid(sticky='EW', padx=(10, 50), pady=10)

        def reconfigure(event):
            for label, _ in message_labels:
                label.configure(wraplength=min(container.winfo_width() - 130, MAX))

        container.bind('<Configure>', reconfigure)

        self.create_bubble(container,message_content,message_time,message_labels)

    def create_bubble(self,container,message_content,message_time,message_labels):
        avatar_image = Image.open('logo.png')
        new_image = avatar_image.resize((50, 50))
        avatar_photo = ImageTk.PhotoImage(new_image)
        avatar_photo.__sizeof__()
        avatar_label = ttk.Label(container,image=avatar_photo)
        avatar_label.image = avatar_photo
        avatar_label.grid(row=0,column=0,rowspan=1,sticky='NEW',padx=(0,0),pady=(0,0))

        time_label = ttk.Label(container, text=message_time)
        time_label.grid(row=0, column=1, sticky='NEW')

        message_label = ttk.Label(
            container,
            text=message_content,
            wraplength=800,
            anchor='w',
            justify='left'
        )
        message_label.grid(row=1, column=1, sticky='NSEW')
        message_labels.append((message_label, time_label))


class Chat(ttk.Frame):
    def __init__ (self, container, *args, **kwargs):
        super().__init__ (container, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.message_window = MessWin(self)
        self.message_window.grid(row=0, column=0, sticky="NSEW", pady=5)

        input_frame = ttk.Frame(self, style="Controls.TFrame", padding=10)
        input_frame.grid(row=1, column=0, sticky="EW")

        self.message_input = tk.Text(input_frame, height=3)
        self.message_input.pack(expand=True, fill="both", side="left", padx=(0, 10))

        message_submit = ttk.Button(
            input_frame,
            text="Send",
            style="SendButton.TButton",
            command=self.post_message
        )
        message_submit.pack()

        message_fetch = ttk.Button(
            input_frame,
            text="Fetch",
            style="FetchButton.TButton",
            command=self.get_messages
        )
        message_fetch.pack()
        self.message_window.update_messages(messages, message_labels)

    def post_message(self):
        body = self.message_input.get("1.0", "end").strip()
        requests.post("http://167.99.63.70/message", json={"message": body})
        self.message_input.delete('1.0', "end")
        self.get_messages()

    def get_messages(self):
        global messages
        messages = requests.get("http://167.99.63.70/messages").json()
        self.message_window.update_messages(messages, message_labels)
        self.after(150, lambda: self.message_window.yview_moveto(1.0))


root = Main()

font.nametofont("TkDefaultFont").configure(size=14)

style = ttk.Style(root)
style.theme_use("clam")

style.configure("Messages.TFrame", background=COLOUR_LIGHT_BACKGROUND_3)

style.configure("Controls.TFrame", background=COLOUR_LIGHT_BACKGROUND_2)

style.configure("SendButton.TButton", borderwidth=0, background=COLOUR_BUTTON_NORMAL)
style.map(
    "SendButton.TButton",
    background=[("pressed", COLOUR_BUTTON_PRESSED), ("active", COLOUR_BUTTON_ACTIVE)],
)

style.configure(
    "FetchButton.TButton", background=COLOUR_LIGHT_BACKGROUND_1, borderwidth=0
)

style.configure(
    "Time.TLabel",
    padding=5,
    background=COLOUR_LIGHT_BACKGROUND_1,
    foreground=COLOUR_LIGHT_TEXT,
    font=8
)

style.configure("Avatar.TLabel", background=COLOUR_LIGHT_BACKGROUND_3)
style.configure("Message.TLabel", background=COLOUR_LIGHT_BACKGROUND_2)

root.mainloop()