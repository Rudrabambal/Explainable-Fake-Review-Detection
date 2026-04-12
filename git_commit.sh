#!/bin/bash
cd "/c/Users/rudra/OneDrive/Desktop/NLP project"
echo "=== Git Status ==="
git status
echo ""
echo "=== Adding all files ==="
git add -A
echo ""
echo "=== Committing ==="
git commit -m "Update project files: app.py and related changes"
echo ""
echo "=== Pushing to GitHub ==="
git push origin main
echo ""
echo "=== Done ==="
