#!/usr/bin/python

"""
#! /usr/bin/env ruby
data = STDIN.read
last_date = `git log --pretty=format:"%ad" -1`
puts data.gsub('$Date$', '$Date: ' + last_date.to_s + '$')
"""

import sys
from subprocess import call

data = sys.stdin.read()
last_date = call('git log --pretty=format:"%ad" -1', shell=True)

sys.stdout.write(data.replace('$Date$', '$Date: ' + last_date.to_s + '$'))