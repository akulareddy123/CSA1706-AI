board = [-1] * 8
row = 0
while row >= 0:
    board[row] += 1

    while board[row] < 8:
        safe = True

        for i in range(row):
            if board[i] == board[row] or abs(board[i] - board[row]) == abs(i - row):
                safe = False
                break

        if safe:
            break

        board[row] += 1

    if board[row] < 8:
        if row == 7:
            print("Solution:")
            for i in range(8):
                for j in range(8):
                    if board[i] == j:
                        print("Q", end=" ")
                    else:
                        print(".", end=" ")
                print()
            break
        else:
            row += 1
            board[row] = -1
    else:
        board[row] = -1
        row -= 1