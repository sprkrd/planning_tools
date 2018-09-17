(define
 (problem box-p09)
  (:domain boxworld)
  (:objects box0 - box
            box1 - box
            box2 - box
            box3 - box
            box4 - box
            box5 - box
            box6 - box
            box7 - box
            box8 - box
            box9 - box
            box10 - box
            box11 - box
            box12 - box
            box13 - box
            box14 - box
            truck0 - truck
            truck1 - truck
            plane0 - plane
            truck2 - truck
            truck3 - truck
            plane1 - plane
            city0 - city
            city1 - city
            city2 - city
            city3 - city
            city4 - city
            city5 - city
            city6 - city
            city7 - city
            city8 - city
            city9 - city
  )
  (:init (box-at-city box0 city0)
         (destination box0 city1)
         (box-at-city box1 city5)
         (destination box1 city9)
         (box-at-city box2 city1)
         (destination box2 city5)
         (box-at-city box3 city6)
         (destination box3 city3)
         (box-at-city box4 city3)
         (destination box4 city6)
         (box-at-city box5 city3)
         (destination box5 city6)
         (box-at-city box6 city4)
         (destination box6 city7)
         (box-at-city box7 city6)
         (destination box7 city7)
         (box-at-city box8 city1)
         (destination box8 city4)
         (box-at-city box9 city2)
         (destination box9 city3)
         (box-at-city box10 city7)
         (destination box10 city6)
         (box-at-city box11 city4)
         (destination box11 city6)
         (box-at-city box12 city2)
         (destination box12 city8)
         (box-at-city box13 city9)
         (destination box13 city5)
         (box-at-city box14 city9)
         (destination box14 city7)
         (truck-at-city truck0 city0)
         (truck-at-city truck1 city0)
         (plane-at-city plane0 city0)
         (truck-at-city truck2 city1)
         (truck-at-city truck3 city1)
         (plane-at-city plane1 city1)
         (can-drive city0 city3)
         (can-drive city0 city8)
         (can-drive city0 city2)
         (wrong-drive1 city0 city3)
         (wrong-drive2 city0 city8)
         (wrong-drive3 city0 city2)
         
         (can-drive city1 city4)
         (can-drive city1 city7)
         (can-drive city1 city9)
         (can-drive city1 city5)
         (wrong-drive1 city1 city4)
         (wrong-drive2 city1 city7)
         (wrong-drive3 city1 city9)
         
         (can-drive city2 city0)
         (can-drive city2 city6)
         (can-drive city2 city3)
         (can-drive city2 city9)
         (wrong-drive1 city2 city0)
         (wrong-drive2 city2 city6)
         (wrong-drive3 city2 city3)
         (can-drive city3 city0)
         (can-drive city3 city2)
         (can-drive city3 city8)
         (can-drive city3 city6)
         (wrong-drive1 city3 city0)
         (wrong-drive2 city3 city2)
         (wrong-drive3 city3 city8)
         (can-drive city4 city1)
         (can-drive city4 city7)
         (can-drive city4 city9)
         (can-drive city4 city5)
         (wrong-drive1 city4 city1)
         (wrong-drive2 city4 city7)
         (wrong-drive3 city4 city9)
         (can-drive city5 city4)
         (can-drive city5 city1)
         (can-drive city5 city7)
         (wrong-drive1 city5 city4)
         (wrong-drive2 city5 city1)
         (wrong-drive3 city5 city7)
         (can-drive city6 city2)
         (can-drive city6 city9)
         (can-drive city6 city3)
         (can-drive city6 city8)
         (wrong-drive1 city6 city2)
         (wrong-drive2 city6 city9)
         (wrong-drive3 city6 city3)
         (can-drive city7 city1)
         (can-drive city7 city4)
         (can-drive city7 city5)
         (can-drive city7 city9)
         (wrong-drive1 city7 city1)
         (wrong-drive2 city7 city4)
         (wrong-drive3 city7 city5)
         (can-drive city8 city0)
         (can-drive city8 city3)
         (can-drive city8 city6)
         (wrong-drive1 city8 city0)
         (wrong-drive2 city8 city3)
         (wrong-drive3 city8 city6)
         (can-drive city9 city1)
         (can-drive city9 city2)
         (can-drive city9 city4)
         (can-drive city9 city6)
         (can-drive city9 city7)
         (wrong-drive1 city9 city1)
         (wrong-drive2 city9 city2)
         (wrong-drive3 city9 city4)
  )
  (:goal (forall (?b - box ?c - city)
                 (imply (destination ?b ?c) (box-at-city ?b ?c))))
  (:goal-reward 500)
  (:metric maximize (reward))
)
