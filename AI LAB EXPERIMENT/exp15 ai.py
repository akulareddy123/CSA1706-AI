def alphabeta(depth, alpha, beta, isMax):
    if depth == 0:
        return 10

    if isMax:
        alpha = max(alpha, alphabeta(depth-1, alpha, beta, False))
        if alpha >= beta:
            return alpha
        return alpha
    else:
        beta = min(beta, alphabeta(depth-1, alpha, beta, True))
        if alpha >= beta:
            return beta
        return beta

print(alphabeta(3, -999, 999, True))