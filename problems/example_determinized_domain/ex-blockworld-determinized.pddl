(define (domain exploding-blocksworld)

(:requirements :typing :conditional-effects :equality)

(:types block)

(:predicates
  (on ?b1 ?b2 - block)
  (on-table ?b - block)
  (clear ?b - block)
  (holding ?b - block)
  (emptyhand)
  (no-detonated ?b - block)
  (no-destroyed ?b - block)
  (no-destroyed-table)
)

(:functions (total-cost))

(:action pick-up_o0
  :parameters (?b1 ?b2 - block)
  :precondition (and (emptyhand) (clear ?b1) (on ?b1 ?b2) (no-destroyed ?b1))
  :effect (and (holding ?b1) (clear ?b2) (not (emptyhand)) (not (on ?b1 ?b2)))
)

(:action pick-up-from-table_o0
  :parameters (?b - block)
  :precondition (and (emptyhand) (clear ?b) (on-table ?b) (no-destroyed ?b))
  :effect (and (holding ?b) (not (emptyhand)) (not (on-table ?b)))
)

(:action put-down_o0
  :parameters (?b - block)
  :precondition (and (holding ?b) (no-destroyed-table))
  :effect (and (emptyhand) (on-table ?b) (not (holding ?b)) (when (no-detonated ?b) (and (not (no-destroyed-table)) (not (no-detonated ?b)))) (increase (total-cost) 92))
)

(:action put-down_o1
  :parameters (?b - block)
  :precondition (and (holding ?b) (no-destroyed-table))
  :effect (and (emptyhand) (on-table ?b) (not (holding ?b)) (increase (total-cost) 51))
)

(:action put-on-block_o0
  :parameters (?b1 ?b2 - block)
  :precondition (and (holding ?b1) (clear ?b2) (no-destroyed ?b2) (not (= ?b1 ?b2)))
  :effect (and (emptyhand) (on ?b1 ?b2) (not (holding ?b1)) (not (clear ?b2)) (when (no-detonated ?b1) (and (not (no-destroyed ?b2)) (not (no-detonated ?b1)))) (increase (total-cost) 230))
)

(:action put-on-block_o1
  :parameters (?b1 ?b2 - block)
  :precondition (and (holding ?b1) (clear ?b2) (no-destroyed ?b2) (not (= ?b1 ?b2)))
  :effect (and (emptyhand) (on ?b1 ?b2) (not (holding ?b1)) (not (clear ?b2)) (increase (total-cost) 11))
))
