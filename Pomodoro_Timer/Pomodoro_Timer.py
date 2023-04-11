import tkinter as tk
from tkinter import ttk
from collections import deque
def set_dpi_awareness():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
set_dpi_awareness()

class Main(tk.Tk):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.title("Pomodoro Timer")
        self.columnconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        self.frames = dict()

        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('Timer.TFrame',background='#fff')
        style.configure('Background.TFrame', background='#2e3f4f')
        style.configure('TimerText.TLabel', background='#fff',foreground='#8095a8',font='Courier 38')
        style.configure('LightText.TLabel', background='#2e3f4f', foreground='#eee')
        style.configure('PomodoroButton.TButton', background='#293846', foreground='#eee')
        style.map('PomodoroButton.TButton',background=[('active','#2e3f4f'),('disabled','#eee')])
        self['background']='#2e3f4f'

        self.pomodoro = tk.StringVar(value=25)
        self.long = tk.StringVar(value=15)
        self.short = tk.StringVar(value=5)
        self.timer_order = ['Pomodoro', 'Short Break', 'Pomodoro', 'Short Break', 'Pomodoro', 'Long Break']
        self.timer_schedule = deque(self.timer_order)

        frame = ttk.Frame(self)
        frame.grid()
        frame.columnconfigure(0,weight=1)

        timer_frame = Timer(frame, self,lambda: self.show_frame(Settings) )
        timer_frame.grid(row=0,column=0,sticky='NSEW')
        settings_frame = Settings(frame, self, lambda: self.show_frame(Timer) )
        settings_frame.grid(row=0, column=0, sticky='NSEW')

        self.frames[Timer] = timer_frame
        self.frames[Settings] = settings_frame

        self.show_frame(Timer)

    def show_frame(self, frame):
        frames = self.frames[frame]
        frames.tkraise()

class Timer(ttk.Frame):
    def __init__(self,parent,controller,show_settings):
        super().__init__(parent)

        self['style'] = 'Background.TFrame'

        self.controller = controller
        pomodoro_time = int(controller.pomodoro.get())
        self.current_time = tk.StringVar(value=f"{pomodoro_time:02d}:00")

        self.current_time_label = tk.StringVar(value=controller.timer_schedule[0])
        self.timer_running = True
        self.decrement_time_job = None

        timer_description = ttk.Label(self,textvariable=self.current_time_label,style='LightText.TLabel')
        timer_description.grid(row=0,column=0,sticky="W",pady=(10,0),padx=(10,0))

        settings_button = ttk.Button(
            self,
            text="Settings",
            command=show_settings,
            style='PomodoroButton.TButton',
            cursor='hand2'
        )
        settings_button.grid(row=0,column=1,sticky='E',padx=10,pady=(10,0))

        timer_frame = ttk.Frame(self,height='100',style='Timer.TFrame')
        timer_frame.grid(row=1,column=0,columnspan=2,pady=(10,0),sticky='NSEW')

        timer_counter = ttk.Label(timer_frame,textvariable=self.current_time,style='TimerText.TLabel')
        timer_counter.place(relx=0.5,rely=0.5, anchor='center')

        button_container = ttk.Frame(self, padding=10,style='Background.TFrame')
        button_container.grid(row=2,column=0,columnspan=2,sticky='EW')
        button_container.columnconfigure((0,1,2),weight=1)
        self.start_button = ttk.Button(
            button_container,
            text="Start",
            command=self.start_timer,
            style='PomodoroButton.TButton',
            cursor="hand2"
        )
        self.start_button.grid(row=0,column=0,sticky='EW')
        self.stop_button = ttk.Button(
            button_container,
            text="Stop",
            state='disable',
            command=self.stop_timer,
            style='PomodoroButton.TButton',
            cursor='hand2'
        )
        self.stop_button.grid(row=0,column=1,sticky="EW",padx=5)
        reset_button = ttk.Button(
            button_container,
            text="Reset",
            command=self.reset_timer,
            style='PomodoroButton.TButton',
            cursor='hand2'
        )
        reset_button.grid(row=0,column=2,sticky='EW')

    def start_timer(self):
        self.timer_running = True
        self.start_button['state'] = 'disable'
        self.stop_button['state'] = 'enable'
        self.decrement_time()

    def stop_timer(self):
        self.timer_running = False
        self.stop_button['state'] = 'disable'
        self.start_button['state'] = 'enable'
        if self.decrement_time_job:
            self.after_cancel(self.decrement_time_job)
            self.decrement_time_job = None

    def reset_timer(self):
        self.stop_timer()
        pomodoro_time = int(self.controller.pomodoro.get())
        self.current_time.set(f"{pomodoro_time:02d}:00")
        self.controller.timer_schedule = deque(self.controller.timer_order)
        self.current_time_label.set(self.controller.timer_schedule[0])

    def decrement_time(self):
        current_time = self.current_time.get()

        if self.timer_running and current_time != '00:00':
            minutes, seconds = current_time.split(':')

            if int(seconds) > 0:
                seconds = int(seconds) - 1
                minutes = int(minutes)
            else:
                seconds = 59
                minutes = int(minutes) - 1
            self.current_time.set(f"{minutes:02d}:{seconds:02d}")
            self.decrement_time_job = self.after(10, self.decrement_time)

        elif self.timer_running and current_time == '00:00':
            self.controller.timer_schedule.rotate(-1)
            next_up = self.controller.timer_schedule[0]
            self.current_time_label.set((next_up))

            if next_up == 'Pomodoro':
                pomodoro_time = int(self.controller.pomodoro.get())
                self.current_time.set(f"{pomodoro_time:02d}:00")
            elif next_up == 'Short Break':
                pomodoro_time = int(self.controller.pomodoro.get())
                self.current_time.set(f"{pomodoro_time:02d}:00")
            elif next_up == 'Long Break':
                pomodoro_time = int(self.controller.pomodoro.get())
                self.current_time.set(f"{pomodoro_time:02d}:00")

            self.decrement_time_job = self.after(10, self.decrement_time)

class Settings(ttk.Frame):
    def __init__(self,parent,controller, show_timer):
        super().__init__(parent)

        self['style']= 'Background.TFrame'

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)

        settings_container = ttk.Frame(self,padding="30 15 30 15",style='Background.TFrame')
        settings_container.grid(row=0,column=0,sticky='EW',padx=10,pady=10)

        settings_container.columnconfigure(0,weight=1)
        settings_container.rowconfigure(1,weight=1)

        pomodoro_label = ttk.Label(settings_container,text="Pomodoro",style='LightText.TLabel')
        pomodoro_label.grid(row=0,column=0,sticky='W')
        pomodoro_input = ttk.Spinbox(
            settings_container,
            from_=0,
            to=120,
            increment=1,
            justify='center',
            textvariable=controller.pomodoro,
            width=10
        )
        pomodoro_input.grid(row=0,column=1,sticky='EW')
        pomodoro_input.focus()

        long_label = ttk.Label(settings_container, text="Long Break",style='LightText.TLabel')
        long_label.grid(row=1, column=0, sticky='W')
        long_input = ttk.Spinbox(
            settings_container,
            from_=0,
            to=60,
            increment=1,
            justify='center',
            textvariable=controller.long,
            width=10
        )
        long_input.grid(row=1, column=1, sticky='EW')

        short_label = ttk.Label(settings_container, text="Short Break",style='LightText.TLabel')
        short_label.grid(row=2, column=0, sticky='W')
        short_input = ttk.Spinbox(
            settings_container,
            from_=0,
            to=30,
            increment=1,
            justify='center',
            textvariable=controller.short,
            width=10
        )
        short_input.grid(row=2, column=1, sticky='EW')

        for child in settings_container.winfo_children():
            child.grid_configure(padx=10,pady=10)

        button_frame = ttk.Frame(self,style='Background.TFrame')
        button_frame.grid(sticky='EW',padx=10)
        button_frame.columnconfigure(0,weight=1)

        timer_button = ttk.Button(
            button_frame,
            text="Back",
            command=show_timer,
            style='PomodoroButton.TButton',
            cursor='hand2'
        )
        timer_button.grid(row=0, column=0, sticky='EW', padx=10, pady=(0, 20))

root = Main()
root.mainloop()