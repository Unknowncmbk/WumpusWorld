"""Library of logic functions for Assignment 3, CS440, Spring 2014

This module contains two items for use in assignment 3.

resolution(KB, q): Given a propositional knowledge base and query, return
whether the query can be inferred from the knowledgebase using resolution.
The implementation is more efficient than pl_resolution in the AIMA code.

KnowledgeBasedAgent: An abstract class that makes decisions to navigate
through a world based on its knowledge.
"""

import collections
import logic

RESULT_DEATH = 0
RESULT_GIVE_UP = 1
RESULT_WIN = 2

class GameOver(Exception):
  """A class representing the event of the game ending."""
  def __init__(self, result):
    """Result is one of the RESULT constants above."""
    self.result = result


# Utility functions
def normalize(clause):
  return frozenset(map(str, logic.disjuncts(clause)))

def negate(literal):
  if literal[0] == '~': return literal[1:]
  else: return '~' + literal


def resolution(KB, alpha):
  """Apply the resolution algorithm to determine if alpha can be inferred from KB.

  Args:
    KB: an instance of logic.PropKB
    alpha: an instance of logic.Expr

  Return True if KB |- alpha
  """
  # We do not want to waste effort resolving clauses of the KB against
  # one another directly, we only want to resolve clauses that contain
  # information derived from alpha.  tainted_clauses will be the set
  # we grow.
  tainted_clauses = set(normalize(clause)
      for clause in logic.conjuncts(logic.to_cnf(~alpha)))
  KB_clauses = [normalize(clause) for clause in KB.clauses]
  new = set()
  while True:
    # clausesWith is a map from literals to clauses containing that literal.
    clausesWith = collections.defaultdict(list)
    for clause in list(tainted_clauses) + KB_clauses:
      for literal in clause:
        clausesWith[literal].append(clause)

    # For each tainted clause, add a pair of that clause and any
    # tainted or KB clause that matches it (i.e. opposes on one literal).
    pairs = []
    for clause0 in tainted_clauses:
      for literal in clause0:
        for clause1 in clausesWith[negate(literal)]:
          pairs.append((literal, clause0, clause1))

    # Resolve all the pairs found above.  If any result in None, the 
    # resolution is a bust (provides no new information).
    # If any result in False (empty set), we have reached a contradiction
    # and proven our goal.
    for literal, clause0, clause1 in pairs:
      result = resolve(clause0, clause1, literal)
      if result is not None:
        if result == set(): return True
        else: new.add(frozenset(result))

    # We now survey all the new clauses.  In order to want to keep them,
    # they must not be a superset of any already-known clause (since that
    # would provide no new information).
    added = False
    for clause in new:
      if not any(old_clause.issubset(clause)
          for old_clause in list(tainted_clauses) + KB_clauses):
        tainted_clauses.add(clause)
        added = True

    # If we have not found any new information, we've reached the end
    # and cannot prove our goal (it may be True, it may be False, but we
    # can't definitively say either way).
    if not added: return False


def resolve(clause0, clause1, literal):
  """Resolve two clauses.

  Each input clause is represented as a sequence of strings, each string being
  one literal.  The two clauses must be resolvable, one containing literal,
  the other the negation of literal.

  Args:
    clause0: An arbitrary clause, containing literal.
    clause1: An arbitrary clause, containing the negation of literal.
    literal: A string.

  Returns:
    None if the two clauses also match on a different literal, because
        in that case, all the resolved clauses would be equivalent to True
    The empty set if the two clauses are exactly literal and not-literal,
        i.e. they resolve to False
    Otherwise, a frozenset of literals, the resolved clause.
  """
  clause0 = set(clause0)
  clause1 = set(clause1)
  clause0.remove(literal)
  clause1.remove(negate(literal))
  if any(negate(other) in clause1 for other in clause0): return None
  return clause0.union(clause1)


class KnowledgeBasedAgent:
  def __init__(self):
    self.KB = logic.PropKB()

  def safe(self):
    """Return the set of safe locations to move to."""
    raise NotImplementedError()

  def not_unsafe(self):
    """Return the set of locations that can't be proven unsafe to move to."""
    raise NotImplementedError()

  def unvisited(self):
    """Return the set of locations that haven't yet been visited."""
    raise NotImplementedError()

  def choose_location(self):
    """Return the next location to explore in the search for gold."""
    unvisited_locations = self.unvisited()
    safe_moves = self.safe().intersection(unvisited_locations)
    if safe_moves:
      location = min(safe_moves)
      print 'Moving to safe location', location
    else:
      not_unsafe_moves = self.not_unsafe().intersection(unvisited_locations)
      if not_unsafe_moves:
        location = min(not_unsafe_moves)
        print 'Taking a risk; moving to a not-unsafe location', location
      else:
        print 'Nowhere left to go'
        raise GameOver(RESULT_GIVE_UP)
    return location
