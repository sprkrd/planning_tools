
(define (problem p03)
  (:domain blocks-domain)
  (:objects b1 b2 b3 b4 b5 - block)
  (:init (emptyhand) (on-table b1) (on-table b2) (on b3 b5) (on b4 b1) (on-table b5) (clear b2) (clear b3) (clear b4))
  (:goal (and (emptyhand) (on b1 b3) (on b2 b4) (on-table b3) (on b4 b1) (on b5 b2) (clear b5)))
  (:goal-reward 40)
  (:metric maximize (reward))
)
