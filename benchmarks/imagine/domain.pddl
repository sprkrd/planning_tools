(define (domain imagine)
(:requirements :adl)
(:types component side mode tool affordance affordance-confidence - object
        removable-component static-component - component
        lever-point suction-point pliers-point - affordance
        screwdriver - tool
        removable-surface removable-volume connector screw - removable-component
)

(:constants
  top bottom front back left right - side
  low medium high - affordance-confidence
  scara power no-mode - mode
  flat-screwdriver - screwdriver
  hammer suction-tool pliers cutter no-tool - tool
)

(:predicates
             (associated-affordance ?c - removable-component ?a - affordance ?conf - affordance-confidence)
             (broken ?c - component)
             ;(connected ?c1 ?c2 - component ?c3 - connector)
             (current-mode ?m - mode)
             (current-side ?s - side)
             (current-tool ?t - tool)
             (held)
             (hides ?c1 ?c2 - component ?s - side)
             (fixed-by ?e - removable-component ?y - screw)
             (loose ?c - removable-component)
             (partially-occludes ?c1 ?c2 - component ?s - side)
             (removed ?c - removable-component)
             ; static predicates
             (visible-from-side ?c - component ?s - side)
             (valid-mode ?t - tool ?m - mode)
             (valid-screwdriver ?s - screw ?sd - screwdriver)
)

(:functions
  (total-cost)
)

(:action switch-tool
  :parameters (?old-tool - tool ?old-mode - mode
               ?new-tool - tool ?new-mode - mode)
  :precondition (and
                  (imply (= ?new-tool no-tool) (= ?new-mode no-mode))
                  (not (and (= ?new-mode power) (held)))
                  (current-tool ?old-tool)
                  (current-mode ?old-mode)
                  (valid-mode ?new-tool ?new-mode)
                )
  :effect (and
            (not (current-tool ?old-tool))
            (not (current-mode ?old-mode))
            (current-tool ?new-tool)
            (current-mode ?new-mode)
            (increase (total-cost) 1)
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

(:action bash
  :parameters (?comp - removable-component ?side - side)
  :precondition (and
                  (visible-from-side ?comp ?side)
                  (current-side ?side)
                  (current-tool hammer)
                  (forall (?comp_ - component) (not (hides ?comp_ ?comp ?side)))
                )
  :effect (and
            (loose ?comp)
            (forall (?screw - screw) (not (fixed-by ?comp ?screw)))
            (increase (total-cost) 1)
          )
)

(:action unscrew
:parameters (?screw - screw ?side - side)
:precondition (and
                (visible-from-side ?screw ?side)
                (exists (?sd - screwdriver) (and (current-tool ?sd) (valid-screwdriver ?screw ?sd)))
                (forall (?comp - component) (not (hides ?comp ?screw ?side)))
                (current-side ?side)
              )
:effect (and
          (forall (?comp - component) (not (fixed-by ?comp ?screw)))
          (removed ?screw)
          (increase (total-cost) 1)
        )
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

(:action lever
:parameters (?comp - removable-component
             ?lp - lever-point
             ?conf - affordance-confidence
             ?side - side)
:precondition (and
                (visible-from-side ?comp ?side)
                (associated-affordance ?comp ?lp ?conf)
                (forall (?comp_ - component) (not (hides ?comp_ ?comp ?side)))
                (forall (?screw - screw) (not (fixed-by ?comp ?screw)))
                (current-side ?side)
              )
:effect (and
          (loose ?comp)
          (increase (total-cost) 1)
        )
)

;(:action push-away
;:parameters (?)
;:precondition (and
                ;(held)
                ;;(current-tool none scara)
                ;(loose ?x)
                ;(not (exists (?y - struct) (hides ?y ?x)))
                ;(reachable ?x ?s)
                ;(current-side ?s)
              ;)
;:effect (and
          ;(increase (total-cost) 1)
          ;(forall (?y - struct) (not (hides ?x ?y)))
          ;(not (reachable ?x ?s))
          ;(tossed-away ?x)
        ;)
;)

;(:action Remove_loose
;:parameters (?x - removable ?s - side)
;:precondition (and
                ;(current-tool suction-pad scara)
                ;(loose ?x)
                ;(not (exists (?y - struct) (hides ?y ?x)))
                ;(reachable ?x ?s)
                ;(current-side ?s)
              ;)
;:effect (and
          ;(increase (total-cost) 2)
          ;(forall (?y - struct) (not (hides ?x ?y)))
          ;(not (reachable ?x ?s))
          ;(retrieved ?x)
        ;)
;)


;(:action Remove_non_loose
;:parameters (?x - removable ?s - side)
;:precondition (and
                ;(current-tool suction-pad scara)
                ;(not (loose ?x))
                ;(not (exists (?y - struct) (hides ?y ?x)))
                ;(not (exists (?s - screw) (fixed-by ?x ?s)))
                ;(reachable ?x ?s)
                ;(current-side ?s)
              ;)
;:effect (and
          ;(increase (total-cost) 10)
          ;(forall (?y - struct) (not (hides ?x ?y)))
          ;(not (reachable ?x ?s))
          ;(retrieved ?x)
        ;)
;)

)
