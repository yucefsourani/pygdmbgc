#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pygdmbgc.py
#  
#  Copyright 2019 youcef sourani <youssef.m.sourani@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import subprocess
import os
import sys
import tempfile

css_file_name          = "gnome-shell.css"
xml_file_name          = "gnome-shell-theme.gresource.xml"
compiled_xml_file_name = "gnome-shell-theme.gresource"

start_xml_file = """<?xml version="1.0" encoding="UTF-8"?>
<gresources>
  <gresource prefix="/org/gnome/shell/theme">\n"""
  
file_location_xml_file = "<file>{}</file>\n"

end_xml_file = """  </gresource>
</gresources>"""


gst="/usr/share/gnome-shell/gnome-shell-theme.gresource"


options = {"background-repeat": "no-repeat", 
  "background-size": "cover" }


_help= """
NAME
    pygdmbgc - Gdm Background Changer
    
SYNOPSIS
    pygdmbgc.py [--help -h]                           HELP
    pygdmbgc.py [--reset -r]                          RESET
    pygdmbgc.py ~/Picture/mypic.png                   CHANGE BACKGROUND WITH DEFAILT OPTIONS 
    pygdmbgc.py ~/Picture/mypic.png [KEY=VALUE ...]   CHANGE BACKGROUND WTTH OPTIONS

OPTIONS
    background-repeat=repeat
    background-repeat=no-repeat
    background-size=cover
    background-size=contain
    "background-size=1920px 1080px"   #[WIDTH]px [HEIGHT]px your screen's resolution
    background-position=center
    "background-position=0 0"         #x y
    "color=#000000"                   #Color For Default background "noise-texture.png"
    
EXAMPLES
    pygdmbgc.py ~/Picture/mypic.png background-repeat=no-repeat background-size=cover
    pygdmbgc.py noise-texture.png "color=#FF3B3B"
    
BUGS
    https://github.com/yucefsourani/pygdmbgc"""

def make_xml_file(location):
    to_write = start_xml_file
    os.chdir(os.path.join(location,"org/gnome/shell/theme"))
    for dirname,folder,files in os.walk(".") :
        for file_ in files:
            to_write = to_write+file_location_xml_file.format(os.path.join(dirname,file_)[2:])
    to_write = to_write+end_xml_file
    try:
        with open(xml_file_name,"w") as myfile:
            myfile.write(to_write)
    except Exception as e:
        print(e)
        return False
    return os.path.join(location,"org/gnome/shell/theme",xml_file_name)

def compile_xml_file(location):
    if subprocess.call("glib-compile-resources {}".format(location),shell=True)!=0:
        return False
    return os.path.join(os.path.dirname(location),compiled_xml_file_name)

def move_xml_file(source,target,pkexec=True):
    if pkexec:
        check = subprocess.call("pkexec cp {} {}".format(source,target),shell=True)
    else:
        check = subprocess.call("pkexec cp {} {}".format(source,target),shell=True)
    return True if check==0 else False

def lock_dialog_css_gene(**options):
    css = "\n#lockDialogGroup {\n"
    count = 0
    options_count = len(options.keys())
    for k,v in options.items():
        count=count+1
        if count==options_count:
            css = css+"  "+k+" : "+v+"; }\n"
            continue
        css = css+"  "+k+" : "+v+"; \n"
    return css
    


def css_edit(location,**options):
    os.chdir(os.path.join(location,"org/gnome/shell/theme"))
    to_write = ""
    b = False
    try:
        with open(css_file_name) as myfile:
            for line in myfile:
                l = line.strip()
                if l.startswith("#lockDialogGroup"):
                    b = True
                elif l.endswith("}") and b:
                    b = False
                    to_write = to_write+lock_dialog_css_gene(**options)
                    continue
                if not b:
                    to_write = to_write+line
        with open(css_file_name,"w") as myfile:
            myfile.write(to_write)
    except Exception as e:
        print(e)
        return False

    return True


def main(workdir,background_pic_location="noise-texture.png",**options):
    if background_pic_location!="noise-texture.png":
        if not os.path.isfile(background_pic_location):
            print("Backgound Picture Not Found.")
            return False
    if "color" in options.keys():
        background_color = options["color"]
    else:
        background_color = "#41494c"
    os.makedirs(workdir,exist_ok=True)
    l = subprocess.check_output("gresource list {}".format(gst),shell=True).decode("utf-8").split("\n")
    for i in l:
        if i:
            ll = os.path.join(workdir,os.path.dirname(i)[1:])
            os.makedirs(ll,exist_ok=True)
            subprocess.call("gresource extract {} {} >{}".format(gst,i,os.path.join(ll,os.path.basename(i))),shell=True)
            
    if  background_pic_location!="noise-texture.png":
        background_pic_location_strip = background_pic_location.replace(" ","")
        background_pic = os.path.basename(background_pic_location_strip)
        if subprocess.call("cp \"{}\" \"{}\"".format(background_pic_location,os.path.join(workdir,"org/gnome/shell/theme",background_pic)),shell=True)!=0:
            print("Copy Backgound Picture Faild.")
            return False
    else:
        background_pic = background_pic_location
    options.setdefault("background"," {} url(resource:///org/gnome/shell/theme/{})".format(background_color,background_pic))
    css_edit(workdir,**options)
    xml_file = make_xml_file(workdir)
    if xml_file:
        compiled_file = compile_xml_file(xml_file)
        if compiled_file :
            if move_xml_file(compiled_file,gst):
                return True
            else:
                print("Move Compiled xml File Faild.")
                return False
            
        else:
            print("Compile xml File Faild.")
            return False
    else:
        print("Make xml File Faild.")
        return False
        
def backup():
    if not os.path.isfile("/usr/share/gnome-shell/gnome-shell-theme.gresource.backup"):
        print("Backup /usr/share/gnome-shell/gnome-shell-theme.gresource.")
        if subprocess.call("pkexec cp /usr/share/gnome-shell/gnome-shell-theme.gresource /usr/share/gnome-shell/gnome-shell-theme.gresource.backup",shell=True)!=0:
            print("Backup /usr/share/gnome-shell/gnome-shell-theme.gresource Faild.")
            exit(1)

def reset():
    if not os.path.isfile("/usr/share/gnome-shell/gnome-shell-theme.gresource.backup"):
            print("Backup File /usr/share/gnome-shell/gnome-shell-theme.gresource.backup not Found.")
            exit(1)
    else:
        if subprocess.call("pkexec cp /usr/share/gnome-shell/gnome-shell-theme.gresource.backup /usr/share/gnome-shell/gnome-shell-theme.gresource",shell=True)!=0:
            print("Reset Faild.")
            exit(1)
    print("Reset Done.")
    exit(0)
    
if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print(_help)
        exit(0)
    if "--reset" in sys.argv or "-r" in sys.argv:
        reset()
    if len(sys.argv)<2:
        print("Nothing To Do please Enter Background Picture Location.")
    elif len(sys.argv)<3:
        backup()
        print("Change gdm Backgound Picture with default Options : ")
        for k,v in options.items():
            print("{} : {} ;".format(k,v))
        with tempfile.TemporaryDirectory() as tmpdirname:
            if not main(tmpdirname,background_pic_location=os.path.expanduser(os.path.expandvars(sys.argv[1])),**options):
                print("Change gdm backgroud picture Faild.")
            else:
                print("Done Please Logout/Login")
            
    else :
        newoptions = dict()
        print("Change gdm Backgound Picture with This Options : ")
        try:
            for op in sys.argv[2:]:
                k,v = op.split("=",1)
                print("{} : {} ;".format(k,v))
                newoptions.setdefault(k,v)
        except :
            pass
        backup()
        if len(newoptions.items())==0 :
            print("Failback To Default Options : ")
            for k,v in options.items():
                print("{} : {} ;".format(k,v))
            with tempfile.TemporaryDirectory() as tmpdirname:
                if not main(tmpdirname,background_pic_location=os.path.expanduser(os.path.expandvars(sys.argv[1])),**options):
                    print("Change gdm backgroud picture Faild.")
                else:
                    print("Done Please Logout/Login")
                    
        elif len(newoptions.items())==1 and "color" in newoptions.keys() :
            backup()
            print("New Color with Default Options : ")
            options.setdefault("color",newoptions["color"])
            for k,v in options.items():
                print("{} : {} ;".format(k,v))
            with tempfile.TemporaryDirectory() as tmpdirname:
                if not main(tmpdirname,background_pic_location=os.path.expanduser(os.path.expandvars(sys.argv[1])),**options):
                    print("Change gdm backgroud picture Faild.")
                else:
                    print("Done Please Logout/Login")

        else:
            backup()
            with tempfile.TemporaryDirectory() as tmpdirname:
                if not main(tmpdirname,background_pic_location=os.path.expanduser(os.path.expandvars(sys.argv[1])),**newoptions):
                    print("Change gdm backgroud picture Faild.")
                else:
                    print("Done Please Logout/Login")
                
                
        

