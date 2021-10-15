#!/usr/bin/env python3
"""
	Author: Arjun Agarwal
	ID: 2017B3A70285G
	Date Created: 12th October 2020

	NOTE: I have used indexing from (0,0) to (3, 3) for the grid in my code. Necessary conversions have been made
"""

from copy import deepcopy
from itertools import combinations, product  # Permission taken from the IC

from Agent import *

no_of_DPLL_calls = 0

##### Keys and a utility function for all the possible literals
W = [  # Wumpus
	[100, 101, 102, 103],
	[110, 111, 112, 113],
	[120, 121, 122, 123],
	[130, 131, 132, 133]
]
P = [  # Pit
	[200, 201, 202, 203],
	[210, 211, 212, 213],
	[220, 221, 222, 223],
	[230, 231, 232, 233]
]
S = [  # Stench
	[300, 301, 302, 303],
	[310, 311, 312, 313],
	[320, 321, 322, 323],
	[330, 331, 332, 333]
]
B = [  # Breeze
	[400, 401, 402, 403],
	[410, 411, 412, 413],
	[420, 421, 422, 423],
	[430, 431, 432, 433]
]


def uf(entity, tup):  # For easily retrieving the numeric values of the literals
	return entity[tup[0]][tup[1]]


# A utility function to find neighbouring rooms of a given room
def get_neighbouring_rooms(cur_room):
	i, j = cur_room

	surrounding_rooms = set()
	if j < 3: surrounding_rooms.add(((i, j + 1), 'Up'))
	if i < 3: surrounding_rooms.add(((i + 1, j), 'Right'))
	if i > 0: surrounding_rooms.add(((i - 1, j), 'Left'))
	if j > 0: surrounding_rooms.add(((i, j - 1), 'Down'))

	return surrounding_rooms


class Clause:
	def __init__(self, literals):
		for literal in literals:
			if -literal in literals:
				print('Clause is inherently unsatisfiable')
				exit(1)

		self.literals = frozenset(literals)

	def is_unit_clause(self, assignments):
		if self.is_satisfied(assignments): return False

		count = 0
		for literal in self.literals:
			if -literal not in assignments: count += 1
			if count > 1: break

		return count == 1

	def is_satisfied(self, assignments):
		if len(self.literals.intersection(assignments)) != 0: return True
		return False

	def is_unsatisfiable(self, assignments):
		count = 0
		for literal in self.literals:
			if -literal not in assignments:
				count += 1
				break

		return count == 0

	def __hash__(self):
		return hash(self.literals)


class KB:

	def __init__(self):
		self._clauses = set()
		self._all_literals = set()  # Maintain a set of active literals
		# self._assignments = set()  # Assignment will be True

		self._add_prelimary_clauses()

	def TELL(self, clause):
		if not isinstance(clause, Clause):
			exit(2)

		self._clauses.add(clause)

		for literal in clause.literals:
			self._all_literals.add(literal)
			self._all_literals.add(-literal)

		return 0

	def ASK(self, clause):
		KB_to_check = deepcopy(self)

		for literal in clause.literals:
			KB_to_check.TELL(Clause([-literal]))

		satisfiable = KB_to_check._DPLL()

		return not satisfiable


	def _add_prelimary_clauses(self):
		loc_combs = [i for i in combinations(product([0, 1, 2, 3], [0, 1, 2, 3]), 2)]

		# Exactly one Wumpus is present
		self.TELL(Clause([W[i][j] for i in range(0, 4) for j in range(0, 4)]))  # Atleast one Wumpus
		for loc_comb in loc_combs:
			self.TELL(Clause([-uf(W, loc_comb[0]), -uf(W, loc_comb[1])]))  # Atmost one Wumpus

		# Wumpus is not present in (0, 0) or (3, 3)
		self.TELL(Clause([-W[0][0]]))
		self.TELL(Clause([-W[3][3]]))

		# Exactly one Pit is present
		self.TELL(Clause([P[i][j] for i in range(0, 4) for j in range(0, 4)]))  # Atleast one Pit
		for loc_comb in loc_combs:
			self.TELL(Clause([-uf(P, loc_comb[0]), -uf(P, loc_comb[1])]))  # Atmost one Pit

		# Pit is not present in (0, 0) or (3, 3)
		self.TELL(Clause([-P[0][0]]))
		self.TELL(Clause([-P[3][3]]))

		# Stench <-> Wumpus relationship
		for i in range(0, 4):
			for j in range(0, 4):
				surrounding_rooms = get_neighbouring_rooms((i, j))

				self.TELL(Clause(  # Prescence of Wumpus implies Stench
					[uf(W, x[0]) for x in surrounding_rooms] +
					[-S[i][j]]
				))

				for room in surrounding_rooms:  # Prescence of Stench implies Wumpus
					self.TELL(Clause([S[i][j], -uf(W, room[0])]))

		# Breeze <-> Pit relationship
		for i in range(0, 4):
			for j in range(0, 4):
				surrounding_rooms = get_neighbouring_rooms((i, j))

				self.TELL(Clause(  # Prescence of Pit implies Breeze
					[uf(P, x[0]) for x in surrounding_rooms] +
					[-B[i][j]]
				))

				for room in surrounding_rooms:  # Prescence of Breeze implies Pit
					self.TELL(Clause([B[i][j], -uf(P, room[0])]))

		return 0

	def _get_unit_clause(self, assignments):
		for clause in self._clauses:
			if clause.is_unit_clause(assignments):
				return True, clause

		return False, 0

	def _get_pure_symbol(self, active_literals, assignments):
		literal_count = {}

		for clause in self._clauses:
			if not clause.is_satisfied(assignments):
				for literal in clause.literals:
					if literal in active_literals:
						if literal not in literal_count:
							literal_count[literal] = 0
							literal_count[-literal] = 0

						literal_count[literal] += 1

		for literal in literal_count:
			if literal_count[literal] == 0 and literal_count[-literal] > 0:
				return True, -literal

		return False, 0

	@staticmethod
	def _assign_literal(literal, active_literals, assignments, reassigning=False):
		if -literal in assignments:
			return False

		if reassigning:
			if literal not in assignments:
				exit(4)

			assignments.remove(literal)
			assignments.add(-literal)
		else:
			active_literals.discard(literal)
			active_literals.discard(-literal)
			assignments.add(literal)

		return True

	def _DPLL(self, active_literals=None, assignments=None):
		global no_of_DPLL_calls
		no_of_DPLL_calls += 1
		# if no_of_DPLL_calls % 5000 == 0: print(no_of_DPLL_calls)

		if active_literals is None:
			active_literals = deepcopy(self._all_literals)
		else:
			active_literals = deepcopy(active_literals)
		if assignments is None:
			assignments = set()
		else:
			assignments = deepcopy(assignments)

		# Early termination heuristic
		satisfied = True
		for clause in self._clauses:
			if clause.is_unsatisfiable(assignments):
				# print(len(assignments), 'Unsatisfiable')
				return False
			elif satisfied and not clause.is_satisfied(assignments):
				satisfied = False

		if satisfied:
			# print(len(assignments), 'Satisfied')
			return True

		# Pure symbol heuristic
		found, literal = self._get_pure_symbol(active_literals, assignments)
		if found:
			# print('%d is a pure literal' % literal)
			if not self._assign_literal(literal, active_literals, assignments): return False
			return self._DPLL(active_literals, assignments)

		# Unit clause heuristic
		found, clause = self._get_unit_clause(assignments)
		if found:
			(literal,) = clause.literals - set([-literal for literal in assignments])
			# print('%s is a unit clause' % clause.to_string(assignments))
			if not self._assign_literal(literal, active_literals, assignments): return False
			return self._DPLL(active_literals, assignments)

		# Otherwise check for both values
		literal = active_literals.pop()

		# print('Assigning literal %d' % literal)
		if not self._assign_literal(literal, active_literals, assignments): return False
		if self._DPLL(active_literals, assignments): return True

		# print('Reassigning literal %d' % literal)`
		if not self._assign_literal(literal, active_literals, assignments, reassigning=True): return False
		return self._DPLL(active_literals, assignments)


def simulate(Agent, KB, cur_loc=(0, 0), rooms_explored=None):
	if rooms_explored is None:
		rooms_explored = set()

	if cur_loc == (3, 3):
		return True

	breeze, stench = Agent.PerceiveCurrentLocation()
	if breeze is None or stench is None:
		print('Agent is DEAD or has already EXITED')
		exit(5)
	else:
		print('Agent perceives [breeze, stench]: [%s, %s]' % (breeze, stench))

	if breeze:
		KB.TELL(Clause([uf(B, cur_loc)]))
	else:
		KB.TELL(Clause([-uf(B, cur_loc)]))

	if stench:
		KB.TELL(Clause([uf(S, cur_loc)]))
	else:
		KB.TELL(Clause([-uf(S, cur_loc)]))

	def get_next_room_and_path():
		frontier = []
		explored = set()

		neighbouring_rooms = get_neighbouring_rooms(cur_loc)
		for neighbouring_room, action in neighbouring_rooms:
			frontier.append((neighbouring_room, (action,)))

		explored.add(cur_loc)

		while frontier:
			frontier.sort(key=lambda a: len(a[1]) + 8 - a[0][0] - a[0][1])  # A room nearer to the exit is preferred

			new_room, path = frontier.pop(0)
			explored.add(new_room)

			if new_room in rooms_explored:
				neighbouring_rooms_of_new_room = get_neighbouring_rooms(new_room)
				for neighbouring_room_of_new_room, action in neighbouring_rooms_of_new_room:
					if neighbouring_room_of_new_room not in explored:
						frontier.append((neighbouring_room_of_new_room, path + (action,)))
			else:
				if KB.ASK(Clause([-uf(W, new_room)])) and KB.ASK(Clause([-uf(P, new_room)])):
					return new_room, path

		print("No safe room found")
		return None, None

	next_room, path = get_next_room_and_path()
	if next_room is None or path is None: exit(7)

	for action in path:
		if not Agent.TakeAction(action):
			print('Agent is DEAD or has already EXITED')
			exit(6)

	rooms_explored.add(cur_loc)

	return simulate(Agent, KB, next_room, rooms_explored)


def main():
	myKB = KB()
	myAgent = Agent()

	print('Agent starts at ', myAgent.FindCurrentLocation())

	if simulate(myAgent, myKB):
		print('Agent has exited successfully')
	else:
		print('Agent could not find his way out! :(')

	print(f'Number of calls made to the DPLL function: {no_of_DPLL_calls}')


if __name__ == '__main__':
	main()
