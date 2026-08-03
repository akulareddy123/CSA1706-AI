tree = [3, 5, 2, 9]

def minimax(a, b, maxi):
    if a == b:
        return tree[a]

    m = (a + b) // 2

    if maxi:
        return max(minimax(a, m, False),
                   minimax(m + 1, b, False))
    else:
        return min(minimax(a, m, True),
                   minimax(m + 1, b, True))

print("Best Value =", minimax(0, 3, True))