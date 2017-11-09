
#!/bin/bash
echo "Change Log for the CoRR Project" > changelog.txt
echo "" >> changelog.txt
echo "" >> changelog.txt
echo "" >> changelog.txt

git config alias.lg "log --oneline -10 --abbrev=12 --graph --numstat --format=\"%cI %h %cn %s\""

git lg -- ./ >> changelog.txt