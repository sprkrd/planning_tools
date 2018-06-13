(define (domain imagine)
(:requirements :adl)
(:types component side mode tool affordance affordance-confidence - object
        removable-component static-component - component
        lever-point suction-point pliers-point - affordance
        screwdriver - tool
        screw - removable-component
)

(:constants
  top bottom front back left right - side
  low medium high - affordance-confidence
  scara power no-mode - mode
  flat-screwdriver - screwdriver
  hammer suction-tool pliers cutter no-tool - tool
)

(:predicates
             (associated-affordance ?c - removable-component ?a - affordance)
             (associated-confidence ?a - affordance ?c - affordance-confidence)
             (broken ?c - component)
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
             (removed ?c - removable-component)
             (stuck ?s - screw)
             ; static predicates
             (opposite-side ?s1 ?s2 - side)
             (at-side ?c - component ?s - side)
             (valid-mode ?t - tool ?m - mode)
             (valid-screwdriver ?s - screw ?sd - screwdriver)
)

(:functions
  (total-cost)
)

(:action check-removed
 :parameters (?comp - removable-component ?side - side)
 :precondition (and
                 (current-side ?side)
                 (at-side ?comp ?side)
                 (removed ?comp)
               )
 :effect (and
           (forall (?other - component)
                   (and
                     (not (hides-component ?comp ?other))
                     (not (partially-occludes ?comp ?other))
                   ))
           (forall (?aff - affordance) (not (hides-affordance ?comp ?aff)))
           (not (at-side ?comp ?side))
         )
)

(:action assert-clear
 :parameters (?comp - removable-component)
 :precondition (and
                 (forall (?screw - screw) (not (fixed-by ?comp ?screw)))
                 (forall (?other - component)
                         (and (not (connected ?comp ?other)) (not (connected ?other ?comp))))
               )
 :effect (clear ?comp)
)

(:action switch-tool
  :parameters (?old-tool - tool ?old-mode - mode
               ?new-tool - tool ?new-mode - mode)
  :precondition (and
                  (not (= ?new-tool no-tool))
                  (not (= ?new-mode no-mode))
                  (imply (= ?old-tool ?new-tool) (not (= ?old-mode ?new-mode)))
                  (imply (= ?new-mode power) (not (held)))
                  (current-tool ?old-tool)
                  (current-mode ?old-mode)
                  (valid-mode ?new-tool ?new-mode)
                )
  :effect (and
            (when (not (= ?old-tool ?new-tool))
              (and (not (current-tool ?old-tool)) (current-tool ?new-tool)))
            (when (not (= ?old-mode ?new-mode))
              (and (not (current-mode ?old-mode)) (current-mode ?new-mode)))
            (increase (total-cost) 1)
          )
)

; Cheaper than switching to another tool
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
         )
)

(:action grab-device
  :parameters ()
  :precondition (and
                  (not (held)) 
                  (not (current-mode power))
                )
  :effect (and (held) (increase (total-cost) 1))
)

(:action place-device
  :parameters ()
  :precondition (held)
  :effect (and (not (held)) (increase (total-cost) 1))
)

(:action flip
:parameters (?old-side - side ?new-side - side)
:precondition (and (current-side ?old-side) (held))
:effect (and
          (not (current-side ?old-side))
          (current-side ?new-side)
          (increase (total-cost) 1)
        )
)

(:action unscrew
 :parameters (?screw - screw ?sd - screwdriver ?side - side)
 :precondition (and
                (not (broken ?screw))
                (imply (not (held)) (current-mode power))
                (current-side ?side)
                (at-side ?screw ?side)
                (current-tool ?sd)
                (valid-screwdriver ?screw ?sd)
                (forall (?comp - component) (not (hides-component ?comp ?screw)))
              )
 :effect (and
           (forall (?comp - component) (not (fixed-by ?comp ?screw)))
           (not (at-side ?screw ?side))
           (removed ?screw)
           (increase (total-cost) 1)
         )
)

(:action bash
  :parameters (?comp - removable-component ?side - side)
  :precondition (and
                  (at-side ?comp ?side)
                  (current-side ?side)
                  (current-tool hammer)
                  (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                  (forall (?comp_ - component) (not (partially-occludes ?comp_ ?comp)))
                )
  :effect (and
            (loose ?comp)
            (forall (?screw - screw) (not (fixed-by ?comp ?screw)))
            (forall (?screw - screw ?side - side) (not (at-side ?screw ?side)))
            (increase (total-cost) 100)
          )
)

(:action lever
:parameters (?comp - removable-component
             ?lp - lever-point
             ?conf - affordance-confidence
             ?side - side)
:precondition (and
                (at-side ?comp ?side)
                (associated-affordance ?comp ?lp)
                (associated-confidence ?lp ?conf)
                (current-side ?side)
                (current-tool flat-screwdriver)
                (imply (not (held)) (current-mode power))
                (forall (?comp_ - component) (not (hides-affordance ?comp_ ?lp)))
                (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                (clear ?comp)
              )
:effect (and
          (loose ?comp)
          (increase (total-cost) 1)
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
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (forall (?comp_ - component) (not (partially-occludes ?comp_ ?comp)))
               )
 :effect (and
           (removed ?comp)
           (increase (total-cost) 1)
         )
)

(:action suck-away
  :parameters (?comp - removable-component
               ?sp - suction-point
               ?conf - affordance-confidence
               ?side - side)
  :precondition (and
                  (at-side ?comp ?side)
                  (associated-affordance ?comp ?sp)
                  (associated-confidence ?sp ?conf)
                  (current-side ?side)
                  (current-tool suction-tool)
                  (imply (not (held)) (current-mode power))
                  (forall (?comp_ - component) (not (hides-affordance ?comp_ ?sp)))
                  (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                  (clear ?comp)
                )
  :effect (and
            (removed ?comp)
            (increase (total-cost) 1)
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
           (increase (total-cost) 1)
         )
)

(:action extract-with-pliers
 :parameters (?comp - removable-component
              ?pp - pliers-point
              ?conf - affordance-confidence
              ?side - side)
 :precondition (and
                 (at-side ?comp ?side)
                 (associated-affordance ?comp ?pp)
                 (associated-confidence ?pp ?conf)
                 (current-side ?side)
                 (current-tool pliers)
                 (forall (?comp_ - component) (not (hides-affordance ?comp_ ?pp)))
                 (forall (?comp_ - component) (not (hides-component ?comp_ ?comp)))
                 (clear ?comp)
               )
 :effect (and
           (removed ?comp)
           (increase (total-cost) 1)
         )
)

)
