(define (domain imagine)
(:requirements :adl :rewards :probabilistic-effects)
(:types component side mode tool affordance affordance-confidence - object
        removable-component - component
        lever-point suction-point pliers-point - affordance
        screwdriver - tool
        screw - removable-component
)

(:constants
  top bottom front back left right - side
  low medium high - affordance-confidence
  scara power no-mode - mode
  flat-sd star-sd - screwdriver
  hammer suction-tool pliers cutter no-tool - tool
)

(:predicates
             (has-affordance ?c - removable-component ?a - affordance)
             (has-confidence ?a - affordance ?c - affordance-confidence)
             (broken-component ?c - removable-component)
             (broken-tool ?t - tool)
             (connected ?c1 ?c2 - component)
             (clear ?c - removable-component)
             (current-mode ?m - mode)
             (current-side ?s - side)
             (current-tool ?t - tool)
             (held)
             (hides-component ?c1 ?c2 - component)
             (hides-affordance ?c1 - component ?a - affordance)
             (fixed-by ?c - removable-component ?s - screw)
             (loose ?c - removable-component)
             (partially-occludes ?c1 ?c2 - component)
             (removed-non-verified ?c - removable-component)
             (removed-verified ?c - removable-component)
             (stuck ?s - screw)
             ; static predicates
             (opposite-side ?s1 ?s2 - side)
             (at-side ?c - component ?s - side)
             (valid-mode ?t - tool ?m - mode)
             (valid-sd ?s - screw ?sd - screwdriver)
)

;#########################
;# DETERMINISTIC ACTIONS #
;#########################

(:action check-removed
 :parameters (?comp - removable-component ?side - side)
 :precondition (and
                 (current-side ?side)
                 (at-side ?comp ?side)
                 (removed-non-verified ?comp)
               )
 :effect (and
           (forall (?other - component)
                   (and
                     (not (hides-component ?comp ?other))
                     (not (partially-occludes ?comp ?other))
                   ))
           (forall (?aff - affordance) (not (hides-affordance ?comp ?aff)))
           (not (at-side ?comp ?side))
           (not (removed-non-verified ?comp))
           (removed-verified ?comp)
         )
)

(:action assert-clear
 :parameters (?comp - removable-component)
 :precondition (and
                 (not (clear ?comp))
                 (forall (?screw - screw) (not (fixed-by ?comp ?screw)))
                 (forall (?other - component)
                         (and (not (connected ?comp ?other)) (not (connected ?other ?comp))))
               )
 :effect (clear ?comp)
)

(:action pick-tool
  :parameters (?tool - tool ?mode - mode)
  :precondition (and
                  (not (= ?tool no-tool))
                  (not (= ?mode no-mode))
                  (imply (held) (not (= ?mode power)))
                  (current-tool no-tool)
                  (current-mode no-mode)
                  (valid-mode ?tool ?mode)
                )
  :effect (and
            (not (current-tool no-tool))
            (not (current-mode no-mode))
            (current-tool ?tool)
            (current-mode ?mode)
            (decrease (reward) 1)
          )
)

(:action put-away-tool
 :parameters (?tool - tool ?mode - mode)
 :precondition (and
                 (not (= ?tool no-tool))
                 (not (= ?mode no-mode))
                 (current-tool ?tool)
                 (current-mode ?mode)
               )
 :effect (and
           (not (current-tool ?tool))
           (not (current-mode ?mode))
           (current-tool no-tool)
           (current-mode no-mode)
           (decrease (reward) 1)
         )
)

(:action grab-device
  :parameters ()
  :precondition (and
                  (not (held)) 
                  (not (current-mode power))
                )
  :effect (and (held) (decrease (reward) 1))
)

(:action place-device
  :parameters ()
  :precondition (held)
  :effect (and (not (held)) (decrease (reward) 1))
)

(:action flip
:parameters (?old-side - side ?new-side - side)
:precondition (and (current-side ?old-side) (held))
:effect (and
          (not (current-side ?old-side))
          (current-side ?new-side)
          (decrease (reward) 1)
        )
)

(:action let-fall-down
 :parameters (?comp - removable-component ?side ?side-opposite - side)
 :precondition (and
                 (held)
                 (at-side ?comp ?side)
                 (opposite-side ?side ?side-opposite)
                 (current-side ?side-opposite)
                 (loose ?comp)
                 (clear ?comp)
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (forall (?comp_ - component) (not (partially-occludes ?comp_ ?comp)))
               )
 :effect (and
           (removed-non-verified ?comp)
           (decrease (reward) 1)
         )
)

(:action cut-connector
 :parameters (?c1 ?c2 - component ?side - side)
 :precondition (and
                 (current-tool cutter)
                 (imply (not (held)) (current-mode power))
                 (connected ?c1 ?c2)
                 (current-side ?side)
                 (or (at-side ?c1 ?side) (at-side ?c2 ?side))
               )
 :effect (and
           (not (connected ?c1 ?c2))
           (not (connected ?c2 ?c1))
           (decrease (reward) 1)
         )
)

;#######################
;# UNSCREW (4 ACTIONS) #
;#######################

(:action unscrew-scara-non-stuck
 :parameters (?screw - screw ?sd - screwdriver ?side - side)
 :precondition (and
                 (not (broken-component ?screw))
                 (not (broken-tool ?sd))
                 (not (stuck ?screw))
                 (current-mode scara)
                 (current-side ?side)
                 (at-side ?screw ?side)
                 (current-tool ?sd)
                 (valid-sd ?screw ?sd)
                 (forall (?comp - component) (not (hides-component ?comp ?screw)))
               )
 :effect (and
           (probabilistic
             0.60 (and
                    (forall (?comp - removable-component) (not (fixed-by ?comp ?screw)))
                    (not (at-side ?screw ?side))
                    (removed-verified ?screw))
             0.15 (stuck ?screw)
           )
           (decrease (reward) 1)
         )
)

(:action unscrew-scara-stuck
 :parameters (?screw - screw ?sd - screwdriver ?side - side)
 :precondition (and
                 (not (broken-component ?screw))
                 (not (broken-tool ?sd))
                 (stuck ?screw)
                 (current-mode scara)
                 (current-side ?side)
                 (at-side ?screw ?side)
                 (current-tool ?sd)
                 (valid-sd ?screw ?sd)
                 (forall (?comp - component) (not (hides-component ?comp ?screw)))
               )
 :effect (and
           (probabilistic
             0.2 (and
                   (forall (?comp - removable-component) (not (fixed-by ?comp ?screw)))
                   (not (at-side ?screw ?side))
                   (removed-verified ?screw))
           )
           (decrease (reward) 1)
         )
)

(:action unscrew-power-non-stuck
 :parameters (?screw - screw ?sd - screwdriver ?side - side)
 :precondition (and
                 (not (broken-component ?screw))
                 (not (broken-tool ?sd))
                 (not (stuck ?screw))
                 (current-mode power)
                 (current-side ?side)
                 (at-side ?screw ?side)
                 (current-tool ?sd)
                 (valid-sd ?screw ?sd)
                 (forall (?comp - component) (not (hides-component ?comp ?screw)))
               )
 :effect (and
           (probabilistic
             0.85 (and
                    (forall (?comp - removable-component) (not (fixed-by ?comp ?screw)))
                    (not (at-side ?screw ?side))
                    (removed-verified ?screw))
             0.15 (stuck ?screw)
           )
           (decrease (reward) 1)
         )
)

(:action unscrew-power-stuck
 :parameters (?screw - screw ?sd - screwdriver ?side - side)
 :precondition (and
                 (not (broken-component ?screw))
                 (not (broken-tool ?sd))
                 (stuck ?screw)
                 (current-mode power)
                 (current-side ?side)
                 (at-side ?screw ?side)
                 (current-tool ?sd)
                 (valid-sd ?screw ?sd)
                 (forall (?comp - component) (not (hides-component ?comp ?screw)))
               )
 :effect (and
           (probabilistic
             0.75 (and
                    (forall (?comp - removable-component) (not (fixed-by ?comp ?screw)))
                    (not (at-side ?screw ?side))
                    (removed-verified ?screw))
             0.10 (broken-component ?screw)
           )
           (probabilistic 0.10 (broken-tool ?sd))
           (decrease (reward) 1)
         )
)

;########
;# BASH #
;########

(:action bash
  :parameters (?comp - removable-component ?side - side)
  :precondition (and
                  (not (broken-component ?comp))
                  (not (broken-tool hammer))
                  (at-side ?comp ?side)
                  (current-side ?side)
                  (current-tool hammer)
                  (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                  (forall (?comp_ - component) (not (partially-occludes ?comp_ ?comp)))
                )
  :effect (and
            (probabilistic
              0.25 (and
                     (forall (?screw - screw) (not (fixed-by ?comp ?screw)))
                     (forall (?screw - screw ?side_ - side) (not (at-side ?screw ?side_)))
                     (probabilistic 0.5 (loose ?comp))
                   )
              0.10 (broken-component ?comp))
            (probabilistic 0.05 (broken-tool hammer))
            (decrease (reward) 1)
          )
)

;#####################
;# LEVER (6 ACTIONS) #
;#####################

(:action lever-scara-low-confidence
 :parameters (?comp - removable-component
              ?lp - lever-point
              ?side - side)
 :precondition (and
                 (not (broken-component ?comp))
                 (not (broken-tool flat-sd))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?lp)
                 (has-confidence ?lp low)
                 (current-side ?side)
                 (current-tool flat-sd)
                 (current-mode scara)
                 (imply (not (held)) (current-mode power))
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?lp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic
             0.10 (and (loose ?comp)
                       (when (loose ?comp) (removed-non-verified ?comp)))
             0.05 (removed-non-verified ?comp)
             0.25 (broken-component ?comp)
           )
           (probabilistic 0.25 (broken-tool flat-sd))
           (decrease (reward) 1)
         )
)

(:action lever-scara-medium-confidence
 :parameters (?comp - removable-component
              ?lp - lever-point
              ?side - side)
 :precondition (and
                 (not (broken-component ?comp))
                 (not (broken-tool flat-sd))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?lp)
                 (has-confidence ?lp medium)
                 (current-side ?side)
                 (current-tool flat-sd)
                 (current-mode scara)
                 (imply (not (held)) (current-mode power))
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?lp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic
             0.25 (and (loose ?comp)
                       (when (loose ?comp) (removed-non-verified ?comp)))
             0.10 (removed-non-verified ?comp)
             0.12 (broken-component ?comp)
           )
           (probabilistic 0.12 (broken-tool flat-sd))
           (decrease (reward) 1)
         )
)

(:action lever-scara-high-confidence
 :parameters (?comp - removable-component
              ?lp - lever-point
              ?side - side)
 :precondition (and
                 (not (broken-component ?comp))
                 (not (broken-tool flat-sd))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?lp)
                 (has-confidence ?lp high)
                 (current-side ?side)
                 (current-tool flat-sd)
                 (current-mode scara)
                 (imply (not (held)) (current-mode power))
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?lp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic
             0.60 (and (loose ?comp)
                       (when (loose ?comp) (removed-non-verified ?comp)))
             0.30 (removed-non-verified ?comp)
             0.05 (broken-component ?comp)
           )
           (probabilistic 0.05 (broken-tool flat-sd))
           (decrease (reward) 1)
         )
)

(:action lever-power-low-confidence
 :parameters (?comp - removable-component
              ?lp - lever-point
              ?side - side)
 :precondition (and
                 (not (broken-component ?comp))
                 (not (broken-tool flat-sd))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?lp)
                 (has-confidence ?lp low)
                 (current-side ?side)
                 (current-tool flat-sd)
                 (current-mode power)
                 (imply (not (held)) (current-mode power))
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?lp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic
             0.05 (and (loose ?comp)
                       (when (loose ?comp) (removed-non-verified ?comp)))
             0.10 (removed-non-verified ?comp)
             0.25 (broken-component ?comp)
           )
           (probabilistic 0.25 (broken-tool flat-sd))
           (decrease (reward) 1)
         )
)

(:action lever-power-medium-confidence
 :parameters (?comp - removable-component
              ?lp - lever-point
              ?side - side)
 :precondition (and
                 (not (broken-component ?comp))
                 (not (broken-tool flat-sd))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?lp)
                 (has-confidence ?lp medium)
                 (current-side ?side)
                 (current-tool flat-sd)
                 (current-mode power)
                 (imply (not (held)) (current-mode power))
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?lp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic
             0.20 (and (loose ?comp)
                       (when (loose ?comp) (removed-non-verified ?comp)))
             0.50 (removed-non-verified ?comp)
             0.25 (broken-component ?comp)
           )
           (probabilistic 0.12 (broken-tool flat-sd))
           (decrease (reward) 1)
         )
)

(:action lever-power-high-confidence
 :parameters (?comp - removable-component
              ?lp - lever-point
              ?side - side)
 :precondition (and
                 (not (broken-component ?comp))
                 (not (broken-tool flat-sd))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?lp)
                 (has-confidence ?lp high)
                 (current-side ?side)
                 (current-tool flat-sd)
                 (current-mode power)
                 (imply (not (held)) (current-mode power))
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?lp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic
             0.25 (and (loose ?comp)
                       (when (loose ?comp) (removed-non-verified ?comp)))
             0.60 (removed-non-verified ?comp)
             0.10 (broken-component ?comp)
           )
           (probabilistic 0.05 (broken-tool flat-sd))
           (decrease (reward) 1)
         )
)

;#########################
;# SUCK-AWAY (3 ACTIONS) #
;#########################

(:action suck-away-low-confidence
 :parameters (?comp - removable-component
              ?sp - suction-point
              ?side - side)
 :precondition (and
                 (not (broken-component ?comp))
                 (not (broken-tool suction-tool))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?sp)
                 (has-confidence ?sp low)
                 (current-side ?side)
                 (current-tool suction-tool)
                 (imply (not (held)) (current-mode power))
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?sp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic 0.05 (removed-non-verified ?comp))
           (probabilistic 0.05 (broken-tool suction-tool))
           (decrease (reward) 1)
         )
)

(:action suck-away-medium-confidence
 :parameters (?comp - removable-component
              ?sp - suction-point
              ?side - side)
 :precondition (and
                 (not (broken-component ?comp))
                 (not (broken-tool suction-tool))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?sp)
                 (has-confidence ?sp medium)
                 (current-side ?side)
                 (current-tool suction-tool)
                 (imply (not (held)) (current-mode power))
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?sp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic 0.25 (removed-non-verified ?comp))
           (probabilistic 0.05 (broken-tool suction-tool))
           (decrease (reward) 1)
         )
)

(:action suck-away-high-confidence
 :parameters (?comp - removable-component
              ?sp - suction-point
              ?side - side)
 :precondition (and
                 (not (broken-component ?comp))
                 (not (broken-tool suction-tool))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?sp)
                 (has-confidence ?sp high)
                 (current-side ?side)
                 (current-tool suction-tool)
                 (imply (not (held)) (current-mode power))
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?sp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic 0.50 (removed-non-verified ?comp))
           (probabilistic 0.05 (broken-tool suction-tool))
           (decrease (reward) 1)
         )
)

;###################################
;# EXTRACT-WITH-PLIERS (3 ACTIONS) #
;###################################

(:action extract-with-pliers-low-confidence
 :parameters (?comp - removable-component
              ?pp - pliers-point
              ?side - side)
 :precondition (and
                 (not (broken-tool pliers))
                 (not (broken-component ?comp))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?pp)
                 (has-confidence ?pp low)
                 (current-side ?side)
                 (current-tool pliers)
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?pp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic 0.50 (removed-non-verified ?comp)
                          0.50 (broken-component ?comp))
           (probabilistic 0.05 (broken-tool pliers))
           (decrease (reward) 1)
         )
)

(:action extract-with-pliers-medium-confidence
 :parameters (?comp - removable-component
              ?pp - pliers-point
              ?side - side)
 :precondition (and
                 (not (broken-tool pliers))
                 (not (broken-component ?comp))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?pp)
                 (has-confidence ?pp medium)
                 (current-side ?side)
                 (current-tool pliers)
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?pp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic 0.75 (removed-non-verified ?comp)
                          0.25 (broken-component ?comp))
           (probabilistic 0.05 (broken-tool pliers))
           (decrease (reward) 1)
         )
)

(:action extract-with-pliers-high-confidence
 :parameters (?comp - removable-component
              ?pp - pliers-point
              ?side - side)
 :precondition (and
                 (not (broken-tool pliers))
                 (not (broken-component ?comp))
                 (at-side ?comp ?side)
                 (has-affordance ?comp ?pp)
                 (has-confidence ?pp high)
                 (current-side ?side)
                 (current-tool pliers)
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?pp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (probabilistic 0.85 (removed-non-verified ?comp)
                          0.15 (broken-component ?comp))
           (probabilistic 0.05 (broken-tool pliers))
           (decrease (reward) 1)
         )
)
)
