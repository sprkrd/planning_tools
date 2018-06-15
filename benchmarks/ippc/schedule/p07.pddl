(define (problem a-schedule-problem966)
(:domain schedule)
(:objects P0 P1 P2 P3 P4 P5 P6 P7 P8 P9 P10 P11  - packet)
(:init 
       (alive)
       (current-phase Arrivals-and-updating)
       (need-to-process-arrivals C0)
       (need-to-process-arrivals C1)
       (need-to-process-arrivals C2)
       (status P0 Available)
       (status P1 Available)
       (status P2 Available)
       (status P3 Available)
       (status P4 Available)
       (status P5 Available)
       (status P6 Available)
       (status P7 Available)
       (status P8 Available)
       (status P9 Available)
       (status P10 Available)
       (status P11 Available)
       (not-dropped P0)
       (not-dropped P1)
       (not-dropped P2)
       (not-dropped P3)
       (not-dropped P4)
       (not-dropped P5)
       (not-dropped P6)
       (not-dropped P7)
       (not-dropped P8)
       (not-dropped P9)
       (not-dropped P10)
       (not-dropped P11)
)
(:goal (and (alive) (forall (?c - class) (served ?c))))
(:goal-reward 1)
(:metric maximize (reward))
)
