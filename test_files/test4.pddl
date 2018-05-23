(define (domain test)
(:requirements :probabilistic-effects)
(:predicates (p) (q) (r) (s))
(:action a
:parameters ()
:precondition ()
:effect (and (probabilistic 0.3 (p) 0.7 (r)) (probabilistic 0.5 (q) 0.5 (s)))))
