import tkinter
import customtkinter
import random
from ctypes import windll
import pywinstyles
import json
import winreg
import os
import sys
from win32mica import ApplyMica, MicaTheme, MicaStyle
from screeninfo import get_monitors
from PIL import Image
import winsound
import threading
import copy
import hPyT

customtkinter.set_appearance_mode("Dark")
windll.shcore.SetProcessDpiAwareness(1)


class Board:
    def __init__(self):
        self.window = customtkinter.CTk()
        self.window.withdraw()

        self.window.title("2048 BrainRot")
        self.window.configure(fg_color="black")
        self.window.iconbitmap(self.resource_path("assets/2048.ico"))
        self.window.wm_attributes("-topmost", 1)
        self.window.protocol("WM_DELETE_WINDOW", self.save_game_state)
        self.window.focus()

        self.window.after(100, lambda: self.window.wm_attributes("-topmost", 0))
        self.window.focus()

        self.window.bind("<Alt-F4>", self.save_game_state)

        with open(r"configs\\user_config.json", "r") as file:
            data = json.loads(file.read())
            self.backdrop_style = data["backdrop_style"]
            self.window_style = data["window_style"]
            self.color_scheme = data["color_scheme"]
            self.continue_previous = data["continue_previous"]
            self.start_pinned = data["start_pinned"]
            self.n = data["grid_size"]

        if len(sys.argv) > 1:
            try:
                geometry = sys.argv[-1]
                self.window.wm_geometry(geometry)
            except Exception:
                if self.n == 4:
                    self.window.geometry("400x550")
                elif self.n == 5:
                    self.window.geometry("500x650")
        else:
            if self.n == 4:
                self.window.geometry("400x550")
            elif self.n == 5:
                self.window.geometry("500x650")

        with open(self.resource_path("assets/color_schemes.json"), "r") as file:
            data = json.loads(file.read())
            if self.color_scheme == "Random":
                ch = random.choice(list(data.keys()))
                self.color = data[ch]["color"]
                self.bg_color = data[ch]["bg_color"]
            else:
                self.color = data[self.color_scheme]["color"]
                self.bg_color = data[self.color_scheme]["bg_color"]

        self.window.update()
        self.window.focus()

        if self.window_style == "Win7":
            pywinstyles.apply_style(self.window, "win7")
        elif self.window_style == "Default":
            pass
        elif self.window_style == "Inverse":
            pywinstyles.apply_style(self.window, "inverse")
        else:
            pass

        if self.backdrop_style == "Mica":
            ApplyMica(
                HWND=self.window.frame(), Theme=MicaTheme.DARK, Style=MicaStyle.DEFAULT
            )
        elif self.backdrop_style == "Mica Alt":
            ApplyMica(
                HWND=self.window.frame(), Theme=MicaTheme.DARK, Style=MicaStyle.ALT
            )
        elif self.backdrop_style == "Acrylic":
            pywinstyles.apply_style(self.window, "acrylic")
        else:
            ApplyMica(
                HWND=self.window.frame(), Theme=MicaTheme.DARK, Style=MicaStyle.DEFAULT
            )

        self.high_score = 0

        self.restart_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/restart.png")),
            size=(20, 20),
        )
        self.trophy_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/trophy.png")),
            size=(20, 20),
        )
        self.settings_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/settings.png")),
            size=(20, 20),
        )
        self.pin_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/pin.png")), size=(20, 20)
        )
        self.unpin_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/unpin.png")),
            size=(20, 20),
        )
        self.game_over_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/game_over.png")),
            size=(80, 80),
        )
        self.game_won_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/game_won.png")),
            size=(75, 75),
        )
        self.cross_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/cross.png")),
            size=(20, 20),
        )

        self.frame_top = customtkinter.CTkFrame(self.window, fg_color="black")
        self.frame_top.pack(padx=10, pady=10, fill=tkinter.BOTH, expand=True)

        self.settings_button = customtkinter.CTkButton(
            self.frame_top,
            text="",
            image=self.settings_image,
            fg_color="grey12",
            corner_radius=6,
            width=20,
            height=30,
            hover_color="grey17",
            command=self.settings,
        )
        self.settings_button.pack(side=tkinter.LEFT)

        self.restart_button = customtkinter.CTkButton(
            self.frame_top,
            text="",
            image=self.restart_image,
            fg_color="grey12",
            corner_radius=6,
            width=20,
            height=30,
            command=self.restart_game,
            hover_color="grey17",
        )
        self.restart_button.pack(side=tkinter.LEFT, padx=(10, 0))

        self.pin_button = customtkinter.CTkButton(
            self.frame_top,
            text="",
            image=self.pin_image,
            fg_color="grey12",
            corner_radius=6,
            width=20,
            height=30,
            hover_color="grey17",
            command=self.pin,
        )
        self.pin_button.pack(side=tkinter.LEFT, padx=(10, 0))

        self.high_score_frame = customtkinter.CTkFrame(
            self.frame_top, fg_color="black", corner_radius=10
        )
        self.high_score_frame.pack(side=tkinter.RIGHT)

        self.trophy_button = customtkinter.CTkButton(
            self.high_score_frame,
            text="",
            image=self.trophy_image,
            fg_color="black",
            corner_radius=6,
            width=20,
            height=30,
            hover=None,
        )
        self.trophy_button.pack(side=tkinter.LEFT)

        self.high_score_label = customtkinter.CTkLabel(
            self.high_score_frame,
            text="",
            font=("Segoe UI", 16, "bold"),
            fg_color="grey12",
            corner_radius=10,
            padx=10,
            pady=10,
        )
        self.high_score_label.pack(side=tkinter.RIGHT)

        self.frame = customtkinter.CTkFrame(self.window, fg_color="black")
        self.frame.pack(padx=10, pady=10, fill=tkinter.BOTH, expand=True)

        self.game_score = customtkinter.CTkLabel(
            self.frame,
            text="Score : 0",
            font=("Segoe UI", 20, "bold"),
            fg_color="grey12",
            corner_radius=10,
            padx=10,
            pady=10,
        )
        self.game_score.pack(padx=10, pady=10)

        self.load_high_score()

        self.high_score_label.configure(text=str(self.high_score))

        self.gameArea = customtkinter.CTkFrame(
            self.frame, fg_color="black", corner_radius=2
        )
        self.board = []
        self.gridCell = [[0] * self.n for i in range(self.n)]
        self.compress = False
        self.merge = False
        self.moved = False
        self.score = 0
        self.argv = sys.argv
        self.undo_stack = []

        for i in range(self.n):
            rows = []
            for j in range(self.n):
                label = customtkinter.CTkLabel(
                    self.gameArea,
                    text="",
                    fg_color="azure4",
                    font=("Segoe UI", 40, "bold"),
                    width=80,
                    height=80,
                    corner_radius=5,
                )
                label.grid(row=i, column=j, padx=5, pady=5)

                rows.append(label)
            self.board.append(rows)

        if self.continue_previous:
            self.load_game_state()
        elif len(sys.argv) > 1:
            self.load_game_state()

        self.gameArea.pack(padx=10, pady=(10, 0))

        self.window.focus()
        if self.backdrop_style == "Mica":
            ApplyMica(
                HWND=self.window.frame(), Theme=MicaTheme.DARK, Style=MicaStyle.DEFAULT
            )
        elif self.backdrop_style == "Mica Alt":
            ApplyMica(
                HWND=self.window.frame(), Theme=MicaTheme.DARK, Style=MicaStyle.ALT
            )

        self.window.deiconify()

        self.window.wm_attributes("-topmost", 0)
        if self.start_pinned:
            self.pin()

        self.window.bind("<Control-;>", self.settings)
        self.window.bind("<Control-r>", self.restart_game)
        self.window.bind("<Control-p>", self.pin)
        self.window.bind("<Control-z>", lambda event: self.undo())
        self.window.bind("u", lambda event: self.undo())

    def resource_path(self, relative_path):
        """Get the absolute path to an asset, handling PyInstaller paths."""
        if getattr(sys, "frozen", False):  # If running as a PyInstaller EXE
            base_path = sys._MEIPASS
        else:  # If running in development
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, relative_path)

    def change_grid(self, size):
        image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/question.png")),
            size=(60, 60),
        )

        self.game_reset_box(
            f"Change Grid Size to {size} x {size}",
            f"Change the Grid Size to {size} x {size}?",
            "Your Progess if any might be lost",
            image,
            "Yes",
            "No",
            size,
        )

    def save_game_state(self, e=None):
        game_state = {
            "gridCell": self.gridCell,
            "score": self.score,
            "undo_stack": self.undo_stack,
        }
        with open(r"configs\\game_state.json", "w") as file:
            json.dump(game_state, file)

        self.window.destroy()

    def load_game_state(self):
        try:
            # Load game state from the saved file
            with open(r"configs\\game_state.json", "r") as file:
                game_state = json.load(file)
                self.gridCell = game_state["gridCell"]
                self.score = game_state["score"]
                self.undo_stack = game_state["undo_stack"]
                # Add code to load other game-related data here
                self.paintGrid()  # Refresh the game board
                self.game_score.configure(text="Score : " + str(self.score))
        # except FileNotFoundError:
        #     self.continue_previous = False
        except Exception:
            self.continue_previous = False

    def restart_app(self):
        geometry = self.window.wm_geometry()
        self.save_game_state()
        os.execl(sys.executable, sys.executable, *sys.argv, geometry)

    def settings(self, e=None):
        self.frame_top.pack_forget()
        self.frame.pack_forget()

        self.window.unbind("<Control-;>")
        self.window.unbind("<Control-r>")
        self.window.unbind("<Control-p>")
        self.window.unbind("<Control-z>")
        self.window.unbind("u")

        try:
            self.settings_pane.pack(
                padx=(3, 0), pady=(0, 10), fill=tkinter.BOTH, expand=True
            )
            self.window.bind("<BackSpace>", self.settings_back)

        except Exception:
            self.settings_pane = customtkinter.CTkScrollableFrame(
                self.window,
                fg_color="black",
                width=400,
                height=530,
                scrollbar_button_color="black",
                scrollbar_fg_color="black",
                scrollbar_button_hover_color="grey13",
            )
            self.settings_pane.pack(
                padx=(3, 0), pady=(0, 10), fill=tkinter.BOTH, expand=True
            )

            self.window.bind("<BackSpace>", self.settings_back)

            self.back_image = customtkinter.CTkImage(
                light_image=Image.open(self.resource_path("assets/back.png")),
                size=(20, 20),
            )

            self.back_button = customtkinter.CTkButton(
                self.settings_pane,
                text="",
                image=self.back_image,
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=self.settings_back,
            )
            self.back_button.place(x=5, y=0)

            self.backdrop_frame = customtkinter.CTkFrame(
                self.settings_pane, fg_color="grey5"
            )
            self.backdrop_frame.pack(padx=5, pady=(50, 10), fill=tkinter.X)

            self.backdrop_label_frame = customtkinter.CTkFrame(
                self.backdrop_frame, fg_color="grey5"
            )
            self.backdrop_label = customtkinter.CTkLabel(
                self.backdrop_label_frame,
                text="Back Drop Material",
                font=("Segoe UI", 18, "bold"),
                fg_color="grey5",
                corner_radius=10,
            )
            self.backdrop_label.pack(padx=10, pady=5, side=tkinter.LEFT)
            self.backdrop_label_frame.pack(padx=5, pady=10, fill=tkinter.X)

            customtkinter.CTkFrame(
                self.backdrop_frame, fg_color="black", height=2
            ).pack(fill=tkinter.X)

            self.mica_frame = customtkinter.CTkFrame(
                self.backdrop_frame, fg_color="grey5"
            )
            self.mica_label = customtkinter.CTkLabel(
                self.mica_frame,
                text="Mica",
                font=("Segoe UI", 16),
                fg_color="grey5",
                corner_radius=10,
            )
            self.mica_label.pack(padx=10, pady=5, side=tkinter.LEFT)
            self.mica_button = customtkinter.CTkButton(
                self.mica_frame,
                text="Apply",
                fg_color="grey12",
                corner_radius=6,
                width=80,
                height=30,
                hover_color="grey17",
                font=("Segoe UI", 14, "bold"),
                command=lambda: self.change_backdrop("Mica"),
            )
            self.mica_button.pack(padx=10, pady=5, side=tkinter.RIGHT)
            self.mica_frame.pack(padx=10, pady=5, fill=tkinter.X)

            customtkinter.CTkFrame(
                self.backdrop_frame, fg_color="black", height=2
            ).pack(fill=tkinter.X)

            self.mica_alt_frame = customtkinter.CTkFrame(
                self.backdrop_frame, fg_color="grey5"
            )
            self.mica_alt_label = customtkinter.CTkLabel(
                self.mica_alt_frame,
                text="Mica Alt",
                font=("Segoe UI", 16),
                fg_color="grey5",
                corner_radius=10,
            )
            self.mica_alt_label.pack(padx=10, pady=5, side=tkinter.LEFT)
            self.mica_alt_button = customtkinter.CTkButton(
                self.mica_alt_frame,
                text="Apply",
                fg_color="grey12",
                corner_radius=6,
                width=80,
                height=30,
                hover_color="grey17",
                font=("Segoe UI", 14, "bold"),
                command=lambda: self.change_backdrop("Mica Alt"),
            )
            self.mica_alt_button.pack(padx=10, pady=5, side=tkinter.RIGHT)
            self.mica_alt_frame.pack(padx=10, pady=5, fill=tkinter.X)

            customtkinter.CTkFrame(
                self.backdrop_frame, fg_color="black", height=2
            ).pack(fill=tkinter.X)

            self.acrylic_frame = customtkinter.CTkFrame(
                self.backdrop_frame, fg_color="grey5"
            )
            self.acrylic_label = customtkinter.CTkLabel(
                self.acrylic_frame,
                text="Acrylic",
                font=("Segoe UI", 16),
                fg_color="grey5",
                corner_radius=10,
            )
            self.acrylic_label.pack(padx=10, pady=5, side=tkinter.LEFT)
            self.acrylic_button = customtkinter.CTkButton(
                self.acrylic_frame,
                text="Apply",
                fg_color="grey12",
                corner_radius=6,
                width=80,
                height=30,
                hover_color="grey17",
                font=("Segoe UI", 14, "bold"),
                command=lambda: self.change_backdrop("Acrylic"),
            )
            self.acrylic_button.pack(padx=10, pady=5, side=tkinter.RIGHT)
            self.acrylic_frame.pack(padx=10, pady=5, fill=tkinter.X)

            self.window_style_frame = customtkinter.CTkFrame(
                self.settings_pane, fg_color="grey5"
            )
            self.window_style_frame.pack(padx=5, pady=5, fill=tkinter.X)

            self.window_style_label_frame = customtkinter.CTkFrame(
                self.window_style_frame, fg_color="grey5"
            )
            self.window_style_label = customtkinter.CTkLabel(
                self.window_style_label_frame,
                text="Window Style",
                font=("Segoe UI", 18, "bold"),
                fg_color="grey5",
                corner_radius=10,
            )
            self.window_style_label.pack(padx=10, pady=5, side=tkinter.LEFT)
            self.window_style_label_frame.pack(padx=5, pady=10, fill=tkinter.X)

            customtkinter.CTkFrame(
                self.window_style_frame, fg_color="black", height=2
            ).pack(fill=tkinter.X)

            self.win7_frame = customtkinter.CTkFrame(
                self.window_style_frame, fg_color="grey5"
            )
            self.win7_label = customtkinter.CTkLabel(
                self.win7_frame,
                text="Windows 7",
                font=("Segoe UI", 16),
                fg_color="grey5",
                corner_radius=10,
            )
            self.win7_label.pack(padx=10, pady=5, side=tkinter.LEFT)
            self.win7_button = customtkinter.CTkButton(
                self.win7_frame,
                text="Apply",
                fg_color="grey12",
                corner_radius=6,
                width=80,
                height=30,
                hover_color="grey17",
                font=("Segoe UI", 14, "bold"),
                command=lambda: self.change_window_style("Win7"),
            )
            self.win7_button.pack(padx=10, pady=5, side=tkinter.RIGHT)
            self.win7_frame.pack(padx=10, pady=5, fill=tkinter.X)

            customtkinter.CTkFrame(
                self.window_style_frame, fg_color="black", height=2
            ).pack(fill=tkinter.X)

            self.default_frame = customtkinter.CTkFrame(
                self.window_style_frame, fg_color="grey5"
            )
            self.defualt_label_frame = customtkinter.CTkLabel(
                self.default_frame,
                text="Default",
                font=("Segoe UI", 16),
                fg_color="grey5",
                corner_radius=10,
            )
            self.defualt_label_frame.pack(padx=10, pady=5, side=tkinter.LEFT)
            self.defualt_button = customtkinter.CTkButton(
                self.default_frame,
                text="Apply",
                fg_color="grey12",
                corner_radius=6,
                width=80,
                height=30,
                hover_color="grey17",
                font=("Segoe UI", 14, "bold"),
                command=lambda: self.change_window_style("Default"),
            )
            self.defualt_button.pack(padx=10, pady=5, side=tkinter.RIGHT)
            self.default_frame.pack(padx=10, pady=5, fill=tkinter.X)

            customtkinter.CTkFrame(
                self.window_style_frame, fg_color="black", height=2
            ).pack(fill=tkinter.X)

            self.inverse_frame = customtkinter.CTkFrame(
                self.window_style_frame, fg_color="grey5"
            )
            self.inverse_label = customtkinter.CTkLabel(
                self.inverse_frame,
                text="Inverse",
                font=("Segoe UI", 16),
                fg_color="grey5",
                corner_radius=10,
            )
            self.inverse_label.pack(padx=10, pady=5, side=tkinter.LEFT)
            self.inverse_button = customtkinter.CTkButton(
                self.inverse_frame,
                text="Apply",
                fg_color="grey12",
                corner_radius=6,
                width=80,
                height=30,
                hover_color="grey17",
                font=("Segoe UI", 14, "bold"),
                command=lambda: self.change_window_style("Inverse"),
            )
            self.inverse_button.pack(padx=10, pady=5, side=tkinter.RIGHT)
            self.inverse_frame.pack(padx=10, pady=5, fill=tkinter.X)

            self.grid_size_frame = customtkinter.CTkFrame(
                self.settings_pane, fg_color="grey5"
            )
            self.grid_size_frame.pack(padx=5, pady=5, fill=tkinter.X)

            self.grid_size_label_frame = customtkinter.CTkFrame(
                self.grid_size_frame, fg_color="grey5"
            )
            self.grid_size_label = customtkinter.CTkLabel(
                self.grid_size_label_frame,
                text="Grid Size",
                font=("Segoe UI", 18, "bold"),
                fg_color="grey5",
                corner_radius=10,
            )

            self.grid_size_label.pack(padx=10, pady=5, side=tkinter.LEFT)
            self.grid_size_label_frame.pack(padx=5, pady=10, fill=tkinter.X)

            customtkinter.CTkFrame(
                self.grid_size_frame, fg_color="black", height=2
            ).pack(fill=tkinter.X)

            x4_frame = customtkinter.CTkFrame(self.grid_size_frame, fg_color="grey5")
            self.four_label = customtkinter.CTkLabel(
                x4_frame,
                text="4 x 4",
                font=("Segoe UI", 16),
                fg_color="grey5",
                corner_radius=10,
            )
            self.four_label.pack(padx=10, pady=5, side=tkinter.LEFT)

            self.four_button = customtkinter.CTkButton(
                x4_frame,
                text="Apply",
                fg_color="grey12",
                corner_radius=6,
                width=80,
                height=30,
                hover_color="grey17",
                font=("Segoe UI", 14, "bold"),
                command=lambda: self.change_grid(4),
            )
            self.four_button.pack(padx=10, pady=5, side=tkinter.RIGHT)

            x4_frame.pack(padx=10, pady=5, fill=tkinter.X)

            customtkinter.CTkFrame(
                self.grid_size_frame, fg_color="black", height=2
            ).pack(fill=tkinter.X)

            x5_frame = customtkinter.CTkFrame(self.grid_size_frame, fg_color="grey5")
            self.five_label = customtkinter.CTkLabel(
                x5_frame,
                text="5 x 5",
                font=("Segoe UI", 16),
                fg_color="grey5",
                corner_radius=10,
            )
            self.five_label.pack(padx=10, pady=5, side=tkinter.LEFT)

            self.five_button = customtkinter.CTkButton(
                x5_frame,
                text="Apply",
                fg_color="grey12",
                corner_radius=6,
                width=80,
                height=30,
                hover_color="grey17",
                font=("Segoe UI", 14, "bold"),
                command=lambda: self.change_grid(5),
            )
            self.five_button.pack(padx=10, pady=5, side=tkinter.RIGHT)

            x5_frame.pack(padx=10, pady=5, fill=tkinter.X)

            self.color_scheme_frame = customtkinter.CTkFrame(
                self.settings_pane, fg_color="grey5"
            )
            self.color_scheme_frame.pack(padx=5, pady=(10, 10), fill=tkinter.X)

            self.color_scheme_label_frame = customtkinter.CTkFrame(
                self.color_scheme_frame, fg_color="grey5"
            )
            self.color_scheme_label = customtkinter.CTkLabel(
                self.color_scheme_label_frame,
                text="Color Scheme",
                font=("Segoe UI", 18, "bold"),
                fg_color="grey5",
                corner_radius=10,
            )
            self.color_scheme_label.pack(padx=10, pady=5, side=tkinter.LEFT)
            self.color_scheme_label_frame.pack(padx=5, pady=10, fill=tkinter.X)

            customtkinter.CTkFrame(
                self.color_scheme_frame, fg_color="black", height=2
            ).pack(fill=tkinter.X)

            self.color_schemes_buttons_frame = customtkinter.CTkFrame(
                self.color_scheme_frame, fg_color="grey5"
            )
            self.color_schemes_buttons_frame.pack(padx=10, pady=5, fill=tkinter.X)

            self.greenish_image = customtkinter.CTkImage(
                light_image=Image.open(
                    self.resource_path("assets/themes/greenish.png")
                ),
                size=(90, 90),
            )
            self.purpulish_image = customtkinter.CTkImage(
                light_image=Image.open(
                    self.resource_path("assets/themes/purpulish.png")
                ),
                size=(90, 90),
            )
            self.default_image = customtkinter.CTkImage(
                light_image=Image.open(self.resource_path("assets/themes/default.png")),
                size=(90, 90),
            )
            self.vibrant_image = customtkinter.CTkImage(
                light_image=Image.open(self.resource_path("assets/themes/vibrant.png")),
                size=(90, 90),
            )
            self.jungle_image = customtkinter.CTkImage(
                light_image=Image.open(self.resource_path("assets/themes/jungle.png")),
                size=(90, 90),
            )
            self.ocean_image = customtkinter.CTkImage(
                light_image=Image.open(self.resource_path("assets/themes/ocean.png")),
                size=(90, 90),
            )
            self.space_image = customtkinter.CTkImage(
                light_image=Image.open(self.resource_path("assets/themes/space.png")),
                size=(90, 90),
            )
            self.desert_image = customtkinter.CTkImage(
                light_image=Image.open(self.resource_path("assets/themes/desert.png")),
                size=(90, 90),
            )
            self.mystic_image = customtkinter.CTkImage(
                light_image=Image.open(
                    self.resource_path("assets/themes/MysticForest.png")
                ),
                size=(90, 90),
            )
            self.midnightSerenity_image = customtkinter.CTkImage(
                light_image=Image.open(
                    self.resource_path("assets/themes/MidnightSerenity.png")
                ),
                size=(90, 90),
            )
            self.winterWonderland_image = customtkinter.CTkImage(
                light_image=Image.open(
                    self.resource_path("assets/themes/WinterWonderland.png")
                ),
                size=(90, 90),
            )
            self.royalPalace_image = customtkinter.CTkImage(
                light_image=Image.open(
                    self.resource_path("assets/themes/RoyalPalace.png")
                ),
                size=(90, 90),
            )
            self.translucent_image = customtkinter.CTkImage(
                light_image=Image.open(
                    self.resource_path("assets/themes/translucent.png")
                ),
                size=(90, 90),
            )
            self.random_image = customtkinter.CTkImage(
                light_image=Image.open(self.resource_path("assets/themes/random.png")),
                size=(90, 90),
            )

            self.purpulish = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.purpulish_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme("Purpulish", self.purpulish),
            )
            self.purpulish.grid(row=0, column=0, padx=5, pady=10)

            self.greenish = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.greenish_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme("Greenish", self.greenish),
            )
            self.greenish.grid(row=0, column=1, padx=5, pady=5)

            self.ocean = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.ocean_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme("Ocean", self.ocean),
            )
            self.ocean.grid(row=0, column=2, padx=5, pady=5)

            self.desert = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.desert_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme("Desert", self.desert),
            )
            self.desert.grid(row=1, column=0, padx=5, pady=10)

            self.default = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.default_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme("Default", self.default),
            )
            self.default.grid(row=1, column=1, padx=5, pady=5)

            self.vibrant = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.vibrant_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme("Vibrant", self.vibrant),
            )
            self.vibrant.grid(row=1, column=2, padx=5, pady=5)

            self.jungle = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.jungle_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme("Jungle", self.jungle),
            )
            self.jungle.grid(row=2, column=0, padx=5, pady=5)

            self.space = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.space_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme("Space", self.space),
            )
            self.space.grid(row=2, column=1, padx=5, pady=5)

            self.mystic = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.mystic_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme("MysticForest", self.mystic),
            )
            self.mystic.grid(row=2, column=2, padx=5, pady=10)

            self.midnightSerenity = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.midnightSerenity_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme(
                    "MidnightSerenity", self.midnightSerenity
                ),
            )
            self.midnightSerenity.grid(row=3, column=0, padx=5, pady=10)

            self.winterWonderland = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.winterWonderland_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme(
                    "WinterWonderland", self.winterWonderland
                ),
            )
            self.winterWonderland.grid(row=3, column=1, padx=5, pady=10)

            self.royalPalace = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.royalPalace_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme(
                    "RoyalPalace", self.royalPalace
                ),
            )
            self.royalPalace.grid(row=3, column=2, padx=5, pady=10)

            self.translucent = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.translucent_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme(
                    "Translucent", self.translucent
                ),
            )
            self.translucent.grid(row=4, column=0, padx=5, pady=10)

            self.randomb = customtkinter.CTkButton(
                self.color_schemes_buttons_frame,
                image=self.random_image,
                text="",
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=lambda: self.change_color_scheme("Random", self.randomb),
            )
            self.randomb.grid(row=4, column=1, padx=5, pady=10)

            self.advanced_frame = customtkinter.CTkFrame(
                self.settings_pane, fg_color="grey5"
            )
            self.advanced_frame.pack(padx=5, pady=5, fill=tkinter.X)

            self.advanced_frame_label_frame = customtkinter.CTkFrame(
                self.advanced_frame, fg_color="grey5"
            )
            self.advanced_frame_label = customtkinter.CTkLabel(
                self.advanced_frame_label_frame,
                text="Advanced",
                font=("Segoe UI", 18, "bold"),
                fg_color="grey5",
                corner_radius=10,
            )

            self.advanced_frame_label.pack(padx=10, pady=5, side=tkinter.LEFT)
            self.advanced_frame_label_frame.pack(padx=5, pady=10, fill=tkinter.X)

            customtkinter.CTkFrame(
                self.advanced_frame, fg_color="black", height=2
            ).pack(fill=tkinter.X)

            self.continue_previous_frame = customtkinter.CTkFrame(
                self.advanced_frame, fg_color="grey5"
            )
            self.continue_previous_frame.pack(padx=10, pady=5, fill=tkinter.X)

            self.continue_previous_label_frame = customtkinter.CTkFrame(
                self.continue_previous_frame, fg_color="grey5"
            )
            self.continue_previous_label = customtkinter.CTkLabel(
                self.continue_previous_label_frame,
                text="Save Game State",
                font=("Segoe UI", 16),
                fg_color="grey5",
                corner_radius=10,
                wraplength=150,
                justify=tkinter.LEFT,
            )
            self.continue_previous_label.pack(padx=10, pady=5, side=tkinter.LEFT)

            self.continue_previous_button = customtkinter.CTkButton(
                self.continue_previous_frame,
                text="Apply",
                fg_color="grey12",
                corner_radius=6,
                width=80,
                height=30,
                hover_color="grey17",
                font=("Segoe UI", 14, "bold"),
                command=self.change_continue_previous,
            )
            self.continue_previous_button.pack(padx=10, pady=5, side=tkinter.RIGHT)

            self.continue_previous_label_frame.pack(padx=5, pady=5, fill=tkinter.X)

            customtkinter.CTkFrame(
                self.advanced_frame, fg_color="black", height=2
            ).pack(fill=tkinter.X)

            self.start_pinned_frame = customtkinter.CTkFrame(
                self.advanced_frame, fg_color="grey5"
            )
            self.start_pinned_frame.pack(padx=10, pady=5, fill=tkinter.X)

            self.start_pinned_label_frame = customtkinter.CTkFrame(
                self.start_pinned_frame, fg_color="grey5"
            )
            self.start_pinned_label = customtkinter.CTkLabel(
                self.start_pinned_label_frame,
                text="Start Pinned",
                font=("Segoe UI", 16),
                fg_color="grey5",
                corner_radius=10,
                wraplength=150,
                justify=tkinter.LEFT,
            )
            self.start_pinned_label.pack(padx=10, pady=5, side=tkinter.LEFT)

            self.start_pinned_button = customtkinter.CTkButton(
                self.start_pinned_frame,
                text="Apply",
                fg_color="grey12",
                corner_radius=6,
                width=80,
                height=30,
                hover_color="grey17",
                font=("Segoe UI", 14, "bold"),
                command=self.change_start_pinned,
            )
            self.start_pinned_button.pack(padx=10, pady=5, side=tkinter.RIGHT)

            self.start_pinned_label_frame.pack(padx=5, pady=5, fill=tkinter.X)

            self.shortcut_image = customtkinter.CTkImage(
                light_image=Image.open(self.resource_path("assets/shortcut.png")),
                size=(30, 30),
            )
            self.history_image = customtkinter.CTkImage(
                light_image=Image.open(self.resource_path("assets/history.png")),
                size=(20, 20),
            )

            self.shortcuts_frame = customtkinter.CTkFrame(
                self.settings_pane, fg_color="grey5"
            )
            self.shortcuts_frame.pack(padx=5, pady=(10, 5), fill=tkinter.X)

            self.shortcuts_frame_label_frame = customtkinter.CTkFrame(
                self.shortcuts_frame, fg_color="transparent"
            )
            self.shortcuts_image_button = customtkinter.CTkButton(
                self.shortcuts_frame_label_frame,
                text="",
                image=self.shortcut_image,
                fg_color="transparent",
                corner_radius=6,
                width=15,
                height=15,
                command=None,
                hover=False,
            )
            self.shortcuts_image_button.pack(padx=(0, 10), pady=0, side=tkinter.LEFT)
            self.shortcuts_frame_label = customtkinter.CTkLabel(
                self.shortcuts_frame_label_frame,
                text="Shortcuts",
                font=("Segoe UI", 15, "bold"),
                fg_color="transparent",
            )
            self.shortcuts_frame_label.pack(padx=5, pady=5, side=tkinter.LEFT)

            self.shortcuts_frame_label_frame.pack(padx=5, pady=5, fill=tkinter.X)

            self.shortcuts_frame.bind(
                "<Enter>", lambda e: self.shortcuts_frame.configure(fg_color="grey10")
            )
            self.shortcuts_frame.bind(
                "<Leave>", lambda e: self.shortcuts_frame.configure(fg_color="grey5")
            )
            self.shortcuts_frame_label_frame.bind(
                "<Enter>", lambda e: self.shortcuts_frame.configure(fg_color="grey10")
            )
            self.shortcuts_frame_label_frame.bind(
                "<Leave>", lambda e: self.shortcuts_frame.configure(fg_color="grey5")
            )
            self.shortcuts_frame_label.bind(
                "<Enter>", lambda e: self.shortcuts_frame.configure(fg_color="grey10")
            )
            self.shortcuts_frame_label.bind(
                "<Leave>", lambda e: self.shortcuts_frame.configure(fg_color="grey5")
            )
            self.shortcuts_image_button.bind(
                "<Enter>", lambda e: self.shortcuts_frame.configure(fg_color="grey10")
            )
            self.shortcuts_image_button.bind(
                "<Leave>", lambda e: self.shortcuts_frame.configure(fg_color="grey5")
            )

            self.shortcuts_frame.bind("<Button-1>", lambda e: self.shortcuts())
            self.shortcuts_frame_label_frame.bind(
                "<Button-1>", lambda e: self.shortcuts()
            )
            self.shortcuts_frame_label.bind("<Button-1>", lambda e: self.shortcuts())
            self.shortcuts_image_button.bind("<Button-1>", lambda e: self.shortcuts())

            curr = 0 if self.n == 4 else 1

            if curr == 0:
                self.four_button.configure(text="Applied", command=None)
                try:
                    self.four_button.configure(fg_color=self.get_accent_color())
                except Exception:
                    pass
            else:
                self.five_button.configure(text="Applied", command=None)
                try:
                    self.five_button.configure(fg_color=self.get_accent_color())
                except Exception:
                    pass

            self.current_color_scheme_button = None

            if self.color_scheme == "Greenish":
                self.current_color_scheme_button = self.greenish
            elif self.color_scheme == "Purpulish":
                self.current_color_scheme_button = self.purpulish
            elif self.color_scheme == "Default":
                self.current_color_scheme_button = self.default
            elif self.color_scheme == "Vibrant":
                self.current_color_scheme_button = self.vibrant
            elif self.color_scheme == "Jungle":
                self.current_color_scheme_button = self.jungle
            elif self.color_scheme == "Ocean":
                self.current_color_scheme_button = self.ocean
            elif self.color_scheme == "Space":
                self.current_color_scheme_button = self.space
            elif self.color_scheme == "Desert":
                self.current_color_scheme_button = self.desert
            elif self.color_scheme == "MysticForest":
                self.current_color_scheme_button = self.mystic
            elif self.color_scheme == "MidnightSerenity":
                self.current_color_scheme_button = self.midnightSerenity
            elif self.color_scheme == "WinterWonderland":
                self.current_color_scheme_button = self.winterWonderland
            elif self.color_scheme == "RoyalPalace":
                self.current_color_scheme_button = self.royalPalace
            elif self.color_scheme == "Translucent":
                self.current_color_scheme_button = self.translucent
            elif self.color_scheme == "Random":
                self.current_color_scheme_button = self.randomb
            else:
                self.current_color_scheme_button = self.default

            try:
                self.current_color_scheme_button.configure(
                    border_width=2, border_color=self.get_accent_color(), command=None
                )
            except Exception:
                pass

            self.current_backdrop_style = None
            self.current_window_style = None

            if self.continue_previous:
                self.continue_previous_button.configure(text="Applied")
                try:
                    self.continue_previous_button.configure(
                        fg_color=self.get_accent_color()
                    )
                except Exception:
                    pass
            else:
                self.continue_previous_button.configure(text="Apply", fg_color="grey12")

            if self.start_pinned:
                self.start_pinned_button.configure(text="Applied")
                try:
                    self.start_pinned_button.configure(fg_color=self.get_accent_color())
                except Exception:
                    pass

            if self.backdrop_style == "Mica":
                self.mica_button.configure(text="Applied")
                self.current_backdrop_style = self.mica_button
            elif self.backdrop_style == "Acrylic":
                self.acrylic_button.configure(text="Applied")
                self.current_backdrop_style = self.acrylic_button
            elif self.backdrop_style == "Mica Alt":
                self.mica_alt_button.configure(text="Applied")
                self.current_backdrop_style = self.mica_alt_button

            if self.window_style == "Win7":
                self.win7_button.configure(text="Applied")
                self.current_window_style = self.win7_button
            elif self.window_style == "Default":
                self.defualt_button.configure(text="Applied")
                self.current_window_style = self.defualt_button
            elif self.window_style == "Inverse":
                self.inverse_button.configure(text="Applied")
                self.current_window_style = self.inverse_button

            try:
                self.current_backdrop_style.configure(
                    fg_color=self.get_accent_color(), command=None
                )
                self.current_window_style.configure(
                    fg_color=self.get_accent_color(), command=None
                )
            except Exception:
                pass

    def shortcuts(self, e=None):
        self.settings_pane.pack_forget()

        self.shortcuts_pane = customtkinter.CTkScrollableFrame(
            self.window,
            fg_color="black",
            scrollbar_button_color="black",
            scrollbar_fg_color="black",
            scrollbar_button_hover_color="grey13",
        )
        self.shortcuts_pane.pack(
            padx=(3, 0), pady=(0, 10), fill=tkinter.BOTH, expand=True
        )

        self.back_button_3 = customtkinter.CTkButton(
            self.shortcuts_pane,
            text="",
            image=self.back_image,
            fg_color="grey12",
            corner_radius=6,
            width=20,
            height=30,
            hover_color="grey17",
            command=self.shortcuts_back,
        )
        self.back_button_3.place(x=5, y=0)

        self.shortcuts_label = customtkinter.CTkLabel(
            self.shortcuts_pane,
            text="Shortcuts",
            font=("Segoe UI", 30, "bold"),
            fg_color="transparent",
            corner_radius=10,
        )
        self.shortcuts_label.pack(padx=5, pady=(5, 15))

        undo = customtkinter.CTkFrame(self.shortcuts_pane, fg_color="grey5")
        undo.pack(padx=5, pady=5, fill=tkinter.X)

        undo_button = customtkinter.CTkFrame(undo, fg_color="grey5")
        undo_button.pack(padx=5, pady=3, side=tkinter.LEFT)

        customtkinter.CTkButton(
            undo_button,
            text="U",
            fg_color="grey20",
            text_color="White",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(10, 5), pady=5, side=tkinter.LEFT)
        customtkinter.CTkLabel(
            undo_button,
            text="or",
            font=("Segoe UI", 20),
            fg_color="transparent",
            corner_radius=10,
        ).pack(padx=0, pady=10, side=tkinter.LEFT)
        customtkinter.CTkButton(
            undo_button,
            text="Ctrl",
            fg_color="grey20",
            text_color="White",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(10, 5), pady=5, side=tkinter.LEFT)
        customtkinter.CTkButton(
            undo_button,
            text="Z",
            fg_color="grey20",
            text_color="White",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(5, 10), pady=5, side=tkinter.LEFT)

        undo_label = customtkinter.CTkLabel(
            undo,
            text="Undo",
            font=("Segoe UI", 18, "bold"),
            fg_color="transparent",
            corner_radius=10,
        )
        undo_label.pack(padx=(10, 15), pady=3, side=tkinter.RIGHT)

        new_game = customtkinter.CTkFrame(self.shortcuts_pane, fg_color="grey5")
        new_game.pack(padx=5, pady=5, fill=tkinter.X)

        new_game_button = customtkinter.CTkFrame(new_game, fg_color="grey5")
        new_game_button.pack(padx=5, pady=3, side=tkinter.LEFT)

        customtkinter.CTkButton(
            new_game_button,
            text="Ctrl",
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(10, 5), pady=5, side=tkinter.LEFT)
        customtkinter.CTkButton(
            new_game_button,
            text="R",
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(5, 15), pady=5, side=tkinter.LEFT)

        new_game_label = customtkinter.CTkLabel(
            new_game,
            text="New Game",
            font=("Segoe UI", 18, "bold"),
            fg_color="transparent",
            corner_radius=10,
        )
        new_game_label.pack(padx=(10, 15), pady=5, side=tkinter.RIGHT)

        settings_ = customtkinter.CTkFrame(self.shortcuts_pane, fg_color="grey5")
        settings_.pack(padx=5, pady=5, fill=tkinter.X)

        settings_button = customtkinter.CTkFrame(settings_, fg_color="grey5")
        settings_button.pack(padx=5, pady=3, side=tkinter.LEFT)

        customtkinter.CTkButton(
            settings_button,
            text="Ctrl",
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(10, 5), pady=5, side=tkinter.LEFT)
        customtkinter.CTkButton(
            settings_button,
            text=";",
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(5, 15), pady=5, side=tkinter.LEFT)

        settings_label = customtkinter.CTkLabel(
            settings_,
            text="Settings",
            font=("Segoe UI", 18, "bold"),
            fg_color="transparent",
            corner_radius=10,
        )
        settings_label.pack(padx=(10, 15), pady=5, side=tkinter.RIGHT)

        pin_ = customtkinter.CTkFrame(self.shortcuts_pane, fg_color="grey5")
        pin_.pack(padx=5, pady=5, fill=tkinter.X)

        pin_button = customtkinter.CTkFrame(pin_, fg_color="grey5")
        pin_button.pack(padx=5, pady=3, side=tkinter.LEFT)

        customtkinter.CTkButton(
            pin_button,
            text="Ctrl",
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(10, 5), pady=5, side=tkinter.LEFT)
        customtkinter.CTkButton(
            pin_button,
            text="P",
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(5, 15), pady=5, side=tkinter.LEFT)

        pin_label = customtkinter.CTkLabel(
            pin_,
            text="Pin Mode",
            font=("Segoe UI", 18, "bold"),
            fg_color="transparent",
            corner_radius=10,
        )
        pin_label.pack(padx=(10, 15), pady=5, side=tkinter.RIGHT)

        up_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/up.png")), size=(22, 22)
        )
        down_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/down.png")), size=(22, 22)
        )
        left_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/left.png")), size=(22, 22)
        )
        right_image = customtkinter.CTkImage(
            light_image=Image.open(self.resource_path("assets/right.png")),
            size=(22, 22),
        )

        up_ = customtkinter.CTkFrame(self.shortcuts_pane, fg_color="grey5")
        up_.pack(padx=5, pady=5, fill=tkinter.X)

        up_button = customtkinter.CTkFrame(up_, fg_color="grey5")
        up_button.pack(padx=5, pady=3, side=tkinter.LEFT)

        customtkinter.CTkButton(
            up_button,
            text="",
            image=up_image,
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(10, 5), pady=5, side=tkinter.LEFT)
        customtkinter.CTkLabel(
            up_button,
            text="or",
            font=("Segoe UI", 20),
            fg_color="transparent",
            corner_radius=10,
        ).pack(padx=0, pady=5, side=tkinter.LEFT)
        customtkinter.CTkButton(
            up_button,
            text="W",
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(5, 15), pady=5, side=tkinter.LEFT)

        up_label = customtkinter.CTkLabel(
            up_,
            text="Up",
            font=("Segoe UI", 18, "bold"),
            fg_color="transparent",
            corner_radius=10,
        )
        up_label.pack(padx=(10, 15), pady=5, side=tkinter.RIGHT)

        down_ = customtkinter.CTkFrame(self.shortcuts_pane, fg_color="grey5")
        down_.pack(padx=5, pady=5, fill=tkinter.X)

        down_button = customtkinter.CTkFrame(down_, fg_color="grey5")
        down_button.pack(padx=5, pady=3, side=tkinter.LEFT)

        customtkinter.CTkButton(
            down_button,
            text="",
            image=down_image,
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(10, 5), pady=5, side=tkinter.LEFT)
        customtkinter.CTkLabel(
            down_button,
            text="or",
            font=("Segoe UI", 20),
            fg_color="transparent",
            corner_radius=10,
        ).pack(padx=0, pady=5, side=tkinter.LEFT)
        customtkinter.CTkButton(
            down_button,
            text="S",
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(5, 15), pady=5, side=tkinter.LEFT)

        down_label = customtkinter.CTkLabel(
            down_,
            text="Down",
            font=("Segoe UI", 18, "bold"),
            fg_color="transparent",
            corner_radius=10,
        )
        down_label.pack(padx=(10, 15), pady=5, side=tkinter.RIGHT)

        left_ = customtkinter.CTkFrame(self.shortcuts_pane, fg_color="grey5")
        left_.pack(padx=5, pady=5, fill=tkinter.X)

        left_button = customtkinter.CTkFrame(left_, fg_color="grey5")
        left_button.pack(padx=5, pady=3, side=tkinter.LEFT)

        customtkinter.CTkButton(
            left_button,
            text="",
            image=left_image,
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(10, 5), pady=5, side=tkinter.LEFT)
        customtkinter.CTkLabel(
            left_button,
            text="or",
            font=("Segoe UI", 20),
            fg_color="transparent",
            corner_radius=10,
        ).pack(padx=0, pady=5, side=tkinter.LEFT)
        customtkinter.CTkButton(
            left_button,
            text="A",
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(5, 15), pady=5, side=tkinter.LEFT)

        left_label = customtkinter.CTkLabel(
            left_,
            text="Left",
            font=("Segoe UI", 18, "bold"),
            fg_color="transparent",
            corner_radius=10,
        )
        left_label.pack(padx=(10, 15), pady=5, side=tkinter.RIGHT)

        right_ = customtkinter.CTkFrame(self.shortcuts_pane, fg_color="grey5")
        right_.pack(padx=5, pady=5, fill=tkinter.X)

        right_button = customtkinter.CTkFrame(right_, fg_color="grey5")
        right_button.pack(padx=5, pady=3, side=tkinter.LEFT)

        customtkinter.CTkButton(
            right_button,
            text="",
            image=right_image,
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(10, 5), pady=5, side=tkinter.LEFT)
        customtkinter.CTkLabel(
            right_button,
            text="or",
            font=("Segoe UI", 20),
            fg_color="transparent",
            corner_radius=10,
        ).pack(padx=0, pady=5, side=tkinter.LEFT)
        customtkinter.CTkButton(
            right_button,
            text="D",
            fg_color="grey20",
            text_color="white",
            width=55,
            height=35,
            font=("Segoe UI", 18),
            corner_radius=8,
            hover_color="grey22",
        ).pack(padx=(5, 15), pady=5, side=tkinter.LEFT)

        right_label = customtkinter.CTkLabel(
            right_,
            text="Right",
            font=("Segoe UI", 18, "bold"),
            fg_color="transparent",
            corner_radius=10,
        )
        right_label.pack(padx=(10, 15), pady=5, side=tkinter.RIGHT)

    def change_continue_previous(self):
        with open(r"configs\\user_config.json", "r") as file:
            data = json.loads(file.read())
            data["continue_previous"] = not data["continue_previous"]

        with open(r"configs\\user_config.json", "w") as file:
            file.write(json.dumps(data))

        if self.continue_previous:
            self.continue_previous_button.configure(text="Apply", fg_color="grey12")
            self.continue_previous = False
        else:
            self.continue_previous_button.configure(text="Applied")
            try:
                self.continue_previous_button.configure(
                    fg_color=self.get_accent_color()
                )
            except Exception:
                pass

            self.continue_previous = True

    def change_start_pinned(self):
        with open(r"configs\\user_config.json", "r") as file:
            data = json.loads(file.read())
            data["start_pinned"] = not data["start_pinned"]

        with open(r"configs\\user_config.json", "w") as file:
            file.write(json.dumps(data))

        if self.start_pinned:
            self.start_pinned_button.configure(text="Apply", fg_color="grey12")
            self.start_pinned = False
        else:
            self.start_pinned_button.configure(text="Applied")
            try:
                self.start_pinned_button.configure(fg_color=self.get_accent_color())
            except Exception:
                pass

            self.start_pinned = True

    def change_color_scheme(self, scheme, button):
        with open(r"configs\\user_config.json", "r") as file:
            data = json.loads(file.read())
            data["color_scheme"] = scheme

        with open(r"configs\\user_config.json", "w") as file:
            file.write(json.dumps(data))

        self.current_color_scheme_button.configure(
            border_width=0,
            command=lambda x=self.color_scheme,
            y=self.current_color_scheme_button: self.change_color_scheme(x, y),
        )

        try:
            button.configure(border_width=2, border_color=self.get_accent_color())
        except Exception:
            pass

        self.current_color_scheme_button = button
        self.color_scheme = scheme

        with open(self.resource_path("assets/color_schemes.json"), "r") as file:
            data = json.loads(file.read())
            if self.color_scheme == "Random":
                ch = random.choice(list(data.keys()))
                self.color = data[ch]["color"]
                self.bg_color = data[ch]["bg_color"]
            else:
                self.color = data[self.color_scheme]["color"]
                self.bg_color = data[self.color_scheme]["bg_color"]

        self.paintGrid()

    def change_backdrop(self, style):
        with open(r"configs\\user_config.json", "r") as file:
            data = json.loads(file.read())
            data["backdrop_style"] = style

        with open(r"configs\\user_config.json", "w") as file:
            file.write(json.dumps(data))

        if self.current_backdrop_style == self.mica_button:
            current_text = "Mica"
        elif self.current_backdrop_style == self.acrylic_button:
            current_text = "Acrylic"
        elif self.current_backdrop_style == self.mica_alt_button:
            current_text = "Mica Alt"
        else:
            current_text = "Mica"

        self.current_backdrop_style.configure(text="Apply", fg_color="grey12")
        self.current_backdrop_style.configure(
            command=lambda: self.change_backdrop(current_text)
        )

        if style == "Mica":
            self.current_backdrop_style = self.mica_button
        elif style == "Acrylic":
            self.current_backdrop_style = self.acrylic_button
        elif style == "Mica Alt":
            self.current_backdrop_style = self.mica_alt_button

        try:
            self.current_backdrop_style.configure(
                text="Restart",
                fg_color=self.get_accent_color(),
                command=self.restart_app,
            )
        except Exception:
            pass

    def change_window_style(self, style):
        with open(r"configs\\user_config.json", "r") as file:
            data = json.loads(file.read())
            data["window_style"] = style

        with open(r"configs\\user_config.json", "w") as file:
            file.write(json.dumps(data))

        if self.current_window_style == self.win7_button:
            current_text = "Win7"
        elif self.current_window_style == self.defualt_button:
            current_text = "Default"
        elif self.current_window_style == self.inverse_button:
            current_text = "Inverse"
        else:
            current_text = "Default"

        self.current_window_style.configure(text="Apply", fg_color="grey12")
        self.current_window_style.configure(
            command=lambda: self.change_window_style(current_text)
        )

        if style == "Win7":
            self.current_window_style = self.win7_button
        elif style == "Default":
            self.current_window_style = self.defualt_button
        elif style == "Inverse":
            self.current_window_style = self.inverse_button
        else:
            self.current_window_style = self.defualt_button

        try:
            self.current_window_style.configure(
                text="Restart",
                fg_color=self.get_accent_color(),
                command=self.restart_app,
            )
        except Exception:
            pass

    def pin(self, e=None):
        if self.window.wm_attributes("-topmost") == 1:
            self.window.withdraw()
            self.window.bind("<Control-;>", self.settings)

            hPyT.title_bar.unhide(window=self.window)
            self.window.wm_attributes("-topmost", 0)
            self.pin_button.configure(image=self.pin_image)
            self.pin_button2.place_forget()

            self.window.wm_geometry(self._previous_geometry)
            pywinstyles.change_border_color(self.window, color="#353535")

            self.frame.pack_forget()

            self.frame_top.pack(padx=10, pady=10, fill=tkinter.BOTH, expand=True)
            self.frame.pack(padx=10, pady=10, fill=tkinter.BOTH, expand=True)

            self.window.deiconify()

        else:
            self.window.withdraw()
            self.frame_top.pack_forget()
            self.window.unbind("<Control-;>")

            self.pin_button2 = customtkinter.CTkButton(
                self.frame,
                text="",
                image=self.unpin_image,
                fg_color="grey12",
                corner_radius=6,
                width=20,
                height=30,
                hover_color="grey17",
                command=self.pin,
            )
            self.pin_button2.place(x=10, y=5)

            self._previous_geometry = self.window.wm_geometry()
            for i in get_monitors():
                if i.is_primary:
                    width = i.width
            window_width = self.window.winfo_width()

            try:
                pywinstyles.change_border_color(self.window, self.get_accent_color())
            except Exception:
                pass

            if self.n == 4:
                self.window.geometry(f"400x450+{width - (window_width + 50)}+50")
            elif self.n == 5:
                self.window.geometry(f"500x550+{width - (window_width + 50)}+50")

            hPyT.title_bar.hide(window=self.window)
            self.window.wm_attributes("-topmost", 1)
            self.pin_button.configure(image=self.unpin_image)
            self.window.deiconify()

    def get_accent_color(self):
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM"
        )
        # Query the value of the ColorizationAfterglow property
        value, type = winreg.QueryValueEx(key, "ColorizationAfterglow")
        # Close the registry key
        winreg.CloseKey(key)
        # Return the value as a hexadecimal string

        if len(hex(value)[4:]) == 6:
            return "#" + hex(value)[4:]
        else:
            return "#" + hex(value)[2:]

    def settings_back(self, e=None):
        self.settings_pane.pack_forget()
        self.frame_top.pack(padx=10, pady=10, fill=tkinter.BOTH, expand=True)
        self.frame.pack(padx=10, pady=10, fill=tkinter.BOTH, expand=True)
        self.window.unbind("<BackSpace>")

        self.window.bind("<Control-;>", self.settings)
        self.window.bind("<Control-r>", self.restart_game)
        self.window.bind("<Control-p>", self.pin)
        self.window.bind("<Control-z>", lambda event: self.undo())
        self.window.bind("u", lambda event: self.undo())

    def shortcuts_back(self, e=None):
        self.shortcuts_pane.pack_forget()
        self.settings_pane.pack(
            padx=(3, 0), pady=(0, 10), fill=tkinter.BOTH, expand=True
        )

    def restart_game(self, e=None):
        with open(self.resource_path("assets/color_schemes.json"), "r") as file:
            data = json.loads(file.read())
            if self.color_scheme == "Random":
                ch = random.choice(list(data.keys()))
                self.color = data[ch]["color"]
                self.bg_color = data[ch]["bg_color"]
            else:
                self.color = data[self.color_scheme]["color"]
                self.bg_color = data[self.color_scheme]["bg_color"]

        self.score = 0
        self.previous_undo_stack = copy.deepcopy(self.undo_stack)

        self.undo_stack = []

        for i in range(self.n):
            for j in range(self.n):
                self.gridCell[i][j] = 0
        self.random_cell()
        self.random_cell()
        self.paintGrid()
        self.game_score.configure(text="Score : " + str(self.score))

        global game2048
        game2048.restart_game()

    def undo(self):
        try:
            if len(self.undo_stack) < 1:
                self.undo_stack = copy.deepcopy(self.previous_undo_stack)
                self.previous_undo_stack = []
        except Exception:
            pass

        if len(self.undo_stack) > 0:
            # Pop the previous game state from the undo stack
            score, previous_state = self.undo_stack.pop()

            try:
                self.gridCell = self.undo_stack[-1][1]  # previous_state
                self.score = self.undo_stack[-1][0]  # score
            except Exception:
                try:
                    self.gridCell = previous_state
                    self.score = score
                except Exception:
                    pass

            try:
                if self.game2048.won or self.game2048.end:
                    self.game2048.restart_game()
            except Exception:
                try:
                    global game2048
                    self.game2048 = game2048
                    if self.game2048.won or self.game2048.end:
                        self.game2048.restart_game()
                except Exception:
                    pass

            self.game_score.configure(text="Score : " + str(self.score))
            self.paintGrid()

    def reverse(self):
        for ind in range(self.n):
            i = 0
            j = self.n - 1
            while i < j:
                self.gridCell[ind][i], self.gridCell[ind][j] = (
                    self.gridCell[ind][j],
                    self.gridCell[ind][i],
                )
                i += 1
                j -= 1

    def transpose(self):
        self.gridCell = [list(t) for t in zip(*self.gridCell)]

    def compressGrid(self):
        self.compress = False
        temp = [[0] * self.n for i in range(self.n)]
        for i in range(self.n):
            cnt = 0
            for j in range(self.n):
                if self.gridCell[i][j] != 0:
                    temp[i][cnt] = self.gridCell[i][j]
                    if cnt != j:
                        self.compress = True
                    cnt += 1
        self.gridCell = temp

    def mergeGrid(self):
        self.merge = False
        for i in range(self.n):
            for j in range(self.n - 1):
                if (
                    self.gridCell[i][j] == self.gridCell[i][j + 1]
                    and self.gridCell[i][j] != 0
                ):
                    self.gridCell[i][j] *= 2
                    self.gridCell[i][j + 1] = 0
                    self.score += self.gridCell[i][j]
                    self.merge = True

    def random_cell(self):
        cells = []
        for i in range(self.n):
            for j in range(self.n):
                if self.gridCell[i][j] == 0:
                    cells.append((i, j))
        curr = random.choice(cells)
        i = curr[0]
        j = curr[1]
        self.gridCell[i][j] = 2

    def can_merge(self):
        for i in range(self.n):
            for j in range(self.n - 1):
                if self.gridCell[i][j] == self.gridCell[i][j + 1]:
                    return True

        for i in range(self.n - 1):
            for j in range(self.n):
                if self.gridCell[i + 1][j] == self.gridCell[i][j]:
                    return True
        return False

    def paintGrid(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.gridCell[i][j] == 0:
                    self.board[i][j].configure(text="", fg_color="grey12")
                else:
                    if self.gridCell[i][j] >= 1024:
                        self.board[i][j].configure(
                            text=str(self.gridCell[i][j]),
                            fg_color=self.bg_color.get(str(self.gridCell[i][j])),
                            text_color=self.color.get(str(self.gridCell[i][j])),
                            font=("Segoe UI", 30, "bold"),
                        )
                    else:
                        self.board[i][j].configure(
                            text=str(self.gridCell[i][j]),
                            fg_color=self.bg_color.get(str(self.gridCell[i][j])),
                            text_color=self.color.get(str(self.gridCell[i][j])),
                            font=("Segoe UI", 40, "bold"),
                        )

    def load_high_score(self):
        try:
            with open(r"configs\\user_config.json", "r") as file:
                try:
                    data = json.loads(file.read())
                    self.high_score = int(data["high_score"])
                except Exception:
                    self.high_score = 0
        except FileNotFoundError:
            self.high_score = 0

    def save_high_score(self):
        with open(r"configs\\user_config.json", "r") as file:
            data = json.loads(file.read())
            data["high_score"] = str(self.high_score)

        with open(r"configs\\user_config.json", "w") as file:
            file.write(json.dumps(data))

    def custom_game_message_box(self, window_title, title, message, img):
        def ask():
            root = customtkinter.CTkToplevel(self.root1)
            root.title(window_title)
            root.geometry("370x160+9000+9000")
            root.transient(self.window)
            root.grab_set_global()
            root.configure(fg_color="black")
            winsound.MessageBeep(winsound.MB_ICONHAND)

            try:
                pywinstyles.change_border_color(root, self.get_accent_color())
            except Exception:
                pass

            def new_game(e=None):
                self.restart_game()
                root.grab_release()
                self.root1.destroy()
                root.destroy()

            def no(e=None):
                root.grab_release()
                self.root1.destroy()
                root.destroy()

            top_frame = customtkinter.CTkFrame(root, fg_color="black")

            app_name_label_frame = customtkinter.CTkFrame(top_frame, fg_color="black")
            app_name_label = customtkinter.CTkLabel(
                app_name_label_frame, text=title, font=("Segoe UI", 25, "bold")
            )
            app_name_label.pack(pady=(5, 0), side="left", padx=20)
            app_name_label_frame.grid(row=0, column=0, sticky="w")

            description_frame = customtkinter.CTkFrame(top_frame, fg_color="black")
            description_label = customtkinter.CTkLabel(
                description_frame, text=message, font=("Segoe UI", 13)
            )
            description_label.pack(pady=(0, 10), side="left", padx=(20, 70))
            description_frame.grid(row=1, column=0, sticky="w")

            img_frame = customtkinter.CTkFrame(
                top_frame, fg_color="black", width=150, height=80
            )
            img_frame.grid(row=0, column=1, rowspan=2, sticky="w", padx=0)

            game_over_button = customtkinter.CTkButton(
                img_frame,
                image=img,
                fg_color="black",
                width=80,
                height=80,
                text="",
                hover=False,
            )
            game_over_button.pack(padx=(20, 0), pady=0, side="right")

            top_frame.pack()

            bottom_frame = customtkinter.CTkFrame(root, fg_color="grey16")
            bottom_frame.pack(fill="both", expand=True)

            button_frame = customtkinter.CTkFrame(bottom_frame, fg_color="grey16")

            ok_button = customtkinter.CTkButton(
                button_frame,
                text="New Game",
                fg_color="black",
                font=("Segoe UI", 15),
                command=lambda: new_game(),
                width=110,
                height=35,
                hover_color="grey3",
            )
            ok_button.pack(padx=(40, 0), pady=15, side="left")

            restart_button = customtkinter.CTkButton(
                button_frame,
                text="No",
                fg_color="black",
                font=("Segoe UI", 15),
                command=lambda: no(),
                width=110,
                height=35,
                hover_color="grey3",
            )
            restart_button.pack(padx=(0, 40), pady=15, side="right")

            button_frame.pack(fill="both", expand=True)

            ApplyMica(HWND=root.frame(), Theme=MicaTheme.DARK, Style=MicaStyle.ALT)
            hPyT.title_bar.hide(root)

            root.update_idletasks()
            root.update()
            root.geometry("+9000+9000")
            hPyT.window_frame.center_relative(self.window, root)
            root.focus()
            # root.mainloop()

        self.root1 = customtkinter.CTkToplevel(self.window)
        self.root1.title("")
        self.root1.geometry("0x0+9000+9000")

        self.root1.transient(self.window)
        self.root1.grab_set_global()
        self.root1.configure(fg_color="black")

        self.root1.after(10, self.root1.focus)
        self.root1.wm_attributes("-alpha", 0.5)

        if self.window.attributes("-topmost") == 1:
            hPyT.title_bar.hide(window=self.root1)
        else:
            hPyT.all_stuffs.hide(window=self.root1)

        self.root1.wm_geometry(self.window.wm_geometry())
        ApplyMica(HWND=self.root1.frame(), Theme=MicaTheme.DARK, Style=MicaStyle.ALT)

        t1 = threading.Thread(target=ask)
        t1.start()

        self.root1.mainloop()

    def game_reset_box(
        self, window_title, title, message, img, button1_text, button2_text, size
    ):
        def ask():
            root = customtkinter.CTkToplevel(self.root1)
            root.title(window_title)
            root.geometry("370x160+9000+9000")
            root.transient(self.window)
            root.grab_set_global()
            root.configure(fg_color="black")
            winsound.MessageBeep(winsound.MB_ICONHAND)

            try:
                pywinstyles.change_border_color(root, self.get_accent_color())
            except Exception:
                pass

            def reset(e=None):
                try:
                    os.remove(r"configs\\game_state.json")
                except Exception:
                    pass

                with open(r"configs\\user_config.json", "r") as file:
                    data = json.loads(file.read())
                    data["grid_size"] = size
                with open(r"configs\\user_config.json", "w") as file:
                    json.dump(data, file)

                os.execl(sys.executable, sys.executable, *sys.argv)

            def no(e=None):
                root.grab_release()
                self.root1.destroy()
                root.destroy()

            top_frame = customtkinter.CTkFrame(root, fg_color="black")

            app_name_label_frame = customtkinter.CTkFrame(top_frame, fg_color="black")
            app_name_label = customtkinter.CTkLabel(
                app_name_label_frame, text=title, font=("Segoe UI", 18, "bold")
            )
            app_name_label.pack(pady=(5, 0), side="left", padx=(20, 10))
            app_name_label_frame.grid(row=0, column=0, sticky="w")

            description_frame = customtkinter.CTkFrame(top_frame, fg_color="black")
            description_label = customtkinter.CTkLabel(
                description_frame, text=message, font=("Segoe UI", 12)
            )
            description_label.pack(pady=(0, 10), side="left", padx=(20, 50))
            description_frame.grid(row=1, column=0, sticky="w")

            img_frame = customtkinter.CTkFrame(
                top_frame, fg_color="black", width=150, height=80
            )
            img_frame.grid(row=0, column=1, rowspan=2, sticky="w", padx=0)

            img_button = customtkinter.CTkButton(
                img_frame,
                image=img,
                fg_color="black",
                width=80,
                height=80,
                text="",
                hover=False,
            )
            img_button.pack(padx=(0, 0), pady=0, side="right")

            top_frame.pack()

            bottom_frame = customtkinter.CTkFrame(root, fg_color="grey16")
            bottom_frame.pack(fill="both", expand=True)

            button_frame = customtkinter.CTkFrame(bottom_frame, fg_color="grey16")

            button1 = customtkinter.CTkButton(
                button_frame,
                text=button1_text,
                fg_color="black",
                font=("Segoe UI", 15),
                command=lambda: reset(),
                width=110,
                height=35,
                hover_color="grey3",
            )
            button1.pack(padx=(40, 0), pady=15, side="left")

            button2 = customtkinter.CTkButton(
                button_frame,
                text=button2_text,
                fg_color="black",
                font=("Segoe UI", 15),
                command=lambda: no(),
                width=110,
                height=35,
                hover_color="grey3",
            )
            button2.pack(padx=(0, 20), pady=15, side="right")

            button_frame.pack(fill="both", expand=True)

            ApplyMica(HWND=root.frame(), Theme=MicaTheme.DARK, Style=MicaStyle.ALT)
            hPyT.title_bar.hide(root)

            root.update_idletasks()
            root.update()
            root.geometry("+9000+9000")
            hPyT.window_frame.center_relative(self.window, root)
            root.focus()
            # root.mainloop()

        self.root1 = customtkinter.CTkToplevel(self.window)
        self.root1.title("")
        self.root1.geometry("0x0+9000+9000")

        self.root1.transient(self.window)
        self.root1.grab_set_global()
        self.root1.configure(fg_color="black")

        self.root1.after(10, self.root1.focus)
        self.root1.wm_attributes("-alpha", 0.5)

        if self.window.attributes("-topmost") == 1:
            hPyT.title_bar.hide(window=self.root1)
        else:
            hPyT.all_stuffs.hide(window=self.root1)

        self.root1.wm_geometry(self.window.wm_geometry())
        ApplyMica(HWND=self.root1.frame(), Theme=MicaTheme.DARK, Style=MicaStyle.ALT)

        t1 = threading.Thread(target=ask)
        t1.start()

        self.root1.mainloop()


class Game:
    def __init__(self, gamepanel):
        self.gamepanel = gamepanel
        self.end = False
        self.won = False

    def start(self):
        if not self.gamepanel.continue_previous and not len(sys.argv) > 1:
            self.gamepanel.random_cell()
            self.gamepanel.random_cell()

        self.gamepanel.load_high_score()
        self.gamepanel.paintGrid()
        self.gamepanel.window.bind("<Key>", self.link_keys)

        self.gamepanel.window.mainloop()

    def restart_game(self):
        self.end = False
        self.won = False

    def link_keys(self, event):
        if self.end or self.won:
            return

        self.gamepanel.compress = False
        self.gamepanel.merge = False
        self.gamepanel.moved = False

        pressed_key = event.keysym

        directions = ["Up", "Down", "Left", "Right"]

        # Map pressed key to its respective direction
        if pressed_key in ("Up", "w"):
            directions.remove("Up")
        elif pressed_key in ("Down", "s"):
            directions.remove("Down")
        elif pressed_key in ("Left", "a"):
            directions.remove("Left")
        elif pressed_key in ("Right", "d"):
            directions.remove("Right")
        else:
            return  # Ignore other keys

        random_direction = random.choice(directions)

        if random_direction == "Up":
            self.gamepanel.transpose()
            self.gamepanel.compressGrid()
            self.gamepanel.mergeGrid()
            self.gamepanel.moved = self.gamepanel.compress or self.gamepanel.merge
            self.gamepanel.compressGrid()
            self.gamepanel.transpose()

        elif random_direction == "Down":
            self.gamepanel.transpose()
            self.gamepanel.reverse()
            self.gamepanel.compressGrid()
            self.gamepanel.mergeGrid()
            self.gamepanel.moved = self.gamepanel.compress or self.gamepanel.merge
            self.gamepanel.compressGrid()
            self.gamepanel.reverse()
            self.gamepanel.transpose()

        elif random_direction == "Left":
            self.gamepanel.compressGrid()
            self.gamepanel.mergeGrid()
            self.gamepanel.moved = self.gamepanel.compress or self.gamepanel.merge
            self.gamepanel.compressGrid()

        elif random_direction == "Right":
            self.gamepanel.reverse()
            self.gamepanel.compressGrid()
            self.gamepanel.mergeGrid()
            self.gamepanel.moved = self.gamepanel.compress or self.gamepanel.merge
            self.gamepanel.compressGrid()
            self.gamepanel.reverse()

        if self.gamepanel.moved:
            self.gamepanel.undo_stack.append([
                self.gamepanel.score,
                copy.deepcopy(self.gamepanel.gridCell),
            ])

        self.gamepanel.paintGrid()
        gamepanel.game_score.configure(text="Score : " + str(self.gamepanel.score))

        flag = 0
        for i in range(self.gamepanel.n):
            for j in range(self.gamepanel.n):
                if self.gamepanel.gridCell[i][j] == 2048:
                    flag = 1
                    break

        if flag == 1:  # found 2048
            self.won = True
            self.gamepanel.custom_game_message_box(
                "You Won",
                "You Won",
                "Do you want your OS to be removed?",
                self.gamepanel.game_won_image,
            )
            return

        for i in range(self.gamepanel.n):
            for j in range(self.gamepanel.n):
                if self.gamepanel.gridCell[i][j] == 0:
                    flag = 1
                    break

        if not (flag or self.gamepanel.can_merge()):
            self.end = True
            self.gamepanel.custom_game_message_box(
                "Game Over",
                "Game Over",
                "Do you want to start again?",
                self.gamepanel.game_over_image,
            )
            return

        if self.gamepanel.moved:
            self.gamepanel.random_cell()

        self.gamepanel.paintGrid()

        if self.gamepanel.score > self.gamepanel.high_score:
            self.gamepanel.high_score = self.gamepanel.score
            self.gamepanel.save_high_score()
            self.gamepanel.high_score_label.configure(
                text=str(self.gamepanel.high_score)
            )


gamepanel = Board()
game2048 = Game(gamepanel)
game2048.start()
