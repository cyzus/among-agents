import tkinter as tk
from tkinter import messagebox
import os
class MapUI:
    def __init__(self, map_image_dir, room_coords, debug=True):
        
        self.map_image_dir = map_image_dir
        # get absolute path of the image
        self.map_image_dir = os.path.abspath(self.map_image_dir)
        self.debug = debug
        self.room_coords = room_coords
        # self.reset()

    def reset(self):
        
        self.master = tk.Tk()
        self.map_image = tk.PhotoImage(file=self.map_image_dir)
        self.canvas = tk.Canvas(self.master, width=self.map_image.width(), height=self.map_image.height())
        self.canvas.pack()

        # Create label to display coordinates
        self.coord_label = tk.Label(self.master, text="")
        self.coord_label.pack()

        # Bind motion event to update coordinates
        self.canvas.bind("<Motion>", self.update_coordinates)

        # Create a frame for task progress bar
        
        self.task_progress = tk.Canvas(self.master, width=self.canvas.winfo_width(), height=30)
        self.task_progress.pack(side='bottom', fill='both', expand=True)
        self.progress_label = tk.Label(self.master, text="Task Progress")
        self.progress_label.pack(side='bottom')

        # Create scrollbar for activity log
        self.activity_log = ScrollingActivityLog(self.master, width=self.map_image.width())
        self.activity_log.pack(side='bottom', fill='both', expand=True)


        
        

    def draw_map(self, env):
        self.master.title("Among Agents UI")
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.map_image)
        for room, roominfo in self.room_coords.items():
            coords = roominfo["coords"]
            x_coords = [coords[i] for i in range(len(coords)) if i % 2 == 0]
            y_coords = [coords[i] for i in range(len(coords)) if i % 2 != 0]
            max_x, min_x = max(x_coords), min(x_coords)
            max_y, min_y = max(y_coords), min(y_coords)
            midx = (max_x + min_x) / 2
            midy = (max_y + min_y) / 2
            text_coord = (midx, min_y + 10)
            if room == "Upper Engine":
                room_text = "Upper Eng."
            elif room == "Lower Engine":
                room_text = "Lower Eng."
            elif room == "Communications":
                room_text = "Comms"
            elif room == "Navigation":
                room_text = "Nav"
            else:
                room_text = room
            self.canvas.create_polygon(coords, outline="black", fill="white")
            self.canvas.create_text(text_coord, text=room_text, fill="black")


            players = env.map.get_players_in_room(room, include_new_deaths=True)
            
            player_size = 15
            space = 5
            part_y = (max_y - min_y) / 3 + min_y
            start_coords = (min_x + space, part_y) # Start drawing players from here
            temp_coords = start_coords
            for player in players:
                self.canvas.create_oval(temp_coords[0], temp_coords[1], temp_coords[0] + player_size, temp_coords[1] + player_size, fill=player.color)

                if not player.is_alive:
                    self.canvas.create_line(temp_coords[0], temp_coords[1], temp_coords[0] + player_size, temp_coords[1] + player_size, fill="red", width=4)
                temp_coords = (temp_coords[0] + player_size + space, temp_coords[1])
                if temp_coords[0] > max_x - player_size - space:
                    temp_coords = (start_coords[0], temp_coords[1] + player_size + space)
        
        self.draw_task_progress(env.task_assignment.check_task_completion(), game_over=env.check_game_over())
        self.draw_activity_log(env.activity_log)
        
        if self.debug:
            self.master.after(1000)
        self.master.update()

    def draw_task_progress(self, task_progress, game_over):
        # Create a task progress bar (rectangle that fills up as tasks are completed) at the bottom of the screen
        height = self.task_progress.winfo_height()
        width = self.task_progress.winfo_width()
        x1 = width * 0.1
        y1 = height * 0.1
        x2 = width * 0.9
        y2 = height * 0.9
        # create a rectangle in the middle of the canvas
        self.task_progress.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
        if game_over != 1:
            self.task_progress.create_rectangle(x1, y1, x1 + (x2 - x1) * task_progress, y2, fill="green", outline="black")
            self.progress_label.config(text=f"Task Progress: {task_progress * 100:.1f}%")

        else:
            self.task_progress.create_rectangle(x1, y1, x2, y2, fill="red", outline="black")


    def draw_activity_log(self, activity_log):
        self.activity_log.log_activity(activity_log)

    def update_coordinates(self, event):
        x, y = event.x, event.y
        self.coord_label.config(text=f"Coordinates: ({x}, {y})")
    
    def report(self, text):
        height = self.canvas.winfo_height()
        width = self.canvas.winfo_width()
        x1 = width * 0.25
        y1 = height * 0.25
        x2 = width * 0.75
        y2 = height * 0.75
        # create a rectangle in the middle of the canvas
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
        self.canvas.create_text((width / 2, height / 2), text=text, fill="black", font=("Calibri", 10))
        self.master.update()

        # wait for n seconds
        self.master.after(5000)
        
    def quit_UI(self):
        self.master.quit()
        self.master.destroy()        


class ScrollingActivityLog(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.activity_log = tk.Text(self, height=10, wrap='none', state='disabled')
        self.activity_log.pack(side='left', fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(self, orient='vertical', command=self.activity_log.yview)
        scrollbar.pack(side='right', fill='y')
        self.activity_log.config(yscrollcommand=scrollbar.set)
        self.logs = []
        
    def log_activity(self, activities):
        self.activity_log.config(state='normal')
        for activity in activities:
            text = self.activity_text(activity)
            if text not in self.logs:
                self.logs.append(text)
                self.activity_log.insert('end', f"{text}\n")
        self.activity_log.config(state='disabled')
        self.activity_log.see('end')

    def activity_text(self, activity):
        text = f"Step {activity['timestep']}: {activity['phase']} phase - {activity['player']} {activity['action']}"
        return text


        