#!/usr/bin/env python3.8
# 
# This script requires pyTermTK which requires python3.8, install like so:
#
# sudo apt install python3.8
# python3.8 -m pip install pyTermTK
#

import atexit
import os
import time
import traceback
import threading
from servie.client import Client

try:
  import TermTk as ttk
  from TermTk.TTkCore.constant import TTkK
except ImportError:
  print("pyTermTK not installed, install it like so:")
  print("python3.8 -m pip install pyTermTK")
  raise SystemExit(1)


USERNAME = 'vqro'
SERVER_IP = '192.168.86.49'
SERVER_PORT = 4242


### Constants/Config
TERMSIZE = os.get_terminal_size()
DEBUG_LOGGING = True
WIDE = int(TERMSIZE.columns * 0.9)  # 90% screen width
CENTER_X = int(TERMSIZE.columns * 0.5)
CENTER_Y = int(TERMSIZE.lines * 0.5)


### Utilities
if DEBUG_LOGGING:
  _debug_log = open('debug.log', 'a')

  @atexit.register
  def bye():
    debug('atexit, closing log')
    _debug_log.close()


def debug(msg):
  if DEBUG_LOGGING:
    ttk.TTkLog.debug(msg)
    print(f'[{time.ctime()}]  {msg}', file=_debug_log)

debug(f'process pid {os.getpid()} started')

def center(text):
  lines = text.splitlines()
  half_screen = CENTER_X
  for i, line in enumerate(list(lines)):
    half_line = int(len(line) * 0.5)
    padding = max(0, half_screen - half_line)
    lines[i] = (' ' * padding) + line

  return '\n'.join(lines)


### Components

class ChatClientApp:
  """Main client logic"""

  def __init__(self):
    self.ui = ChatClientUI(self)
    self.client = Client(SERVER_IP, SERVER_PORT)

    # Initialize UI
    self.ui.gamelog_append(center('#' * 50))
    self.ui.gamelog_append(center('TTK Chat Client v9000# (Whammy Bar edition)'))
    self.ui.gamelog_append(center('#' * 50))

  def run(self):
    self.ui.run()

  def command_entered(self, command):
    """This gets called when the user types a command and hits enter."""
    debug(f'command_entered: {command}')
    self.ui.gamelog_append(command)
    try:
      self.handle_command(command)
    except (SystemExit, KeyboardInterrupt):
      raise SystemExit()
    except:
      self.ui.gamelog_append(traceback.format_exc())

  def handle_command(self, command):
    if command == 'quit':
      raise SystemExit(0)

    if command.startswith('connect '):
      host = command.split()[1]
      ip, port = host.split(':')
      port = str(int(port))
      self.do_connect(ip, port)

  def do_connect(self, ip, port):
    self.server = (ip, port)
    assert False, f"I should connect to {self.server}"


class ChatClientUI:
  """Contains all the TTk objects and layout, no logic."""
  gamelog_max_lines = 500

  def __init__(self, app):
    self.app = app
    self.root = ttk.TTk()

    self.win = ttk.TTkWindow(
      parent=self.root,
      size=(TERMSIZE.columns,TERMSIZE.lines),
      title="TTK Chat Client v0.0.0.0.000.0.9-beta-alpha-gamma-lambda++",
      # This win has a big top portion (gamelog_frame) and a smaller
      # portion below it (input_frame) for user input.
      layout=ttk.TTkVBoxLayout(),
    )
    self.create_top_frame()
    self.create_input_frame()

  def run(self):
    self.root.mainloop()

  def create_top_frame(self):
    self.top_frame = ttk.TTkFrame(
      parent=self.win,
      border=False,
      layout=ttk.TTkVBoxLayout(),
    )
    self.menu_frame = ttk.TTkFrame(
      parent=self.top_frame,
      border=False,
      maxHeight=1,
    )
    #self.create_menus()

    self.gamelog_frame = ttk.TTkFrame(
      parent=self.top_frame,
      layout=ttk.TTkVBoxLayout(),
      border=True,
    )
    self.gamelog_textedit = ttk.TTkTextEdit(
      parent=self.gamelog_frame,
      border=True,
    )
    self.gamelog_textedit.setLineWrapMode(TTkK.WidgetWidth)
    self.gamelog_textedit.setReadOnly(True)
    self.gamelog_text = ''  # Manually track this

  def create_menus(self):
    # Not sure how to actually interact with these... so maybe throw this away
    fileMenu = self.menu_frame.menubarTop().addMenu('&File')
    fileMenu.addMenu('Open')
    fileMenu.addMenu('Close')

  def set_gamelog_text(self, text):
    # Only keep the last self.gamelog_max_lines of text around.
    text = '\n'.join(text.splitlines()[-self.gamelog_max_lines:])
    self.gamelog_textedit.setReadOnly(False)
    self.gamelog_textedit.setText(text)
    self.gamelog_textedit.setReadOnly(True)
    self.gamelog_text = text
    # Ultra hack to to "scroll to bottom of the text area"... why is this not easy?
    self.gamelog_textedit._textEditView._scrolToInclude(99999999, 999999999)

  def gamelog_append(self, text):
    new_text = self.gamelog_text + ('\n' if self.gamelog_text else '') + text
    self.set_gamelog_text(new_text)

  def create_input_frame(self):
    self.input_frame = ttk.TTkFrame(
      parent=self.win,
      layout=ttk.TTkVBoxLayout(),
      border=True,
    )

    # Status Frame = [LeftFrame,RightFrame], which each have labels
    self.status_frame = ttk.TTkFrame(
      parent=self.input_frame,
      border=True,
      layout=ttk.TTkHBoxLayout(),
      maxHeight=5,
    )
    status_frame_left = ttk.TTkFrame(
      parent=self.status_frame,
      border=False,
      layout=ttk.TTkVBoxLayout(),
    )
    ttk.TTkFrame(parent=self.status_frame, border=False, layout=ttk.TTkVBoxLayout(), minWidth=16)
    status_frame_right = ttk.TTkFrame(
      parent=self.status_frame,
      border=False,
      layout=ttk.TTkVBoxLayout(),
    )

    def add_label(name, value, parent):
      frame = ttk.TTkFrame(parent=parent, border=False, layout=ttk.TTkHBoxLayout())
      ttk.TTkLabel(parent=frame, text=name, maxWidth=16)
      return ttk.TTkLabel(parent=frame, text=value)

    self.username_label = add_label("Username", USERNAME, status_frame_right)
    self.server_value_label = add_label("Server", f"{SERVER_IP}:{SERVER_PORT}", status_frame_right)
    
    self.input_line = ttk.TTkLineEdit(
      parent=self.input_frame,
      border=True,
    )
    self.input_line.setFocus()
    self.input_line.returnPressed.connect(self.input_line_return)

  def input_line_return(self):
    command = self.input_line.text().strip()
    self.input_line.setText("")
    if command:
      self.app.command_entered(command)


app = ChatClientApp()
app.run()
