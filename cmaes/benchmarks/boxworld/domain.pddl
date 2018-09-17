;; Generated by boxworld generator
;; http://www.cs.rutgers.edu/~jasmuth/boxworld.tar.gz
;; by John Asmuth (jasmuth@cs.rutgers.edu)

; [Alejandro] The domain has been modified to adapt the expressivity
; to our tools and to make it more interesting. In the old domain, the trivial
; no-risk solution is to just use planes. In this version, the planes can
; take just one package and the cost of flying is higher than the cost of
; driving

(define (domain boxworld)
 (:requirements :adl :rewards)
 (:types city box truck plane)
 (:predicates (box-at-city ?b - box ?c - city)
              (truck-at-city ?t - truck ?c - city)
              (box-on-truck ?b - box ?t - truck)
              (plane-at-city ?p - plane ?c - city)
              (box-on-plane ?b - box ?p - plane)
              (can-drive ?src - city ?dst - city)
              (full-plane ?p - plane)
              (wrong-drive1 ?src - city ?wrongdst - city)
              (wrong-drive2 ?src - city ?wrongdst - city)
              (wrong-drive3 ?src - city ?wrongdst - city))

 (:action load-box-on-truck-in-city
  :parameters (?b - box ?t - truck ?c - city)
  :precondition (and
                  (box-at-city ?b ?c)
                  (truck-at-city ?t ?c))
  :effect (and
            (box-on-truck ?b ?t)
            (not (box-at-city ?b ?c))))

 (:action unload-box-from-truck-in-city
  :parameters (?b - box ?t - truck ?c - city)
  :precondition (and
                  (box-on-truck ?b ?t)
                  (truck-at-city ?t ?c))
  :effect (and
            (box-at-city ?b ?c)
            (not (box-on-truck ?b ?t))))

 (:action load-box-on-plane-in-city
  :parameters (?b - box ?p - plane ?c - city)
  :precondition (and
                  (box-at-city ?b ?c)
                  (not (full-plane ?p))
                  (plane-at-city ?p ?c))
  :effect (and
            (full-plane ?p)
            (box-on-plane ?b ?p)
            (not (box-at-city ?b ?c))))

 (:action unload-box-from-plane-in-city
  :parameters (?b - box ?p - plane ?c - city)
  :precondition (and
                  (box-on-plane ?b ?p)
                  (plane-at-city ?p ?c))
  :effect (and
            (not (full-plane ?p))
            (box-at-city ?b ?c)
            (not (box-on-plane ?b ?p))))

 (:action drive-truck
  :parameters (?t - truck ?src ?dst ?wrg1 ?wrg2 ?wrg3 - city)
  :precondition (and (truck-at-city ?t ?src)
                     (can-drive ?src ?dst)
                     (wrong-drive1 ?src ?wrg1)
                     (wrong-drive2 ?src ?wrg2)
                     (wrong-drive3 ?src ?wrg3))
  :effect (and (decrease (reward) 1)
               (not (truck-at-city ?t ?src))
               (probabilistic
                0.2 (probabilistic
                      1/3 (truck-at-city ?t ?wrg1)
                      1/3 (truck-at-city ?t ?wrg2)
                      1/3 (truck-at-city ?t ?wrg3)
                    )
                0.8 (truck-at-city ?t ?dst)
               )))

 (:action fly-plane
  :parameters (?p - plane ?src - city ?dst - city)
  :precondition (and (plane-at-city ?p ?src))
  :effect (and (decrease (reward) 2)
               (not (plane-at-city ?p ?src))
               (plane-at-city ?p ?dst))
 )

)
