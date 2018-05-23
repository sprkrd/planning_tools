(define (domain test)
(:requirements :probabilistic-effects :rewards)
(:predicates (p) (q) (r) (s))
(:action a
:parameters ()
:precondition (and (and) (and) (imply (and) (and)))
:effect (when (s) (probabilistic 0.5 (and (p) (increase (reward) 25)) 0.5 (probabilistic 0.3 (q) 0.2 (and (r) (decrease (reward) 50))))))))
