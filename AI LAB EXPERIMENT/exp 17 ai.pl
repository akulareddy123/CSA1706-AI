bird(parrot).
bird(eagle).
bird(penguin).

can_fly(X) :- bird(X), X \= penguin.
cannot_fly(penguin).
