import tkinter as tk
import time
import math

class AnalogClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Analog Clock")
        self.root.geometry("400x450")
        self.root.resizable(False, False)
        
        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack(pady=10)
        
        self.update_clock()
    
    def draw_clock(self):
        self.canvas.delete("all")
        
        # Draw circle
        self.canvas.create_oval(50, 50, 350, 350, outline="black", width=2)
        
        # Draw center dot
        self.canvas.create_oval(195, 195, 205, 205, fill="black")
        
        # Draw hour markers
        for i in range(12):
            angle = math.radians(i * 30)
            x1 = 200 + 130 * math.sin(angle)
            y1 = 200 - 130 * math.cos(angle)
            x2 = 200 + 140 * math.sin(angle)
            y2 = 200 - 140 * math.cos(angle)
            self.canvas.create_line(x1, y1, x2, y2, width=2)
        
        # Get current time
        current_time = time.localtime()
        hour = current_time.tm_hour % 12
        minute = current_time.tm_min
        second = current_time.tm_sec
        
        # Calculate angles
        hour_angle = math.radians((hour + minute / 60) * 30)
        minute_angle = math.radians((minute + second / 60) * 6)
        second_angle = math.radians(second * 6)
        
        # Draw hour hand
        hour_x = 200 + 80 * math.sin(hour_angle)
        hour_y = 200 - 80 * math.cos(hour_angle)
        self.canvas.create_line(200, 200, hour_x, hour_y, width=6, fill="black")
        
        # Draw minute hand
        minute_x = 200 + 110 * math.sin(minute_angle)
        minute_y = 200 - 110 * math.cos(minute_angle)
        self.canvas.create_line(200, 200, minute_x, minute_y, width=4, fill="blue")
        
        # Draw second hand
        second_x = 200 + 120 * math.sin(second_angle)
        second_y = 200 - 120 * math.cos(second_angle)
        self.canvas.create_line(200, 200, second_x, second_y, width=2, fill="red")
    
    def update_clock(self):
        self.draw_clock()
        self.root.after(1000, self.update_clock)

if __name__ == "__main__":
    root = tk.Tk()
    clock = AnalogClock(root)
    root.mainloop()
