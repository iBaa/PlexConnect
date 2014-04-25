#!/bin/bash

# Check for brew and install it
if [ ! -f "/usr/local/bin/brew" ]; then
  ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
  brew prune
fi

brew install git
