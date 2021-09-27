import re


pattern = re.compile(r'{.*?}')
text = "{dwaddddd{dddddddddddddddddddddddddddddddd64       \d                 \s  \t  \rdwad}"
print(re.findall(pattern, text))