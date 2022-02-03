# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 09:27:33 2021

@author: Paul Leroy
"""

import os, subprocess

import tools.ccConfig as ccConfig

miniconda3 = ccConfig.miniconda3
_python = ccConfig._python

def to_bool(str_):
    if 'false' in str_:
        str_ = str_.replace('false', 'False')
    elif 'true' in str_:
        str_ = str_.replace('true', 'True')
    return eval(str_)
    
def to_str(bool_):
    if bool_ is True:
        ret = 'true'
    else:
        ret ='false'
    return ret

def exe(cmd, debug=False):
    if debug is True:
        print('Execute the following command:')
        print(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True) 
    while process.poll() is None:
        for output in process.stdout.readlines():
            if debug is True:
                print(output.strip())
            else:
                pass
    # Process has finished, read rest of the output 
    for output in process.stdout.readlines():
        if debug is True:
            print(output.strip())
        else:
            pass
    process.wait()
    return process.returncode

def pyuic5(ui, debug=False):
    head, tail = os.path.split(ui)
    root, ext = os.path.splitext(tail)
    out = os.path.join(head, 'Ui_' + root + '.py')
    cmd = [_python, '-m', 'PyQt5.uic.pyuic', ui, '-o', out]
    print(cmd)
    exe(cmd, debug=debug)


if __name__ == '__main__':
    in_ = 'C:/Users/PaulLeroy/Documents/DEV/icpm3c2'
    ui_main = os.path.join(in_, 'MainWindow.ui')
    ui_icp = os.path.join(in_, 'ICPParameters.ui')
    ui_m3c2 = os.path.join(in_, 'M3C2Parameters.ui')
