#!/usr/bin/python

"""
#! /usr/bin/env ruby
data = STDIN.read
last_date = `git log --pretty=format:"%ad" -1`
puts data.gsub('$Date$', '$Date: ' + last_date.to_s + '$')
"""

import sys
import subprocess

data = sys.stdin.read()

proc = subprocess.Popen('git log --pretty=format:"%ad" -1', shell=True, stdout=subprocess.PIPE)
return_code = proc.wait()
last_date = ''
for line in proc.stdout:
    #print("stdout: " + line.rstrip())
    last_date += line.rstrip()

sys.stdout.write(data.replace('$Date$', '$Date: ' + last_date + '$'))