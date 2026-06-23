@echo off
"C:\Program Files\Git\cmd\git.exe" status
"C:\Program Files\Git\cmd\git.exe" add README.md
"C:\Program Files\Git\cmd\git.exe" commit -m "Update README.md with NLP and ML details"
"C:\Program Files\Git\cmd\git.exe" push origin main
