import re
def modify(filepath, from_, to_):
    file = open(filepath,"r+")
    text = file.read()
    pattern = from_
    splitted_text = re.split(pattern,text)
    modified_text = to_.join(splitted_text)
    with open(filepath, 'w') as file:
        file.write(modified_text)

file = open("changedCharactersList.txt","r+")
text = file.read()
print("Before modification:",text)
modify("changedCharactersList.txt","Defense","\nDefense")
file = open("changedCharactersList.txt","r+")
text = file.read()
print("After modification:",text)
file.close()
