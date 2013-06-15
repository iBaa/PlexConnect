#!/usr/bin/python

# export-subst
"""
Option  Description of Output
%H  Commit hash
%h  Abbreviated commit hash
%T  Tree hash
%t  Abbreviated tree hash
%P  Parent hashes
%p  Abbreviated parent hashes
%an Author name
%ae Author e-mail
%ad Author date (format respects the --date= option)
%ar Author date, relative
%cn Committer name
%ce Committer email
%cd Committer date
%cr Committer date, relative
%s  Subject
"""

last_commit = '$Format:%cd$'
commit_hash = '$Format:%H$'
tree_hash = '$Format:%T$'
parent_hashes = '$Format:%P$'

# filter
date ='$Date: Sat Jun 15 21:23:33 2013 +0200$'
