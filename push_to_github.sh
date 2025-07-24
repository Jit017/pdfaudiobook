#!/bin/bash
# Commands to push your PDF to Audiobook Generator to GitHub
# Replace 'YOUR_GITHUB_USERNAME' with your actual GitHub username

echo "🚀 Pushing PDF to Audiobook Generator to GitHub..."

# Add GitHub remote (replace with your username)
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/pdf-to-audiobook-generator.git

# Push to main branch
git branch -M main
git push -u origin main

echo "✅ Successfully pushed to GitHub!"
echo "🌐 Your repository is now available at:"
echo "   https://github.com/YOUR_GITHUB_USERNAME/pdf-to-audiobook-generator"

# Alternative: If you prefer SSH (need SSH key setup)
# git remote add origin git@github.com:YOUR_GITHUB_USERNAME/pdf-to-audiobook-generator.git
# git push -u origin main 