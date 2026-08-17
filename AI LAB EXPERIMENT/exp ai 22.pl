edge(a,b,2).
edge(a,c,1).
edge(b,d,3).
edge(c,d,2).

best_first(X,Y) :-
    edge(X,Y,_).
