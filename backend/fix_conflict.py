#!/usr/bin/env python

with open('main.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Remove conflict markers (lines 736-743, which is indexes 735-742)
in_conflict = False
new_lines = []

for i, line in enumerate(lines):
    if i == 735 and '<<<<<<< Updated upstream' in line:
        in_conflict = True
        continue
    elif in_conflict and line.strip().startswith('======='):
        # Skip lines until we find the end of conflict
        continue
    elif in_conflict and '>>>>>>> eshwar' not in line:
        # Skip conflict lines, keep the second version (after =======)
        if line.strip() != '=======' and '<<<<<<< Updated upstream' not in line:
            # This is part of the cleaner solution (the =======  version)
            if i >= 741 and i <= 742:  # Lines 742-743 (indices 741-742)
                new_lines.append(line)
    elif '>>>>>>> eshwar' in line:
        in_conflict = False
        continue
    else:
        new_lines.append(line)

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed merge conflict!")
