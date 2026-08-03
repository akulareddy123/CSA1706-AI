board=[' ']*9

def show():
    for i in range(0,9,3):
        print(board[i:i+3])

for i in range(9):
    show()
    p=int(input("Position: "))
    board[p]='X' if i%2==0 else 'O'

show()