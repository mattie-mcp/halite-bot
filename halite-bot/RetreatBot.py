import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square, opposite_cardinal
import random



myID, game_map = hlt.get_init()
hlt.send_init("RetreatBot")


def find_nearest_enemy_direction(square):
    direction = NORTH
    max_distance = min(game_map.width, game_map.height) / 2
    for d in (NORTH, EAST, SOUTH, WEST):
        distance = 0
        current = square
        while current.owner == (myID or 0) and distance < max_distance:
            distance += 1
            current = game_map.get_target(current, d)
        if distance < max_distance:
            direction = d
            max_distance = distance
    return direction, max_distance

def heuristic(square):
    if square.owner == 0 and square.strength > 0:
        return square.production / square.strength
    else:
        # return total potential damage caused by overkill when attacking this square
        return sum(neighbor.strength for neighbor in game_map.neighbors(square) if neighbor.owner not in (0, myID))

def get_move(square):
	#returns neighbor/direction of neighbor with highest prod/strength ratio
    target, direction = max(((neighbor, direction) for direction, neighbor in enumerate(game_map.neighbors(square))
                                if neighbor.owner != myID),
                                default = (None, None),
                                key = lambda t: heuristic(t[0]))
    if target is not None and target.strength < square.strength:
        return Move(square, direction)
    elif square.strength < square.production * 5:
        return Move(square, STILL)

    border = any(neighbor.owner != myID for neighbor in game_map.neighbors(square))
    if not border:
        return Move(square, find_nearest_enemy_direction(square))
    else: 
        #wait until we are strong enough to attack
		#if the nearest enemy is within 3, retreat. otherwise stay still
        info = find_nearest_enemy_direction(square)
        if info[1] > 2:
            return Move(square, STILL)
        else:
            return Move(square, opposite_cardinal(info[0]))

while True:
    game_map.get_frame()
    moves = [get_move(square) for square in game_map if square.owner == myID]
    hlt.send_frame(moves)

