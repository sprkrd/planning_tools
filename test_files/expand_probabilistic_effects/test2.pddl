(define (domain test)
(:requirements :probabilistic-effects)
(:predicates (p) (q) (r) (s))
(:action a
:parameters ()
:precondition ()
:effect (probabilistic 0.3 (p) 0.6 (and (q) (r)))))
