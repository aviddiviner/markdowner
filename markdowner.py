#!/usr/bin/env python
# Based on code from http://www.jezra.net/blog/A_markdown_editorviewer_in_Python
# GPLv3 and copyright 2010 Jezra
import os
import sys
import gtk
import pango
import webkit
import markdown # http://www.freewisdom.org/projects/python-markdown/

# Resolve a chain of symbolic links by returning the absolute path name of the final target.
# Used to find the folder containing this script and its resources (.png icon).
# Raises os.error exception in case of circular link.
def resolve_link(path):
  try:
    os.stat(path)
  except os.error, err:
    # do not raise exception in case of broken symlink;
    # we want to know the final target anyway
    if err.errno == errno.ENOENT:
      pass
    else:
      raise
  if not os.path.isabs(path):
    basedir = os.path.dirname(os.path.abspath(path))
  else:
    basedir = os.path.dirname(path)
  p = path
  while os.path.islink(p):
    p = os.readlink(p)
    if not os.path.isabs(p):
      p = os.path.join(basedir, p)
      basedir = os.path.dirname(p)
  return os.path.join(basedir, p)

# Check command line options
try:
  global default_file
  default_file = sys.argv[1]
except:
  print "Usage:", os.path.basename(sys.argv[0]), "<filename>"
  exit(1)

class application:
  def __init__(self):
    # Build the UI
    winder = gtk.Window(gtk.WINDOW_TOPLEVEL)
    winder.set_title(os.path.basename(default_file) + " - markdowner")
    winder.set_position(gtk.WIN_POS_CENTER)
    winder.set_size_request(1024, 768)
    ##winder.maximize()

    # File menu
    filemenu = gtk.Menu()
    filem = gtk.MenuItem("_File",use_underline=True)
    filem.set_submenu(filemenu)

    agr = gtk.AccelGroup()
    winder.add_accel_group(agr)

    fsave = gtk.MenuItem("Save")
    fsave.connect("activate", self.save)
    key, mod = gtk.accelerator_parse("<Control>S")
    fsave.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
    filemenu.append(fsave)

    frend = gtk.MenuItem("Render")
    frend.connect("activate", self.markdown)
    key, mod = gtk.accelerator_parse("<Control>R")
    frend.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
    filemenu.append(frend)

    sep = gtk.SeparatorMenuItem()
    filemenu.append(sep)

    fexit = gtk.MenuItem("Exit")
    fexit.connect("activate", self.quit)
    key, mod = gtk.accelerator_parse("<Control>Q")
    fexit.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
    filemenu.append(fexit)

    # Help menu
    helpmenu = gtk.Menu()
    helpm = gtk.MenuItem("_Help",use_underline=True)
    helpm.set_submenu(helpmenu)

    about = gtk.MenuItem("About")
    about.connect("activate", self.about_dialog)
    helpmenu.append(about)

    # Build the window box
    box = gtk.VBox(False)
    winder.add(box)

    # Build the menu bar and add it to the box
    mb = gtk.MenuBar()
    mb.append(filem)
    mb.append(helpm)
    box.pack_start(mb, False, False, 0)

    # Add a pane to the box
    pane = gtk.HPaned()
    box.pack_start(pane)

    # Do the text processing for the first pane
    self.tb = gtk.TextBuffer()
    tv = gtk.TextView(self.tb)
    tv.set_wrap_mode(gtk.WRAP_WORD)

    # Try to add spell checking to the textview if possible
    try:
      import gtkspell
      self.spell = gtkspell.Spell(tv)
      self.has_spell_library=True
    except Exception:
      self.has_spell_library=False
      print Exception.message

    # Use a nice monospace font
    fontdesc = pango.FontDescription("monospace 10")
    tv.modify_font(fontdesc)

    # Add the text view to a scrollable window
    input_scroll = gtk.ScrolledWindow()
    input_scroll.add_with_viewport(tv)
    input_scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

    # Add it to the pane
    pane.pack1(input_scroll,True)

    # Make the HTML viewable area
    self.wv = webkit.WebView()

    # Disable the plugins for the webview
    ws = self.wv.get_settings()
    ws.set_property('enable-plugins',False)
    self.wv.set_settings(ws)
    out_scroll = gtk.ScrolledWindow()
    out_scroll.add(self.wv)
    out_scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
    pane.add2(out_scroll)

    # Add a statusbar
    winder.statusbar = gtk.Statusbar()
    box.pack_start(winder.statusbar, False, False, 0)
    #subprocess.Popen(["python", "Helloworld.py"])

    # Display the window
    winder.connect("destroy", self.quit)
    icopath = os.path.join(os.path.dirname(resolve_link(__file__)), 'markdowner.png')
    ico = gtk.gdk.pixbuf_new_from_file(icopath)
    winder.set_icon(ico)
    winder.show_all()

    # Read file and render the markdown
    winder.statusbar.push(0, os.path.abspath(default_file))
    self.read_default_file()
    self.markdown()

    # Set callback for textbuffer changes
    self.winder = winder
    self.tb.connect("changed", self.text_modified)

  def about_dialog(self,widget=None):
    dialog = gtk.MessageDialog(
               parent = self.winder,
               flags = gtk.DIALOG_DESTROY_WITH_PARENT,
               type = gtk.MESSAGE_INFO,
               buttons = gtk.BUTTONS_OK,
               message_format = "Based on code from http://www.jezra.net/blog\nGPLv3, Copyright (c) 2010 Jezra, (c) 2011 aviddiviner"
             )
    dialog.set_title('About markdowner')
    dialog.connect('response', lambda dialog, response: dialog.destroy())
    dialog.show()

  def text_modified(self, textbuf):
    self.winder.set_title("*" + os.path.basename(default_file) + " - markdowner")

  def run(self):
    # Set the program icon
    statusIcon = gtk.StatusIcon()
    statusIcon.set_from_file("page-down-icon.png")
    statusIcon.set_visible(True)
    gtk.main()
    
  def quit(self,widget=None):
    ##self.save()
    gtk.main_quit()
  
  def markdown(self,widget=None):
    text = self.get_buffer_text()
    mdtext = markdown.markdown(text)
    self.wv.load_html_string(mdtext,"file:///")
  
  def read_default_file(self):
    try:
      f = open(default_file,"r")
      text = f.read()
      self.tb.set_text(text)
      f.close()
    except:
      pass
    
  def quit_accel(self,accel_group, acceleratable, keyval, modifier):
    self.quit()
  
  def save_accel(self,accel_group, acceleratable, keyval, modifier):
    self.save()
    
  def save(self,widget=None):
    text = self.get_buffer_text()
    f = open(default_file,"w")
    f.write(text)
    f.close()
    self.winder.set_title(os.path.basename(default_file) + " - markdowner")
    
  def get_buffer_text(self):
    start_iter = self.tb.get_start_iter()
    end_iter = self.tb.get_end_iter()
    text = self.tb.get_text(start_iter,end_iter)
    return text
    
if __name__=="__main__":
  a = application()
  a.run()
  
