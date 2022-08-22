#!/bin/bash
pyinstaller main.py \
--name "Tolio" \
--icon='icon.icns' \
--onefile \
--windowed \
--runtime-hook hook.py \
--add-data "images/*.jpg:images" \
--add-data "portfolio.db:." \
--hidden-import tkinter \
--hidden-import PIL \
--hidden-import sqlite3 \
--hidden-import PIL._ImageTk \
--hidden-import PIL.Image \
--debug=all \
--clean
