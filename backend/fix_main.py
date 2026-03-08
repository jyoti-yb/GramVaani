#!/usr/bin/env python3
import re

# Read the file
with open('main.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Remove conflict markers - keep the second version (after =======)
# Pattern: <<<<<<< ... ======= ... >>>>>>>
pattern = r'<<<<<<< Updated upstream\n(.*?)\n=======\n(.*?)\n>>>>>>> Stashed changes'

def replace_conflict(match):
    # Return the second version (after =======)
    return match.group(2)

content = re.sub(pattern, replace_conflict, content, flags=re.DOTALL)

# Write back
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed all merge conflicts!")

# Verify
with open('main.py', 'r', encoding='utf-8', errors='replace') as f:
    if '<<<<<<< ' in f.read():
        print("⚠ Warning: Some markers might remain")
    else:
        print("✓ All markers removed!")
