# 
# This module implements an logical agent and a world for it to explore.
#
# Compiled against Python 2.7
# Author: Stephen Bahr (sbahr@bu.edu)

import logic
import logic_440

class WumpusWorldAgent(logic_440.KnowledgeBasedAgent):
  def __init__(self, cave_size):
    self.KB = logic.PropKB()
    self.size = cave_size

    # example of propositional logic
    #self.KB.tell("B11 <=> (P12|P21)")
    #self.KB.tell("~B11")

    # background knowledge about the wumpus world
    # Every x on the board
    for x in range(1, cave_size + 1):
        #Every y on the board
        for y in range(1, cave_size + 1):

            #Breeze notBreeze Stench notStench
            B = "B" + str(x) + "_" + str(y) + " <=> ("
            notB = "~B" + str(x) + "_" + str(y) + " <=> ("
            S = "S" + str(x) + "_" + str(y) + " <=> ("
            notS = "~S" + str(x) + "_" + str(y) + " <=> ("

            #Lets get the nearby neighbors
            neighbors = get_neighbors(x, y, self.size)

            for n in neighbors:
                B += " P" + str(n[0]) + "_" + str(n[1]) + " |"

            for n in neighbors:
                notB += " ~P" + str(n[0]) + "_" + str(n[1]) + " &"

            for n in neighbors:
                S += " W" + str(n[0]) + "_" + str(n[1]) + " |"

            for n in neighbors:
                notS += " ~W" + str(n[0]) + "_" + str(n[1]) + " &"

            B = B[:-1] + ")"
            notB = notB[:-1] + ")"
            S = S[:-1] + ")"
            notS = notS[:-1] + ")"

            self.KB.tell(B)
            self.KB.tell(notB)
            self.KB.tell(S)
            self.KB.tell(notS)
  def safe(self):
    """
    Use logic to determine the set of locations I can prove to be safe.
    """

    safe_spots = set()
    for x in range(1, self.size + 1):
        for y in range(1, self.size + 1):
            #Current location
            loc = "" + str(x) + "_" + str(y)

            #Add current location spot to the safe_spots
            if logic_440.resolution(self.KB, logic.expr("L" + loc)):
                safe_spots.add((x,y))

            #Not a pit or not a wumpus at current location
            if logic_440.resolution(self.KB, logic.expr("~P" + loc)) and logic_440.resolution(self.KB, logic.expr("~W" + loc)):
                safe_spots.add((x,y))

            # If no smell, and no breeze, then all neighbors are safe locations.
            no_smell = logic_440.resolution(self.KB, logic.expr("~S" + loc))
            no_breeze = logic_440.resolution(self.KB, logic.expr("~B" + loc))
            if (no_smell and no_breeze):
                for n in get_neighbors(x, y, self.size):
                    #print "Adding " + str(n) + " to safe_spots"
                    safe_spots.add(n)

    return safe_spots

  def not_unsafe(self):
    """
    Use logic to determine the set of locations I can't prove to be unsafe
    """
    not_unsafe_spots = set()
    for x in range(1, self.size + 1):
        for y in range(1, self.size + 1):

            #Current location
            loc = "" + str(x) + "_" + str(y)

            if not logic_440.resolution(self.KB, logic.expr("L" + loc)):
                not_unsafe_spots.add((x,y))

            if logic_440.resolution(self.KB, logic.expr("P" + loc)) or logic_440.resolution(self.KB, logic.expr("W" + loc)):
                if not_unsafe_spots.__contains__((x,y)):
                    not_unsafe_spots.remove((x,y))

            # If no smell, and no breeze, then all neighbors are safe locations.
            no_smell = logic_440.resolution(self.KB, logic.expr("~S" + loc))
            no_breeze = logic_440.resolution(self.KB, logic.expr("~B" + loc))
            if (no_smell and no_breeze):
                for n in get_neighbors(x, y, self.size):
                    #print "Adding " + str(n) + " to not_unsafe_spots"
                    not_unsafe_spots.add(n)

    return not_unsafe_spots

  def unvisited(self):
    """
    Use logic to determine the set of locations I haven't visited yet.
    """
    result = set()
    for x in range(1, self.size + 1):
        for y in range(1, self.size + 1):
            if not logic_440.resolution(self.KB, logic.expr("L" + str(x) + "_" + str(y))):
                result.add((x,y))

    return result

NEIGHBOR_DELTAS = ((+1, 0), (-1, 0), (0, +1), (0, -1))

def get_neighbors(x, y, cave_size):
  """
  Return a list of neighbors given the canvas size, and the current coordinates
  """
  possible_neighbors = [(x + dx, y + dy) for dx, dy in NEIGHBOR_DELTAS]
  return [(x1, y1) for x1, y1 in possible_neighbors if 
      1 <= x1 <= cave_size and 1 <= y1 <= cave_size]


class World:
  def __init__(self, size, gold, pits, wumpus):
    self.size = size
    self.gold = gold
    self.pits = pits
    self.wumpus = wumpus

  def perceive(self, (x, y), KB):
    print 'You enter room (%d, %d)' % (x, y)
    KB.tell('L%d_%d' % (x, y))

    if (x, y) in self.pits:
      print 'Oh no, you have fallen into a pit!'
      raise logic_440.GameOver(logic_440.RESULT_DEATH)
    else:
      KB.tell('~P%d_%d' % (x, y))

    if (x, y) == self.wumpus:
      print 'Oh no, you have wandered into the Wumpus\' room!'
      raise logic_440.GameOver(logic_440.RESULT_DEATH)
    else:
      KB.tell('~W%d_%d' % (x, y))

    if any((x1, y1) in self.pits for x1, y1 in get_neighbors(x,y, self.size)):
      print 'You feel a breeze'
      KB.tell('B%d_%d' % (x, y))
    else:
      KB.tell('~B%d_%d' % (x, y))

    if any((x1, y1) == self.wumpus for x1, y1 in get_neighbors(x,y, self.size)):
      print 'You smell a stench'
      KB.tell('S%d_%d' % (x, y))
    else:
      KB.tell('~S%d_%d' % (x, y))

    if (x, y) == self.gold:
      print 'You found the gold!'
      raise logic_440.GameOver(logic_440.RESULT_WIN)

def play(world):
  agent = WumpusWorldAgent(world.size)
  location = 1, 1
  try:
    while True:
      world.perceive(location, agent.KB)
      location = agent.choose_location()
  except logic_440.GameOver as e:
    print {logic_440.RESULT_WIN: 'You have won!',
           logic_440.RESULT_DEATH: 'You have died :(',
           logic_440.RESULT_GIVE_UP: 
           'You have left the cave without finding the gold :( '}[e.result]
    print
    print

def main():
  # Play a world with no Wumpus
  play(World(4, (2, 3), ((3, 1), (3, 3), (4, 4)), (-1, -1)))

  # Play a world with a Wumpus
  play(World(4, (2, 3), ((3, 1), (3, 3), (4, 4)), (1, 3)))

  # Feel free to make up additional worlds and see how your agent does at exploring them!

  #play(World(4, (4, 4), ((3, 1), (3, 3), (4, 4)), (1, 3)))
  #play(World(4, (3, 4), ((3, 1), (3, 3), (4, 4)), (1, 3)))
  #play(World(4, (2, 4), ((3, 1), (3, 3), (4, 4)), (1, 3)))
  #play(World(4, (1, 4), ((3, 1), (3, 3), (4, 4)), (1, 3)))

if __name__ == '__main__':
  main()
