# VHS script for docs/attack-demo.gif.
# Regenerate with: vhs docs/attack-demo.tape
# Requires: both app containers running locally on 5100 (vulnerable-app)
# and 5101 (secure-app) — see docs/attack-demo.md for the exact commands.

Output docs/attack-demo.gif

Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 650
Set Padding 20
Set Theme "Dracula"
Set TypingSpeed 40ms

Type "# same SQLi payload, run against both apps"
Enter
Sleep 700ms

Type "python3 security/exploits/sqli_exploit.py --compare --insecure-url http://localhost:5100 --secure-url http://localhost:5101"
Sleep 500ms
Enter

Sleep 8s
