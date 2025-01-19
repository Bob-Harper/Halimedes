import tkinter as tk
from PIL import Image, ImageTk  # For background image support


class RobotLegGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Robot Leg Controller")

        self.positions = {"leg1": [0, 0, 0], "leg2": [0, 0, 0], "leg3": [0, 0, 0], "leg4": [0, 0, 0]}

        # Create a canvas for the layout
        self.canvas = tk.Canvas(master, width=800, height=600, bg="white")
        self.canvas.pack()

        # Load and display the background image
        self.background_image = Image.open("top_down_view.png")  # Replace with your image file
        self.bg_image_tk = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image_tk)

        # Layout the sliders for each leg
        self.leg1_frame = self.create_leg_frame("leg1", 25, 25)
        self.leg2_frame = self.create_leg_frame("leg2", 475, 25)
        self.leg3_frame = self.create_leg_frame("leg3", 25, 450)
        self.leg4_frame = self.create_leg_frame("leg4", 475, 450)

        # Central control panel (representing the robot's body)
        self.control_frame = tk.Frame(self.master, bg="gray", width=200, height=200, relief="ridge", bd=3)
        self.control_frame.place(x=337, y=455)

        tk.Button(self.control_frame, text="Save Position", command=self.save_position).pack(pady=5)
        tk.Button(self.control_frame, text="Playback", command=self.playback).pack(pady=5)

        # Textbox for displaying coordinates
        self.coords_box = tk.Text(self.master, width=64, height=4)
        self.coords_box.place(x=135, y=300)

    def create_leg_frame(self, leg_name, x, y):
        frame = tk.Frame(self.master, bg="lightgray", relief="ridge", bd=3)
        frame.place(x=x, y=y, width=300, height=100)

        tk.Label(frame, text=leg_name.capitalize()).pack()

        sliders = []
        for i, axis in enumerate(["X", "Y", "Z"]):
            row_frame = tk.Frame(frame)
            row_frame.pack(fill="x", pady=2)

            label = tk.Label(row_frame, text=f"{axis}: 0", width=6, anchor="w")
            label.pack(side="left")

            slider = tk.Scale(row_frame, from_=-100, to=100, orient=tk.HORIZONTAL, length=200, showvalue=False)
            slider.pack(side="right", fill="x", expand=True)
            slider.bind("<Motion>", lambda e, l=leg_name.lower(), a=i, lbl=label: self.update_position(l, a, e.widget.get(), lbl))
            sliders.append(slider)

        # Store sliders in positions using lowercase keys
        self.positions[leg_name.lower()] = sliders
        return frame

    def update_position(self, leg_name, axis_index, value, label):
        sliders = self.positions[leg_name]
        sliders[axis_index].set(value)  # Update slider value
        label.config(text=f"{['X', 'Y', 'Z'][axis_index]}: {value}")  # Update label text
        self.update_coords_box()

    def update_coords_box(self):
        self.coords_box.delete(1.0, tk.END)

        # Ensure leg order matches ['right front', 'left front', 'left rear', 'right rear']
        ordered_legs = ['leg1', 'leg2', 'leg3', 'leg4']  # Matches original CLI leg order
        steps = [self.positions[leg] for leg in ordered_legs]

        # Format the steps
        step_lines = f"[[{steps[0][0].get()}, {steps[0][1].get()}, {steps[0][2].get()}], " \
                    f"[{steps[1][0].get()}, {steps[1][1].get()}, {steps[1][2].get()}], " \
                    f"[{steps[2][0].get()}, {steps[2][1].get()}, {steps[2][2].get()}], " \
                    f"[{steps[3][0].get()}, {steps[3][1].get()}, {steps[3][2].get()}]]"
        self.coords_box.insert(tk.END, f"step_values = {step_lines}\n")

    def save_position(self):
        current_positions = {leg: [slider.get() for slider in sliders] for leg, sliders in self.positions.items()}
        self.coords_box.insert(tk.END, f"Saved: {current_positions}\n")

    def playback(self):
        self.coords_box.insert(tk.END, "Playback sequence initiated.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotLegGUI(root)
    root.geometry("800x600")  # Adjusted to fit 1280x800 resolution
    root.mainloop()
