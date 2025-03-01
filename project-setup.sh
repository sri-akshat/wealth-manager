#!/bin/bash
# This script configures the Git hooks directory to ensure that custom hooks are used.
# Make sure you have a 'hooks' directory at the root of your repository with your hook files.

# Check if we're inside a Git repository
if [ ! -d .git ]; then
  echo "This script must be run from the root of a Git repository."
  exit 1
fi

# Set the hooks path to the 'hooks' directory
git config core.hooksPath git-hooks

if [ $? -eq 0 ]; then
  echo "Git hooks path successfully set to 'git-hooks'."
else
  echo "There was an error setting the Git hooks path."
  exit 1
fi