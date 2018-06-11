(define (domain terrain)
(:requirements :typing :strips)
(:types loc - object land shallow-water deep-water - loc)
(:predicates
  (connected ?l1 ?l2 - loc)
  (at ?l - loc)
  (boulder-at ?l - loc)
  (drill-at ?l - loc)
  (alive)
  (has-drill)
)

(:action move-to-land
 :parameters (?l1 - loc ?l2 - land)
 :precondition (and 
  (alive) (at ?l1) (or (connected ?l1 ?l2) (connected ?l2 ?l1)) (not (boulder-at ?l2)))
 :effect (and (not (at ?l1)) (at ?l2))
)

(:action move-to-shallow-water
 :parameters (?l1 - loc ?l2 - shallow-water)
 :precondition (and 
  (alive) (at ?l1) (or (connected ?l1 ?l2) (connected ?l2 ?l1)) (not (boulder-at ?l2)))
 :effect (and (not (at ?l1)) (at ?l2))
)

(:action move-to-deep-water
 :parameters (?l1 - loc ?l2 - deep-water)
 :precondition (and 
  (alive) (at ?l1) (or (connected ?l1 ?l2) (connected ?l2 ?l1)) (not (boulder-at ?l2)))
 :effect (and (not (at ?l1)) (at ?l2))
)

)

