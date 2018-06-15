(define (domain sysadmin-slp)

 (:requirements :typing :equality :disjunctive-preconditions
                :probabilistic-effects :existential-preconditions
                :conditional-effects :negative-preconditions
                :universal-preconditions :rewards :equality)
 (:types comp)

 (:predicates (up-verified ?c - comp)
              (up-not-verified ?c - comp)
              (reboot-started ?c - comp)
              (reboot-pending ?x - comp)
              (conn ?c ?d - comp))

;; Note: MDPSim performs an action by going down its effect tree,
;; storing adds and dels (of terms) and updates (of values). The
;; "reboot" action has been modified to prevent the term (up ?x) from
;; being in both the adds and dels lists.
;; All tests are based on old terms and values (which is good). Terms
;; and values are updated only after the "action tree" has been
;; processed. As a result, no chain reaction can take place.
(:action start-reboot
  :parameters (?x - comp)
  :precondition (forall (?d - comp) (not (reboot-started ?d)))
  :effect (and
            (reboot-started ?x)
            (forall (?d - comp) (reboot-pending ?d))
            (forall (?d - comp) (when (up-verified ?d) (up-not-verified ?d)))
            (forall (?d - comp) (when (not (up-verified ?d)) (not (up-not-verified ?d))))
          )
)

(:action reboot-step-not-same-up
  :parameters (?x ?d - comp)
  :precondition (and
                  (reboot-started ?x)
                  (reboot-pending ?d)
                  (up-verified ?d)
                  (not (= ?x ?d))
                )
  :effect (and
            (not (reboot-pending ?d))
            (probabilistic
              0.2 (when
                    (exists (?c - comp) (and
                                          (conn ?c ?d)
                                          (not (up-verified ?c))))
                    (not (up-not-verified ?d))))
            (probabilistic 0.05 (not (up-not-verified ?d)))
          )
)

(:action reboot-step-not-same-down
  :parameters (?x ?d - comp)
  :precondition (and
                  (reboot-started ?x)
                  (reboot-pending ?d)
                  (not (up-verified ?d))
                  (not (= ?x ?d))
                )
  :effect (and
            (decrease (reward) 1)
            (not (reboot-pending ?d))
            (probabilistic
              0.2 (when
                    (exists (?c - comp) (and
                                          (conn ?c ?d)
                                          (not (up-verified ?c))))
                    (not (up-not-verified ?d)))
              )
            (probabilistic 0.05 (not (up-not-verified ?d)))
          )
)

(:action reboot-step-same-up
 :parameters (?x - comp)
 :precondition (and
                 (reboot-started ?x)
                 (reboot-pending ?d)
                 (up-verified ?x)
               )
 :effect (and
           (not (reboot-pending ?x))
           (probabilistic 0.9 (up-not-verified ?x)))
         )


(:action reboot-step-same-down
 :parameters (?x - comp)
 :precondition (and
                 (reboot-started ?x)
                 (reboot-pending ?x)
                 (not (up-verified ?x))
               )
 :effect (and
           (not (reboot-pending ?x))
           (decrease (reward) 1)
           (probabilistic 0.9 (up-not-verified ?x)))
)

(:action finish-reboot
  :parameters (?x - comp)
  :precondition (and
                  (reboot-started ?x)
                  (forall (?d - comp) (not (reboot-pending ?d)))
                )
  :effect (and
            (not (reboot-started ?x))
            (forall (?d - comp) (when (up-not-verified ?d) (up-verified ?d)))
            (forall (?d - comp) (when (not (up-not-verified ?d)) (not (up-verified ?d))))
          )
)

)
