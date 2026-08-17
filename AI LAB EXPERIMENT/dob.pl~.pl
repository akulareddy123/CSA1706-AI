person(rahul, '10-05-2003').
person(priya, '15-08-2004').
person(arun, '20-12-2002').
person(kiran, '05-03-2005').

dob(Name, DOB) :-
    person(Name, DOB).
