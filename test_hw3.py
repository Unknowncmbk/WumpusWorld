import unittest

import hw3
import logic
import logic_440


class Test(unittest.TestCase):
  def test_background_knowledge(self):
    print Test
    agent = hw3.WumpusWorldAgent(4)
    agent.KB.tell(logic.expr('B1_1'))
    agent.KB.tell(logic.expr('~P1_2'))
    self.assertTrue(logic_440.resolution(agent.KB, logic.expr('P2_1')))

  def test_safe(self):
    agent = hw3.WumpusWorldAgent(4)
    agent.KB.tell(logic.expr('P2_3'))
    agent.KB.tell(logic.expr('~P1_1'))
    agent.KB.tell(logic.expr('~W1_1'))
    safe = agent.safe()
    self.assertTrue((2, 3) not in safe)
    self.assertTrue((1, 1) in safe)

  def test_not_unsafe(self):
    agent = hw3.WumpusWorldAgent(4)
    agent.KB.tell(logic.expr('P2_3'))
    not_unsafe = agent.not_unsafe()
    self.assertTrue((2, 3) not in not_unsafe)
    self.assertTrue((1, 1) in not_unsafe)

  def test_unvisited(self):
    agent = hw3.WumpusWorldAgent(4)
    agent.KB.tell(logic.expr('L2_3'))
    unvisited = agent.unvisited()
    self.assertTrue((2, 3) not in unvisited)
    self.assertTrue((1, 1) in unvisited)

if __name__ == '__main__':
  unittest.main()
