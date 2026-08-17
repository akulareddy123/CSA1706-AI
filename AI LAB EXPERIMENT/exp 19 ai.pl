diet(diabetes,'Sugar Free Food').
diet(bp,'Low Salt Food').
diet(obesity,'Low Fat Food').
diet(fever,'Liquid Food').

suggest(D,Diet) :-
    diet(D,Diet).
