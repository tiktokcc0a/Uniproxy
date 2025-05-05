import os
import sys
import tkinter as tk
from ui import UniproxyApp

def main():
    root = tk.Tk()
    app = UniproxyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
