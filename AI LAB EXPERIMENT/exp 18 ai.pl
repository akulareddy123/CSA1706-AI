parent(john,mary).
parent(john,david).
parent(mary,alice).
parent(david,robert).

father(X,Y) :- parent(X,Y).

grandparent(X,Y) :-
    parent(X,Z),
    parent(Z,Y).
