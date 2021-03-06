;; Authors: Michael Littman and David Weissman
;; Modified by: Blai Bonet

;; Comment: Good plans are those that avoid putting blocks on table since the probability of detonation is higher

(define (problem p01)
  (:domain exploding-blocksworld)
  (:objects b1 b2 b3 b4 b5 - block)
  (:init (emptyhand) (on b1 b4) (on-table b2) (on b3 b2) (on b4 b5) (on-table b5) (clear b1) (clear b3) (no-detonated b1) (no-destroyed b1) (no-detonated b2) (no-destroyed b2) (no-detonated b3) (no-destroyed b3) (no-detonated b4) (no-destroyed b4) (no-detonated b5) (no-destroyed b5) (no-destroyed-table) (= (total-cost) 0))
  (:goal (and (on b2 b4) (on-table b4)  )
)
  (:metric minimize (total-cost))
)
