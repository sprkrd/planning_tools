(define (domain test)
(:requirements :probabilistic-effects)
(:predicates (p) (q) (r) (s))
(:action a
:parameters ()
:precondition (and (and) (and) (imply (and) (and)))
:effect (when (s) (probabilistic 0.5 (p) 0.5 (probabilistic 0.3 (q) 0.2 (r))))))
