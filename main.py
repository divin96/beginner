import tkinter as tk
#from tkinter import ttk
import ttkbootstrap as ttk
import dbm
from PIL import Image,ImageTk
import playsound 
import threading
import os

class Ring(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Timetable')
        self.geometry('800x800')
        self.tk.call('source','azure\\azure.tcl')
        self.tk.call("set_theme","dark")

        self.menu = Menu(self)
        self.task = Task(self)
        self.watch = Watch(self)
        self.sound = Sound(self)

        self.mainloop()
        # Ensure to close the database connection if needed here

class Menu(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.widget()
        self.place(relx=0, rely=0.1, relwidth=0.3, relheight=0.8)

    def widget(self):
        self.table = ttk.Button(self, text="Time table", command=self.show_task)
        self.table.pack(side='top', expand=True, fill='both', pady=4)
        self.time = ttk.Button(self, text="Time", command=self.show_watch)
        self.time.pack(side='top', expand=True, fill='both', pady=4)
        self.sounds = ttk.Button(self, text="Sounds", command=self.show_sound)
        self.sounds.pack(side='top', expand=True, fill='both', pady=4)

    def show_task(self):
        self.master.task.raising()

    def show_watch(self):
        self.master.watch.raising()

    def show_sound(self):
        self.master.sound.raising()

class Task(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.widget()
        self.place(relx=0.34, rely=0.1, relwidth=0.7, relheight=0.8)
        self.load_tasks()
        #self.snd=Sound(self)
        self.raising()

    def widget(self):
        self.i = tk.StringVar()
        self.stat = tk.StringVar()
        
        self.tb = ttk.Treeview(self, columns=('timestamp', 'task', 'status'), show='headings')
        self.tb.heading('timestamp', text='TIME')
        self.tb.heading('task', text='TASK')
        self.tb.heading('status', text='STATUS')
        self.tb.pack(side='top', fill='both', expand=True)
        
        self.sel = ttk.Combobox(self, textvariable=self.stat)
        self.sel['values'] = [f"{hour:02d}:00" for hour in range(24)]
        self.sel.pack(side='left', fill='x', expand=True)
        
        self.inp = ttk.Entry(self, textvariable=self.i)
        self.inp.pack(side='left', fill='x', expand=True)
        
        self.btn = ttk.Button(self, text='ADD', command=self.adding)
        self.btn.pack(side='left', fill='x',padx=2, expand=True)
        self.start = ttk.Button(self, text='Begin Tasks', command=self.manage)
        self.start.pack(side='left', expand=True,padx=2, fill='both')
        self.tb.bind("<BackSpace>", lambda event: self.delete_selected())

    def raising(self):
        self.lift()

    def adding(self):
        timestamp = self.sel.get()
        task = self.inp.get()
        
        if timestamp and task:
            # Replace with your own database insertion code
            dbm.put(timestamp, task)
            self.tb.insert('', 'end', values=(timestamp, task, 'not yet started'))
            self.i.set('')
            self.stat.set('')

    def manage(self):

        selected_items = self.tb.selection()
        if selected_items:
            for item in selected_items:
                rowid = self.get_rowid(item)
                try:
                    # Replace with your own database query code
                    dbm.c.execute('SELECT duration, task FROM ring WHERE rowid=?', (rowid,))
                    task_data = dbm.c.fetchone()
                    if task_data:
                        self.tb.item(item, values=(task_data[0], task_data[1], 'task in progress'))
                        # Call the start_countdown on Watch instance
                        self.master.watch.start_countdown(task_data[1])
                        file_path=f"C:\\Users\\hp\\Desktop\\my projects\\apping\\songs\\{self.master.sound.file_names[self.master.sound.to]}"
                        self.play_sound(file_path)
                except Exception as e:
                    print(f"Error managing task: {e}")

    def delete_selected(self):
        selected_items = self.tb.selection()
        for item in selected_items:
            self.tb.delete(item)
            rowid = self.get_rowid(item)
            # Replace with your own database deletion code
            dbm.delete(rowid)

    def get_rowid(self, item_id):
        return item_id[1:]

    def load_tasks(self):
        try:
            dbm.c.execute('SELECT duration, task FROM ring')
            rows = dbm.c.fetchall()
            for row in rows:
                self.tb.insert('', 'end', values=(row[0], row[1], "not yet started"))
        except Exception as e:
            print(f"Error loading tasks: {e}")
    def play_sound(self,sound):
        thread = threading.Thread(target=playsound.playsound, args=(sound,))
        thread.start()

class Watch(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.sece = dict()
        self.widget()
        self.place(relx=0.34, rely=0.1, relwidth=0.7, relheight=0.8)

    def widget(self):
        # Replace with your own database fetching code
        dbm.c.execute('SELECT * FROM ring')
        self.data = dbm.c.fetchall()
        if self.data:
            for i in self.data:
                self.sece[i[1]] = self.hms_to_seconds(i[0])
        else:
            self.data = [('00:00', 'none is available')]
            self.sece[self.data[0][1]] = self.hms_to_seconds(self.data[0][0])
        
        self.label = ttk.Label(self, text=self.convert_seconds(self.sece[self.data[0][1]]), background='red')
        self.label.pack(expand=True, fill='both')
        self.img =ttk.Label(self, text='me',background='blue')
        self.img.pack(expand=True, fill='both')

    def hms_to_seconds(self, hms):
        h, m = map(int, hms.split(':'))
        total_seconds = h * 3600 + m * 60
        return total_seconds

    def convert_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def raising(self):
        self.lift()

    def start_countdown(self, task):
        if self.sece.get(task, 0) > 0:
            self.sece[task] -= 1
            self.label.config(text=self.convert_seconds(self.sece[task]))
            self.after(1000, lambda: self.start_countdown(task))
        else:
            self.label.config(text="Task Over")

class Sound(ttk.Frame):
    def __init__(self, parent):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            super().__init__(parent)
            self.selected_button = None  # Track the currently selected button
            self.widget()
            self.place(relx=0.34, rely=0.1, relwidth=0.7, relheight=0.8)
        #print(os.getcwd())

    def widget(self):
        folder_path = 'C:\\Users\\hp\\Desktop\\my projects\\apping\\songs'
        self.file_names = os.listdir(folder_path)
        
        self.buttons = {}  # Dictionary to hold button references
        
        for index, file_name in enumerate(self.file_names):
            btn = ttk.Button(self, text=file_name, command=lambda idx=index: self.soundings(idx))
            btn.pack(expand=True, fill='both', pady=2)
            self.buttons[index] = btn

    def raising(self):
        self.lift()

    def soundings(self, song_index):
        # Load the image
        image_path = "C:\\Users\\hp\\Desktop\\my projects\\apping\\images\\ok.jfif"
        io = Image.open(image_path)
        itk = ImageTk.PhotoImage(io)
        
        # Get the selected button
        new_button = self.buttons.get(song_index)
        
        # Deselect the previously selected button
        if self.selected_button and self.selected_button != new_button:
            self.selected_button.config(image='', compound='none')  # Reset image and state
        
        if new_button:
            new_button.config(image=itk, compound='left')
            # Keep a reference to the image to prevent garbage collection
            new_button.image = itk
        
        # Update the currently selected button
        self.selected_button = new_button
        self.to=song_index


Ring()
