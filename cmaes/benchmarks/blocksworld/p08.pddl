
(define (problem p08)
  (:domain blocks-domain)
  (:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 - block)
  (:init (emptyhand) (on b1 b5) (on b2 b9) (on-table b3) (on b4 b6) (on b5 b2) (on-table b6) (on b7 b8) (on b8 b1) (on b9 b3) (on-table b10) (clear b4) (clear b7) (clear b10))
  (:goal (and (emptyhand) (on b1 b10) (on b2 b6) (on b3 b8) (on b4 b2) (on-table b5) (on-table b6) (on b7 b5) (on-table b8) (on b9 b3) (on b10 b4) (clear b1) (clear b7) (clear b9)))
  (:metric maximize (reward))
)
