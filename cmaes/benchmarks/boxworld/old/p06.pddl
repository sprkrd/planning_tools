(define
 (problem box-p06)
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
            city10 - city
            city11 - city
            city12 - city
            city13 - city
            city14 - city
  )
  (:init (box-at-city box0 city8)
         (destination box0 city1)
         (box-at-city box1 city4)
         (destination box1 city12)
         (box-at-city box2 city6)
         (destination box2 city7)
         (box-at-city box3 city1)
         (destination box3 city14)
         (box-at-city box4 city12)
         (destination box4 city8)
         (box-at-city box5 city12)
         (destination box5 city11)
         (box-at-city box6 city9)
         (destination box6 city1)
         (box-at-city box7 city7)
         (destination box7 city3)
         (box-at-city box8 city9)
         (destination box8 city5)
         (box-at-city box9 city4)
         (destination box9 city7)
         (truck-at-city truck0 city0)
         (truck-at-city truck1 city0)
         (plane-at-city plane0 city0)
         (truck-at-city truck2 city1)
         (truck-at-city truck3 city1)
         (plane-at-city plane1 city1)
         (can-drive city0 city11)
         (can-drive city0 city3)
         (can-drive city0 city8)
         (can-drive city0 city10)
         (can-drive city0 city14)
         (wrong-drive1 city0 city11)
         (wrong-drive2 city0 city3)
         (wrong-drive3 city0 city8)
         
         (can-drive city1 city6)
         (can-drive city1 city7)
         (can-drive city1 city13)
         (can-drive city1 city4)
         (wrong-drive1 city1 city6)
         (wrong-drive2 city1 city7)
         (wrong-drive3 city1 city13)
         
         (can-drive city2 city12)
         (can-drive city2 city9)
         (can-drive city2 city8)
         (wrong-drive1 city2 city12)
         (wrong-drive2 city2 city9)
         (wrong-drive3 city2 city8)
         (can-drive city3 city0)
         (can-drive city3 city11)
         (can-drive city3 city8)
         (wrong-drive1 city3 city0)
         (wrong-drive2 city3 city11)
         (wrong-drive3 city3 city8)
         (can-drive city4 city5)
         (can-drive city4 city13)
         (can-drive city4 city1)
         (wrong-drive1 city4 city5)
         (wrong-drive2 city4 city13)
         (wrong-drive3 city4 city1)
         (can-drive city5 city4)
         (can-drive city5 city13)
         (can-drive city5 city9)
         (wrong-drive1 city5 city4)
         (wrong-drive2 city5 city13)
         (wrong-drive3 city5 city9)
         (can-drive city6 city1)
         (can-drive city6 city7)
         (can-drive city6 city13)
         (wrong-drive1 city6 city1)
         (wrong-drive2 city6 city7)
         (wrong-drive3 city6 city13)
         (can-drive city7 city1)
         (can-drive city7 city6)
         (can-drive city7 city13)
         (wrong-drive1 city7 city1)
         (wrong-drive2 city7 city6)
         (wrong-drive3 city7 city13)
         (can-drive city8 city0)
         (can-drive city8 city2)
         (can-drive city8 city3)
         (can-drive city8 city11)
         (can-drive city8 city9)
         (can-drive city8 city12)
         (wrong-drive1 city8 city0)
         (wrong-drive2 city8 city2)
         (wrong-drive3 city8 city3)
         (can-drive city9 city2)
         (can-drive city9 city5)
         (can-drive city9 city8)
         (can-drive city9 city13)
         (can-drive city9 city12)
         (wrong-drive1 city9 city2)
         (wrong-drive2 city9 city5)
         (wrong-drive3 city9 city8)
         (can-drive city10 city14)
         (can-drive city10 city11)
         (can-drive city10 city0)
         (wrong-drive1 city10 city14)
         (wrong-drive2 city10 city11)
         (wrong-drive3 city10 city0)
         (can-drive city11 city0)
         (can-drive city11 city3)
         (can-drive city11 city8)
         (can-drive city11 city10)
         (can-drive city11 city14)
         (wrong-drive1 city11 city0)
         (wrong-drive2 city11 city3)
         (wrong-drive3 city11 city8)
         (can-drive city12 city2)
         (can-drive city12 city9)
         (can-drive city12 city8)
         (wrong-drive1 city12 city2)
         (wrong-drive2 city12 city9)
         (wrong-drive3 city12 city8)
         (can-drive city13 city1)
         (can-drive city13 city4)
         (can-drive city13 city5)
         (can-drive city13 city6)
         (can-drive city13 city7)
         (can-drive city13 city9)
         (wrong-drive1 city13 city1)
         (wrong-drive2 city13 city4)
         (wrong-drive3 city13 city5)
         (can-drive city14 city10)
         (can-drive city14 city11)
         (can-drive city14 city0)
         (wrong-drive1 city14 city10)
         (wrong-drive2 city14 city11)
         (wrong-drive3 city14 city0)
  )
  (:goal (forall (?b - box ?c - city)
                 (imply (destination ?b ?c) (box-at-city ?b ?c))))
  (:goal-reward 1)
  (:metric maximize (reward))
)
