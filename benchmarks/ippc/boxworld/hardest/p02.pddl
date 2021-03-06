(define (problem box-p02)
(:domain boxworld)
(:objects box0 box1 box2 box3 box4 box5 box6 box7 box8 box9 - box truck0 truck1 - truck plane0 - plane truck2 truck3 - truck plane1 - plane city0 city1 city2 city3 city4 - city)
(:init
  (box-at-city box0 city1)
  (box-at-city box1 city4)
  (box-at-city box2 city2)
  (box-at-city box3 city0)
  (box-at-city box4 city0)
  (box-at-city box5 city0)
  (box-at-city box6 city0)
  (box-at-city box7 city1)
  (box-at-city box8 city1)
  (box-at-city box9 city3)
  (truck-at-city truck0 city0)
  (truck-at-city truck1 city0)
  (plane-at-city plane0 city0)
  (truck-at-city truck2 city1)
  (truck-at-city truck3 city1)
  (plane-at-city plane1 city1)
  (can-drive city0 city3)
  (can-drive city0 city1)
  (can-drive city0 city4)
  (wrong-drive1 city0 city3)
  (wrong-drive2 city0 city1)
  (wrong-drive3 city0 city4)
  (can-drive city1 city0)
  (can-drive city1 city3)
  (can-drive city1 city4)
  (can-drive city1 city2)
  (wrong-drive1 city1 city0)
  (wrong-drive2 city1 city3)
  (wrong-drive3 city1 city4)
  (can-drive city2 city3)
  (can-drive city2 city4)
  (can-drive city2 city1)
  (wrong-drive1 city2 city3)
  (wrong-drive2 city2 city4)
  (wrong-drive3 city2 city1)
  (can-drive city3 city0)
  (can-drive city3 city1)
  (can-drive city3 city2)
  (can-drive city3 city4)
  (wrong-drive1 city3 city0)
  (wrong-drive2 city3 city1)
  (wrong-drive3 city3 city2)
  (can-drive city4 city0)
  (can-drive city4 city1)
  (can-drive city4 city2)
  (can-drive city4 city3)
  (wrong-drive1 city4 city0)
  (wrong-drive2 city4 city1)
  (wrong-drive3 city4 city2)
)
(:goal (and (box-at-city box3 city1) (box-at-city box0 city4) (box-at-city box6 city4) (box-at-city box1 city1) (box-at-city box5 city1) (box-at-city box9 city1) (box-at-city box7 city0) (box-at-city box8 city3) (box-at-city box2 city3) (box-at-city box4 city4)))
(:goal-reward 10)
(:metric maximize (reward))
)