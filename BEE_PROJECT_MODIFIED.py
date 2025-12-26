import tkinter as tk
from tkinter import messagebox
import math
import time
import pygame  # For sound

HEX_SIZE = 60

bee_img_path = "bee2.png"
first_bg_image_path = "first_image.png"   # for Start screen
other_bg_image_path = "bee_first_slide.png"  # for Input and Grid
bee_sound_path = "bee_buzz.mp3"
bgm_path = "BGM.mp3"  # BGM for all screens

class HexGridApp:
    def __init__(self, root):
        self.root = root
        pygame.mixer.init()
        self.bee_sound = pygame.mixer.Sound(bee_sound_path)
        self.bgm_channel = pygame.mixer.Channel(1)  # BGM channel

        self.first_bg_image = tk.PhotoImage(file=first_bg_image_path)
        self.other_bg_image = tk.PhotoImage(file=other_bg_image_path)

        self.bgm_on = True  # Toggle flag

        self.reset_state()
        self.start_screen()

    def reset_state(self):
        self.rows = 0
        self.cols = 0
        self.start_cell = None
        self.end_cell = None
        self.hex_centers = {}
        self.hex_ids = {}
        self.pos_to_axial = {}
        self.canvas = None
        self.canvas_frame = None
        self.info_labels = []

    def play_bgm(self):
        if self.bgm_on and not self.bgm_channel.get_busy():
            bgm = pygame.mixer.Sound(bgm_path)
            self.bgm_channel.play(bgm, loops=-1)

    def stop_bgm(self):
        self.bgm_channel.stop()

    def toggle_bgm(self):
        self.bgm_on = not self.bgm_on
        if self.bgm_on:
            self.play_bgm()
            self.bgm_button.config(text="Music ON")
        else:
            self.stop_bgm()
            self.bgm_button.config(text="Music OFF")

    def start_screen(self):
        self.stop_bgm()
        self.play_bgm()
        self.clear_root()

        label = tk.Label(self.root, image=self.first_bg_image)
        label.place(x=0, y=0, relwidth=1, relheight=1)

        start_button = tk.Button(self.root, text="Start Now", font=("Comic Sans MS", 16, "bold"),
                                 bg="green", fg="white",
                                 command=self.input_screen)
        start_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.bgm_button = tk.Button(self.root, text="Music ON", font=("Comic Sans MS", 12, "bold"),
                                    bg="light blue", fg="black",
                                    command=self.toggle_bgm)
        self.bgm_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def input_screen(self):
        self.reset_state()
        self.play_bgm()
        self.clear_root()

        label = tk.Label(self.root, image=self.other_bg_image)
        label.place(x=0, y=0, relwidth=1, relheight=1)

        frame = tk.Frame(self.root, bg="#FFDB58")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        label1 = tk.Label(frame, text="Enter No. of Rows:", font=("Comic Sans MS", 14, "bold"),
                          bg="#FFDB58", fg="#8B4513")
        label1.pack(pady=10)
        self.row_entry = tk.Entry(frame, font=("Comic Sans MS", 14), bg="#FFDB58",
                                  fg="#8B4513", insertbackground="#8B4513")
        self.row_entry.pack(pady=5)

        label2 = tk.Label(frame, text="Enter No. of Columns:", font=("Comic Sans MS", 14, "bold"),
                          bg="#FFDB58", fg="#8B4513")
        label2.pack(pady=10)
        self.col_entry = tk.Entry(frame, font=("Comic Sans MS", 14), bg="#FFDB58",
                                  fg="#8B4513", insertbackground="#8B4513")
        self.col_entry.pack(pady=5)

        proceed_button = tk.Button(frame, text="Generate Grid", font=("Comic Sans MS", 14, "bold"),
                                   bg="#8B4513", fg="white", command=self.start_hex_grid)
        proceed_button.pack(pady=20)

        self.bgm_button = tk.Button(self.root, text="Music ON" if self.bgm_on else "Music OFF",
                                    font=("Comic Sans MS", 12, "bold"),
                                    bg="light blue", fg="black",
                                    command=self.toggle_bgm)
        self.bgm_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def start_hex_grid(self):
        try:
            self.rows = int(self.row_entry.get())
            self.cols = int(self.col_entry.get())
            if self.rows <= 0 or self.cols <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid positive integers.")
            return
        self.clear_root()
        self.play_bgm()
        self.setup_canvas()
        self.draw_hex_grid()
        self.add_bottom_buttons()

    def setup_canvas(self):
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.canvas.bind("<Button-1>", self.on_hex_click)

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def draw_hex_grid(self):
        self.canvas.delete("all")
        self.hex_centers.clear()
        self.hex_ids.clear()
        self.pos_to_axial.clear()
        for label in self.info_labels:
            label.destroy()
        self.info_labels.clear()

        cell_num = 1
        x_spacing = 3 / 4 * HEX_SIZE * 2
        y_spacing = math.sqrt(3) * HEX_SIZE

        total_width = self.cols * x_spacing + 400
        total_height = self.rows * y_spacing + 400
        x_offset = (total_width - (self.cols - 1) * x_spacing) / 2
        y_offset = (total_height - (self.rows - 1) * y_spacing) / 2

        img_w = self.other_bg_image.width()
        img_h = self.other_bg_image.height()
        self.canvas.delete("bg_tile")
        for x in range(0, int(total_width), img_w):
            for y in range(0, int(total_height), img_h):
                self.canvas.create_image(x, y, image=self.other_bg_image, anchor="nw", tags="bg_tile")

        for row in range(self.rows):
            fill_color = "#fca503" if row % 2 == 0 else "#f5b905"
            for col in range(self.cols):
                x = col * x_spacing + x_offset
                y = row * y_spacing + y_offset
                if col % 2 == 1:
                    y += y_spacing / 2
                self.hex_centers[cell_num] = (x, y)
                axial_q = col
                axial_r = row - col // 2
                self.pos_to_axial[cell_num] = (axial_q, axial_r)
                poly_id = self.draw_hexagon(x, y, HEX_SIZE, cell_num, fill_color)
                self.hex_ids[poly_id] = cell_num
                cell_num += 1

        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def draw_hexagon(self, center_x, center_y, size, cell_number, color="yellow"):
        points = []
        for i in range(6):
            angle_rad = math.radians(60 * i)
            x = center_x + size * math.cos(angle_rad)
            y = center_y + size * math.sin(angle_rad)
            points.extend((x, y))
        poly_id = self.canvas.create_polygon(points, fill=color, outline="black", width=2)
        self.canvas.create_text(center_x, center_y, text=str(cell_number), font=("Comic Sans MS", 10, "bold"))
        return poly_id

    def on_hex_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        clicked_items = self.canvas.find_overlapping(x, y, x, y)
        for item in clicked_items:
            if item in self.hex_ids:
                cell = self.hex_ids[item]
                if self.start_cell is None:
                    self.start_cell = cell
                    self.highlight_hex(cell, "red")
                elif self.end_cell is None and cell != self.start_cell:
                    self.end_cell = cell
                    self.highlight_hex(cell, "red")
                    self.draw_path_and_animate()
                break

    def highlight_hex(self, cell, color):
        x, y = self.hex_centers[cell]
        self.draw_hexagon(x, y, HEX_SIZE, cell, color)

    def draw_path_and_animate(self):
        self.stop_bgm()  # stop BGM while bee moves
        start_axial = self.pos_to_axial[self.start_cell]
        end_axial = self.pos_to_axial[self.end_cell]
        axial_path = self.hex_line(*start_axial, *end_axial)
        reverse_pos_to_cell = {v: k for k, v in self.pos_to_axial.items()}
        cell_path = [reverse_pos_to_cell[a] for a in axial_path if a in reverse_pos_to_cell]
        for cell in cell_path:
            self.highlight_hex(cell, "lightgreen")
        self.animate_bee(cell_path)
        self.play_bgm()  # resume BGM
        self.show_custom_popup(cell_path)

    def animate_bee(self, cell_path):
        bee_img = tk.PhotoImage(file=bee_img_path)
        self.canvas.bee_img = bee_img
        bee = self.canvas.create_image(0, 0, image=bee_img)

        self.bee_sound.play(-1)

        for i in range(len(cell_path) - 1):
            start = self.hex_centers[cell_path[i]]
            end = self.hex_centers[cell_path[i + 1]]
            for s in range(20):
                t = s / 20
                x = start[0] * (1 - t) + end[0] * t
                y = start[1] * (1 - t) + end[1] * t
                self.canvas.coords(bee, x, y)
                self.keep_bee_visible(x, y)
                self.canvas.update()
                time.sleep(0.01)

        self.bee_sound.stop()
        self.canvas.delete(bee)

    def keep_bee_visible(self, x, y):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        visible_x0 = self.canvas.canvasx(0)
        visible_y0 = self.canvas.canvasy(0)
        visible_x1 = visible_x0 + canvas_width
        visible_y1 = visible_y0 + canvas_height
        margin = 80
        if x < visible_x0 + margin:
            self.canvas.xview_moveto(max((x - margin) / self.canvas.bbox("all")[2], 0))
        elif x > visible_x1 - margin:
            self.canvas.xview_moveto(min((x - canvas_width + margin) / self.canvas.bbox("all")[2], 1))
        if y < visible_y0 + margin:
            self.canvas.yview_moveto(max((y - margin) / self.canvas.bbox("all")[3], 0))
        elif y > visible_y1 - margin:
            self.canvas.yview_moveto(min((y - canvas_height + margin) / self.canvas.bbox("all")[3], 1))

    def show_custom_popup(self, path):
        info_win = tk.Toplevel(self.root)
        info_win.title("Path Information")
        info_win.configure(bg="#FFDB58")  # Mustard yellow

        start = f"Start Cell: {self.start_cell}"
        end = f"End Cell: {self.end_cell}"
        steps = f"Cells Passed: {len(path)}"
        cells_list = "\n".join(str(cell) for cell in path)

        message = f"{start}\n{end}\n{steps}\n\nCells on Path:\n\n"

        frame = tk.Frame(info_win, bg="#FFDB58")
        frame.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)

        label = tk.Label(frame, text=message, font=("Chewy", 14),
                         bg="#FFDB58", fg="#5C4033", justify="left", anchor="w")
        label.pack(anchor="w")

        text_frame = tk.Frame(frame, bg="#FFDB58")
        text_frame.pack(fill=tk.BOTH, expand=True)

        # No bg/fg color set here — defaults will apply
        text = tk.Text(text_frame, wrap="word", font=("Chewy", 12),
                       height=10, width=40,fg="#5C4033")
        text.insert(tk.END, cells_list)
        text.config(state=tk.DISABLED)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)

        close_btn = tk.Button(info_win, text="Close",
                              font=("Chewy", 12, "bold"),
                              bg="green", fg="white",
                              command=info_win.destroy)
        close_btn.pack(pady=20)

    def add_bottom_buttons(self):
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        retry = tk.Button(bottom_frame, text="Retry", font=("Comic Sans MS", 14, "bold"),
                          bg="green", fg="white",
                          command=self.retry_selection)
        retry.pack(side=tk.LEFT, padx=20)

        back = tk.Button(bottom_frame, text="Back", font=("Comic Sans MS", 14, "bold"),
                         bg="green", fg="white",
                         command=self.input_screen)
        back.pack(side=tk.LEFT, padx=20)

        exit_btn = tk.Button(bottom_frame, text="Exit", font=("Comic Sans MS", 14, "bold"),
                             bg="red", fg="white",
                             command=self.root.quit)
        exit_btn.pack(side=tk.RIGHT, padx=20)

        self.bgm_button = tk.Button(bottom_frame, text="Music ON" if self.bgm_on else "Music OFF",
                                    font=("Comic Sans MS", 12, "bold"),
                                    bg="light blue", fg="black",
                                    command=self.toggle_bgm)
        self.bgm_button.pack(side=tk.BOTTOM, pady=5)

    def retry_selection(self):
        self.start_cell = None
        self.end_cell = None
        self.draw_hex_grid()

    def axial_to_cube(self, q, r):
        x = q
        z = r
        y = -x - z
        return x, y, z

    def cube_to_axial(self, x, y, z):
        return x, z

    def cube_round(self, x, y, z):
        rx, ry, rz = round(x), round(y), round(z)
        dx, dy, dz = abs(rx - x), abs(ry - y), abs(rz - z)
        if dx > dy and dx > dz:
            rx = -ry - rz
        elif dy > dz:
            ry = -rx - rz
        else:
            rz = -rx - ry
        return (rx, ry, rz)

    def hex_line(self, aq, ar, bq, br):
        a_cube = self.axial_to_cube(aq, ar)
        b_cube = self.axial_to_cube(bq, br)
        N = max(abs(a_cube[0] - b_cube[0]), abs(a_cube[1] - b_cube[1]), abs(a_cube[2] - b_cube[2]))
        results = []
        for i in range(N + 1):
            t = i / N
            x = a_cube[0] + (b_cube[0] - a_cube[0]) * t
            y = a_cube[1] + (b_cube[1] - a_cube[1]) * t
            z = a_cube[2] + (b_cube[2] - a_cube[2]) * t
            rx, ry, rz = self.cube_round(x, y, z)
            results.append(self.cube_to_axial(rx, ry, rz))
        return results

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Honeycomb Hex Grid")
    root.geometry("1200x800")
    app = HexGridApp(root)
    root.mainloop()
