(define (problem p01)
(:domain imagine)
(:objects
  ;motor-axis - component
  lid pcb - removable-component
  lid-s0 lid-s1 lid-s2 lid-s3 pcb-s0 pcb-s1 pcb-s2 pcb-s3 - screw
  lid-a0 pcb-a0 - lever-point
  lid-a1 - suction-point
  pcb-a1 - pliers-point
)
(:init
  (has-affordance lid lid-a0)
  (has-affordance lid lid-a1)
  (has-affordance pcb pcb-a0)
  (has-affordance pcb pcb-a1)
  (has-confidence lid-a0 medium)
  (has-confidence lid-a1 low)
  (has-confidence pcb-a0 low)
  (has-confidence pcb-a1 high)
  (current-mode no-mode)
  (current-tool no-tool)
  (fixed-by lid lid-s0)
  (fixed-by lid lid-s1)
  (fixed-by lid lid-s2)
  (fixed-by lid lid-s3)
  (fixed-by pcb pcb-s0)
  (fixed-by pcb pcb-s1)
  (fixed-by pcb pcb-s2)
  (fixed-by pcb pcb-s3)
  (partially-occludes lid pcb)
  (at-side lid top)
  (at-side pcb bottom)
  (at-side lid-s0 top)
  (at-side lid-s1 top)
  (at-side lid-s2 top)
  (at-side lid-s3 top)
  (at-side pcb-s0 bottom)
  (at-side pcb-s1 bottom)
  (at-side pcb-s2 bottom)
  (at-side pcb-s3 bottom)
  (current-side top)
  (valid-sd lid-s0 flat-sd)
  (valid-sd lid-s1 flat-sd)
  (valid-sd lid-s2 flat-sd)
  (valid-sd lid-s3 flat-sd)
  (valid-sd pcb-s0 flat-sd)
  (valid-sd pcb-s1 flat-sd)
  (valid-sd pcb-s2 flat-sd)
  (valid-sd pcb-s3 flat-sd)
  (valid-mode flat-sd scara)
  (valid-mode flat-sd power)
  (valid-mode suction-tool scara)
  (valid-mode suction-tool power)
  (valid-mode cutter scara)
  (valid-mode pliers power)
  (valid-mode hammer power)
  (opposite-side top bottom)
  (opposite-side left right)
  (opposite-side front back)
  (opposite-side bottom top)
  (opposite-side right left)
  (opposite-side back front)
)
;(:goal (forall (?s - screw) (not (fixed-by lid ?s))))
(:goal (and (removed-verified lid) (removed-verified pcb)))
(:metric maximize (reward))
)
