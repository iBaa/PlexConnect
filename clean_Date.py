#!/usr/bin/python

import sys
import subprocess

data = sys.stdin.read()

while '$Date:' in data:
    start = data.find('$Date:')
    end = data.find('$', start+1)
    data = data[:start+5] + data[end:]

sys.stdout.write(data)