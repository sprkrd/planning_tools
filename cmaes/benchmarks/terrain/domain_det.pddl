(define (domain terrain)
(:requirements :typing :strips)
(:types loc - object land shallow-water deep-water - loc)
(:predicates
  (connected ?l1 ?l2 - loc)
  (at ?l - loc)
  (boulder-at ?l - loc)
  (pickaxe-at ?l - loc)
  (flag-at ?l - loc)
  (alive)
  (has-pickaxe)
  (goal-reached)
)

(:functions (reward))

(:action move-to-land
 :parameters (?l1 - loc ?l2 - land)
 :precondition (and 
  (alive)
  (at ?l1)
  (or (connected ?l1 ?l2)
  (connected ?l2 ?l1))
  (not (boulder-at ?l2)))
 :effect (and
  (not (at ?l1))
  (at ?l2)
  (decrease (reward) 1))
)

(:action move-to-shallow-water
 :parameters (?l1 - loc ?l2 - shallow-water)
 :precondition (and 
  (alive)
  (at ?l1)
  (or (connected ?l1 ?l2) (connected ?l2 ?l1))
  (not (boulder-at ?l2)))
 :effect (and
  (not (at ?l1))
  (at ?l2)
  (decrease (reward) 1)
))

(:action move-to-deep-water
 :parameters (?l1 - loc ?l2 - deep-water)
 :precondition (and 
  (alive)
  (at ?l1)
  (or (connected ?l1 ?l2) (connected ?l2 ?l1))
  (not (boulder-at ?l2)))
 :effect (and
  (not (at ?l1))
  (at ?l2)
  (decrease (reward) 1))
)

(:action pick-pickaxe
 :parameters (?l - loc)
 :precondition (and
  (alive)
  (not (has-pickaxe))
  (at ?l)
  (pickaxe-at ?l))
 :effect (and
  (has-pickaxe)
  (not (pickaxe-at ?l)))
)

(:action break-boulder
 :parameters (?l1 ?l2 - loc)
 :precondition (and
  (alive)
  (has-pickaxe)
  (at ?l1)
  (or (connected ?l1 ?l2) (connected ?l2 ?l1))
  (boulder-at ?l2))
 :effect (and
  (not (boulder-at ?l2))
  (decrease (reward) 2))
)

(:action reach-goal
 :parameters (?l - loc)
 :precondition (and
  (not (goal-reached))
  (alive)
  (at ?l)
  (flag-at ?l)
 )
 :effect (goal-reached)
)

)

