(define (problem zeno_2_2_1_27818)
  (:domain zenotravel)
  (:objects c0 c1 - city p0 p1 - person a0 - aircraft f0 f1 f2 f3 f4 - flevel)
  (:init (next f0 f1) (next f1 f2) (next f2 f3) (next f3 f4)
         (at-person p0 c0) (not-boarding p0) (not-debarking p0)
         (at-person p1 c1) (not-boarding p1) (not-debarking p1)
         (at-aircraft a0 c1) (fuel-level a0 f2) (not-refueling a0)
  )
  (:goal (and (at-person p0 c1) (at-person p1 c0)))
)
