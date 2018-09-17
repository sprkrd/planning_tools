(define (problem sysadmin-12-6-5)
  (:domain sysadmin-slp)
  (:objects comp0 comp1 comp2 comp3 comp4 comp5 comp6 comp7 comp8 comp9 comp10 comp11 - comp)
  (:init
	 (conn comp0 comp1)
	 (conn comp1 comp2)
	 (conn comp2 comp3)
	 (conn comp3 comp4)
	 (conn comp4 comp5)
	 (conn comp5 comp6)
	 (conn comp6 comp4)
	 (conn comp6 comp7)
	 (conn comp6 comp10)
	 (conn comp7 comp2)
	 (conn comp7 comp8)
	 (conn comp8 comp0)
	 (conn comp8 comp7)
	 (conn comp8 comp9)
	 (conn comp9 comp0)
	 (conn comp9 comp10)
	 (conn comp10 comp11)
	 (conn comp11 comp0)
  )
  (:goal (forall (?c - comp)
                 (up-verified ?c)))
  (:goal-reward 500)
 (:metric maximize (reward))
)
