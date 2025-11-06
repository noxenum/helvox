import tkinter as tk

from helvox.app import App


def main():
    root = tk.Tk()
    _ = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
