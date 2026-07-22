rooms = {'A':'Dirty','B':'Dirty'}

location = 'A'

while True:

    if rooms[location]=='Dirty':
        print("Cleaning",location)
        rooms[location]='Clean'

    if location=='A':
        location='B'
    else:
        break

print("Final State:",rooms)