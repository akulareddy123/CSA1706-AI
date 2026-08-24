hanoi(1,X,Y,_) :-
    write('Move '),write(X),write(' -> '),write(Y),nl.

hanoi(N,X,Y,Z) :-
    N > 1,
    M is N-1,
    hanoi(M,X,Z,Y),
    hanoi(1,X,Y,Z),
    hanoi(M,Z,Y,X).
