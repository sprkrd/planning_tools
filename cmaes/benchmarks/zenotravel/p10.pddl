(define (problem p10)
  (:domain zenotravel)
  (:objects c0 c1 c2 c3 c4 c5 c6 c7 c8 c9 - city p0 p1 p2 p3 p4 - person a0 a1 a2 - aircraft f0 f1 f2 f3 f4 - flevel)
  (:init (next f0 f1) (next f1 f2) (next f2 f3) (next f3 f4)
         (at-person p0 c5) (not-boarding p0) (not-debarking p0)
         (at-person p1 c8) (not-boarding p1) (not-debarking p1)
         (at-person p2 c9) (not-boarding p2) (not-debarking p2)
         (at-person p3 c2) (not-boarding p3) (not-debarking p3)
         (at-person p4 c2) (not-boarding p4) (not-debarking p4)
         (at-aircraft a0 c2) (fuel-level a0 f4) (not-refueling a0)
         (at-aircraft a1 c8) (fuel-level a1 f1) (not-refueling a1)
         (at-aircraft a2 c7) (fuel-level a2 f4) (not-refueling a2)
  )
  (:goal (and (at-person p0 c5) (at-person p1 c9) (at-person p2 c0) (at-person p3 c5) (at-person p4 c4)))
  (:goal-reward 10000)
  (:metric maximize (reward))
)
