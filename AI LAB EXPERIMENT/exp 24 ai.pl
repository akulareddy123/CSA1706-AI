fact(rain).
fact(cloud).

rule(wet) :-
    fact(rain).

rule(carry_umbrella) :-
    rule(wet).
