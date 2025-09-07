@echo off
git pull origin main 2>nul || echo "No remote configured yet"
git add .
git commit -m "%*"
git push origin main 2>nul || git push --set-upstream origin main