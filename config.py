import os
import sys

copied_things = []
show_time = []
monitoring = True
stop = False
image_references = []
folder_to_save = ''
show_warning = False

if getattr(sys, 'frozen', False):
    exec_dir = os.path.dirname(sys.executable)
else:
    exec_dir = os.path.dirname(os.path.abspath(__file__))

appdata_dir = os.path.join(os.environ['APPDATA'], 'Clipy')
if not os.path.exists(appdata_dir):
    os.makedirs(appdata_dir)

root_folder = appdata_dir
settings_path = os.path.join(root_folder, 'settings.json')

folder_path = ''
background_color = ''
