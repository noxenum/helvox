import tkinter as tk


class RoundedCanvas(tk.Canvas):
    def __init__(
        self,
        parent,
        bg="#000000",
        height=50,
        corner_radius=20,
    ):
        tk.Canvas.__init__(
            self,
            parent,
            height=height,
            highlightthickness=0,
        )

        self.bg = bg
        self.corner_radius = corner_radius

        # Bind to Configure event to redraw when size changes
        self.bind("<Configure>", lambda e: self.draw_canvas())

    def draw_canvas(self):
        # Clear previous drawings
        self.delete("rounded_bg")

        # Get actual canvas dimensions
        width = self.winfo_width()
        height = self.winfo_height()
        radius = self.corner_radius

        # Create rounded rectangle using polygon
        points = [
            radius,
            0,
            width - radius,
            0,
            width,
            0,
            width,
            radius,
            width,
            height - radius,
            width,
            height,
            width - radius,
            height,
            radius,
            height,
            0,
            height,
            0,
            height - radius,
            0,
            radius,
            0,
            0,
        ]

        self.create_polygon(
            points, fill=self.bg, smooth=True, outline=self.bg, tags="rounded_bg"
        )
