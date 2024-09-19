#!/bin/bash

# Directory where the JSON file is located
DIRECTORY="path_to_your_directory"

# GitHub repository details
REPO="https://github.com/yourusername/yourrepo.git"
BRANCH="main"

# Check if the JSON file exists
if [ -f "$DIRECTORY/all_transcriptions.json" ]; then
  cd $DIRECTORY
  

  # Add the remote repository
  git remote add origin $REPO
  
  # Check out the branch
  git checkout -b $BRANCH
  
  # Stage and commit the changes
  git add all_transcriptions.json
  git commit -m "Add transcription data"
  
  # Push to GitHub
  git push origin $BRANCH
else
  echo "JSON file not found!"
fi
