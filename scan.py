#!/usr/bin/env python3
#
# scan.py - scan documents on the Canon pixma MX922
#           over ethernet using the libsane backend.
#
# author: richard.t.jones at uconn.edu
# version: march 21, 2020
# usage: $ scan.sh
#
# notes:
# (1) This script is a wrapper around the scanimage utility
#
# (2) The help message below was generated using the command
#     $ scanimage -L
#     device `pixma:MX920_192.168.1.131' is a CANON \
#     Canon PIXMA MX920 Series multi-function peripheral
#     $ scanimage -d pixma:MX920_192.168.1.131 --help
#
# Usage: scanimage [OPTION]...
# 
# Start image acquisition on a scanner device and write image data to
# standard output.
# 
# Parameters are separated by a blank from single-character options (e.g.
# -d epson) and by a "=" from multi-character options (e.g. --device-name=epson)
# -d, --device-name=DEVICE   use a given scanner device (e.g. hp:/dev/scanner)
#     --format=pnm|tiff      file format of output file
# -i, --icc-profile=PROFILE  include this ICC profile into TIFF file
# -L, --list-devices         show available scanner devices
# -f, --formatted-device-list=FORMAT similar to -L, but the FORMAT of the output
#                            can be specified: %d (device name), %v (vendor),
#                            %m (model), %t (type), %i (index number), and
#                            %n (newline)
# -b, --batch[=FORMAT]       working in batch mode, FORMAT is `out%d.pnm' or
#                            `out%d.tif' by default depending on --format
#     --batch-start=#        page number to start naming files with
#     --batch-count=#        how many pages to scan in batch mode
#     --batch-increment=#    increase page number in filename by #
#     --batch-double         increment page number by two, same as
#                            --batch-increment=2
#     --batch-prompt         ask for pressing a key before scanning a page
#     --accept-md5-only      only accept authorization requests using md5
# -p, --progress             print progress messages
# -n, --dont-scan            only set options, don't actually scan
# -T, --test                 test backend thoroughly
# -A, --all-options          list all available backend options
# -h, --help                 display this help message and exit
# -v, --verbose              give even more status messages
# -B, --buffer-size=#        change input buffer size (in kB, default 32)
# -V, --version              print version information
# 
# Options specific to device `pixma:MX920_192.168.1.131':
#   Scan mode:
#     --resolution auto||75|150|300|600|1200|2400dpi [75]
#         Sets the resolution of the scanned image.
#     --mode auto|Color|Gray|Lineart [Color]
#         Selects the scan mode (e.g., lineart, monochrome, or color).
#     --source Flatbed|Automatic Document Feeder|ADF Duplex [Flatbed]
#         Selects the scan source (such as a document-feeder). Set source before
#         mode and resolution. Resets mode and resolution to auto values.
#     --button-controlled[=(yes|no)] [no]
#         When enabled, scan process will not start immediately. To proceed,
#         press "SCAN" button (for MP150) or "COLOR" button (for other models).
#         To cancel, press "GRAY" button.
#   Gamma:
#     --custom-gamma[=(auto|yes|no)] [yes]
#         Determines whether a builtin or a custom gamma-table should be used.
#     --gamma-table auto|0..255,...
#         Gamma-correction table.  In color mode this option equally affects the
#         red, green, and blue channels simultaneously (i.e., it is an intensity
#         gamma table).
#     --gamma auto|0.299988..5 [2.2]
#         Changes intensity of midtones
#   Geometry:
#     -l auto|0..216.069mm [0]
#         Top-left x position of scan area.
#     -t auto|0..297.011mm [0]
#         Top-left y position of scan area.
#     -x auto|0..216.069mm [216.069]
#         Width of scan-area.
#     -y auto|0..297.011mm [297.011]
#         Height of scan-area.
#   Buttons:
#     --button-update
#         Update button state
#   Extras:
#     --threshold auto|0..100% (in steps of 1) [inactive]
#         Select minimum-brightness to get a white point
#     --threshold-curve auto|0..127 (in steps of 1) [inactive]
#         Dynamic threshold curve, from light to dark, normally 50-65
# 

import os
import sys
import subprocess
import tkinter as tk

email_list = ["rjones30@gmail.com",
              "carolbj30@gmail.com",
              "estherpjones@gmail.com",
             ]

def backticks(cmd):
   out = subprocess.Popen(" ".join([str(arg) for arg in cmd]), shell=True,
                          stdout=subprocess.PIPE).communicate()[0]
   return out.decode('utf-8')

# assign some default options
scan_options = {"scandev": "pixma:MX920_jonesscanner",
                "scan2sided": 0,
                "nice": 18}

# prepare the output directory for action
homedir = backticks(["echo $HOME"]).rstrip()
os.chdir(homedir + "/scans")
backticks(["echo rm -f out*.pnm"]).rstrip()

# set to the threshold level for white [0,4095]
white = 2000

# set to the maximum level for black [0,4095]
black = 100

# set the gamma factor for non-linear response
gamma = 1
gamma_table = backticks(["gamma4scanimage", gamma, black, white, 4095]).rstrip()

def scan_from_glass():
    def ok():
        return
    clear_prompt = display_prompt(["Scanning from glass..."], action=ok)
    sp = subprocess.Popen(
               ["nice", "-n" "{0}".format(scan_options['nice']),
                "scanimage", "-d", "{0}".format(scan_options['scandev']),
                "--format=pnm",
                "--batch=out%d.pnm",
                "--batch-start=1",
                "--batch-count=1",
                "--resolution",
                "{0}dpi".format(scan_options['scan resolution']),
                "--custom-gamma=yes",
                "--gamma-table", "{0}".format(gamma_table),
                "-x", "216", "-y", "280",
               ])
    if sp.wait() == 0:
        send_output(1)
    else:
        print("The scanner returned an error, it does that.",
              "Please eject page and reload on top of remaining",
              "stack, reboot the scanner, then try again.")
        backticks(["scanimage -T >/dev/null 2>&1"])
    clear_prompt()

def scan_from_feeder(side=0):
    def ok():
        return
    clear_prompt = display_prompt(["Scanning from feeder..."], action=ok)
    sp = subprocess.Popen(
           ["nice", "-n" "{0}".format(scan_options['nice']),
            "scanimage", "-d", "{0}".format(scan_options['scandev']),
            "--source", "Automatic Document Feeder",
            "--format=pnm",
            "--batch=out%d.pnm",
            "--batch-start={0}".format((side + 1) * 1000),
            "--batch-count=" + page_count_string.get(),
            "--resolution",
            "{0}".format(scan_options['scan resolution']),
            "--custom-gamma=yes",
            "--gamma-table", "{0}".format(gamma_table),
            "-x", "216", "-y", "280",
           ])
    if sp.wait() == 0:
        pages = int(page_count_string.get())
        if scan_options['scan2sided'] and side == 0:
            clear_prompt()
            def scan_other_side(s=1):
                scan_from_feeder(side=s)
            display_prompt(["Now turn over the stack, and we will scan",
                            "the back sides of those pages in reverse."],
                           action=scan_other_side)
            return # and wait for user to turn over the stack
        if scan_options['scan2sided']:
            for n in range(0, pages):
                os.rename("out{0}.pnm".format(n + 1000),
                          "out{0}.pnm".format(2 * n + 1))
            for n in range(0, pages):
                os.rename("out{0}.pnm".format(1999 + pages - n),
                          "out{0}.pnm".format(2 * n + 2))
            pages *= 2
        else:
            for n in range(0, pages):
                os.rename("out{0}.pnm".format(n + 1000),
                          "out{0}.pnm".format(n + 1))
        send_output(pages)
    else:
        print("The scanner returned an error, it does that.",
              "Please eject page and reload on top of remaining",
              "stack, reboot the scanner, then try again.")
        backticks(["scanimage -T >/dev/null 2>&1"])
    clear_prompt()

def send_output(pages):
    outlist = ["out{0}.pnm".format(n + 1) for n in range(0, pages)]
    print("converting output")
    outpdf = "scan-" + backticks(["date +%s"]).rstrip() + ".pdf"
    # The gm tool can run out of memory when merging large images, use img2pdf instead
    #backticks(["gm", "convert"] + outlist + [outpdf,]).rstrip()
    backticks(["img2pdf"] + outlist + ["-o", outpdf]).rstrip()
    if False:
        print("sending email")
        backticks(["scp", outpdf, "piggy@gluey.phys.uconn.edu:"])
        email_cmd = ["echo 'Your scanned document is attached. -rtj'", "|",
                     "mail -s 'new scan from jonesbase' ", "-A",
                     outpdf, sendto_email.get(), ";",
                     "exit $?"]
        sp = subprocess.Popen(["ssh", "piggy@gluey.phys.uconn.edu"], 
                              stdin=subprocess.PIPE) 
        resp = sp.communicate(input=" ".join(email_cmd).encode('ascii'))
        email_cmd = ["mail", "-s", "new scan from jonesbase", "-A",
                     outpdf, sendto_email.get()]
        sp = subprocess.Popen(email_cmd, stdin=subprocess.PIPE)
        resp = sp.communicate("Your scanned document is attached. -rtj".encode('ascii'))
        if sp.wait() == 0:
            print("Success: email sent to ", sendto_email.get())
        else:
            print("Failure: email send failed with status ",
                  "{0}".format(sp.returncode))

def display_prompt(message, action):
    dwin = tk.Tk()
    dwin.title("User Query")
    dwin.geometry("400x200")
    messages = []
    for line in message:
        label = tk.Label(dwin, text=line, font=("arial", 14))
        messages.append(label)
    messages[0].pack(pady=(50,5))
    for n in range(1, len(messages)):
        messages[n].pack(pady=(5,5))
    def callback():
        len(messages)
        dwin.destroy()
        action()
    button = tk.Button(dwin, text="OK", font=("arial", 12), command=callback)
    button.pack(pady=(5,50))
    dwin.update_idletasks()
    return callback

# the rest of this is just the gui

gwindow = tk.Tk()
gwindow.geometry("475x250")
gwindow.title("Canon Pixma MX922 scanning utility")
gwindow.resizable(0, 0)
extra_popups = {}
extra_buttons = {}

# define the buttons and controls
feeder_panel = tk.Frame(gwindow, width=240, height=200, bg="green",
                        relief=tk.RIDGE, borderwidth=2,
                        highlightbackground="black",
                        highlightcolor="black",
                        highlightthickness=1)
glass_panel = tk.Frame(gwindow, width=240, height=200, bg="orange",
                        relief=tk.RIDGE, borderwidth=2,
                        highlightbackground="black",
                        highlightcolor="black",
                        highlightthickness=1)
sendto_panel = tk.Frame(gwindow, width=480, height=50, bd=0,
                        relief=tk.RIDGE, borderwidth=2,
                        highlightbackground="black",
                        highlightcolor="black",
                        highlightthickness=2)
feeder_panel.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
glass_panel.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
sendto_panel.grid(row=1, column=0, columnspan=2,
                  sticky=tk.N+tk.S+tk.E+tk.W, ipady=2)

sendto_email = tk.StringVar()
sendto_email.set(email_list[0])
def change_email():
    popup = tk.Tk()
    popup.title("Select recipient email")
    buttons = []
    for email in email_list:
        def callback(select=email):
            sendto_email.set(select)
            popup.destroy()
        button = tk.Button(popup, text=email, font=("arial", 12),
                           command=callback)
        button.pack(fill=tk.X, side=tk.TOP, ipadx=20, ipady=10)
        buttons.append(button)

email_label = tk.Label(sendto_panel, text="send to", font=("arial", 14))
email_field = tk.Entry(sendto_panel, font=("arial", 14),
                       relief=tk.RIDGE, borderwidth=2,
                       textvariable=sendto_email,
                       width=27, bg="#eee", bd=0)
email_select = tk.Button(sendto_panel, text="Select", font=("arial", 14),
                         command=change_email)
email_label.grid(row=0, column=0, ipadx=5, ipady=5)
email_field.grid(row=0, column=1, ipadx=5, ipady=1)
email_select.grid(row=0, column=2, ipadx=1, ipady=2)

glass_button = tk.Button(glass_panel, text="Scan from glass",
                         bg="#ff5", height=2,
                         font=("arial", 14), command=scan_from_glass)
glass_button.grid(row=0, column=0, columnspan=3, pady=(5,5), padx=(32,32))

feeder_button = tk.Button(feeder_panel, text="Scan from feeder",
                          bg="#5f5", height=2,
                          font=("arial", 14), command=scan_from_feeder)
feeder_button.grid(row=0, column=0, columnspan=2, pady=(5,5), padx=(32,32))

def select_one_sided():
    scan_options['scan2sided'] = 0
    scan_options['set1sided button'].configure(background="white")
    scan_options['set2sided button'].configure(background="gray")

def select_two_sided():
    scan_options['scan2sided'] = 1
    scan_options['set1sided button'].configure(background="gray")
    scan_options['set2sided button'].configure(background="white")

set1sided_button = tk.Button(feeder_panel, text="1-sided",
                             bg="gray", height=2,
                             font=("arial", 14), command=select_one_sided)
set1sided_button.grid(row=1, column=0, padx=(5,5), pady=(10,10))
scan_options['set1sided button'] = set1sided_button

set2sided_button = tk.Button(feeder_panel, text="2-sided",
                             bg="gray", height=2,
                             font=("arial", 14), command=select_two_sided)

set2sided_button.grid(row=1, column=1, padx=(5,5), pady=(10,10))
scan_options['set2sided button'] = set2sided_button
select_one_sided()

sheets_label = tk.Label(feeder_panel, text="# of sheets",
                        font=("arial", 14), fg="white", bg="green")
sheets_label.grid(row=2, column = 0, pady=(10,10), padx=(5,5),
                  sticky=tk.W)
sheets_pane = tk.Frame(feeder_panel, width=40, height=30, bg="green")
sheets_pane.grid(row=2, column=1, pady=(5,5), padx=(1,1))

page_count_string = tk.StringVar()
page_count_string.set("1")

def increment_page_count():
    try:
        page_count = int(page_count_string.get())
        page_count_string.set(str(page_count + 1))
    except:
        page_count_string.set("1")

def decrement_page_count():
    try:
        page_count = int(page_count_string.get())
        if page_count > 1:
            page_count_string.set(str(page_count - 1))
        else:
            page_count_string.set(str(1))
    except:
        page_count_string.set("1")

page_count_field = tk.Entry(sheets_pane, font=("arial", 14),
                            relief=tk.RIDGE, borderwidth=2,
                            textvariable=page_count_string,
                            width=2, bg="#eee", bd=0)
page_count_field.grid(row=0, column=1, padx=(5,5), pady=(5,5),
                      ipadx=5, ipady=5)
page_count_incr = tk.Button(sheets_pane, text="+",
                            bg="#5f5", height=2,
                            font=("arial", 14), command=increment_page_count)
page_count_decr = tk.Button(sheets_pane, text="-",
                            bg="#5f5", height=2,
                            font=("arial", 14), command=decrement_page_count)
page_count_incr.grid(row=0, column=0, padx=(1,1), pady=(1,1))
page_count_decr.grid(row=0, column=2, padx=(1,1), pady=(1,1))

def set_resolution(dpi):
    def setres():
       for res in res_button:
           if res == dpi:
               res_button[res].configure(background="#ffc")
           else:
               res_button[res].configure(background="#cc2")
       scan_options['scan resolution'] = dpi
    return setres

res_button = {}
res_button[75] = tk.Button(glass_panel, text="75", bg="#cc2", height=2,
                           font=("arial", 14), command=set_resolution(75))
res_button[75].grid(row=1, column=0, padx=(5,5), pady=(5,5))
res_button[150] = tk.Button(glass_panel, text="150", bg="#cc2", height=2,
                          font=("arial", 14), command=set_resolution(150))
res_button[150].grid(row=1, column=1, padx=(5,5), pady=(5,5))
res_button[300] = tk.Button(glass_panel, text="300", bg="#cc2", height=2,
                          font=("arial", 14), command=set_resolution(300))
res_button[300].grid(row=1, column=2, padx=(5,5), pady=(5,5))
res_button[600] = tk.Button(glass_panel, text="600", bg="#cc2", height=2,
                          font=("arial", 14), command=set_resolution(600))
res_button[600].grid(row=2, column=0, padx=(5,5), pady=(5,5))
res_button[1200] = tk.Button(glass_panel, text="1200", bg="#cc2", height=2,
                          font=("arial", 14), command=set_resolution(1200))
res_button[1200].grid(row=2, column=1, padx=(5,5), pady=(5,5))
res_button[2400] = tk.Button(glass_panel, text="2400", bg="#cc2", height=2,
                          font=("arial", 14), command=set_resolution(2400))
res_button[2400].grid(row=2, column=2, padx=(5,5), pady=(5,5))
set_resolution(75)()

tk.mainloop()
