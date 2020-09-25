'''
This script makes a fixture for the TRIBE model from the iwi.txt file.

We'll need to include all other tribes (throught out world) in this file
Does that make sense? Not sure...

'''

import io

f = io.open('iwi.txt', mode="r", encoding="utf-8")
lines = f.readlines()
f.close()


f = io.open('iwi.yaml', mode="w", encoding="utf-8")
count = 0
for line in lines:
    if '#' in line[0]:
        continue
    count = count+1
    string = u'''
- model: people.tribe
  pk: {0}
  fields:
    name: {1}\n'''.format(count, line.strip())
    f.write(string)

f.close()
