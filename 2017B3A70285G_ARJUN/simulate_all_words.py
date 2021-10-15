from Agent import *

s = __import__('2017B3A70285G_ARJUN')

def main():
	import time

	mytime = 0
	max_time = 0
	count = 0
	for w in range(2, 15):
		for p in range(2, 15):
			world = [
			    ['', '', '', ''],  # Rooms [1,1] to [4,1]
			    ['', '', '', ''],  # Rooms [1,2] to [4,2]
			    ['', '', '', ''],  # Rooms [1,3] to [4,3]
			    ['', '', '', ''],  # Rooms [1,4] to [4,4]
			]
			if p != 4 and w != 4:
				count += 1
				if count < 0:
					continue
				if count == 108 or count == 141:
					continue
				world[p % 4][p//4] += 'P'
				world[w % 4][w//4] += 'W'
				print(f"         {world[3]} <- end")
				print(f"         {world[2]}       ")
				print(f"         {world[1]}       ")
				print(f"start -> {world[0]}       ")
				stime = time.time()
				ag = Agent(world)
				kb = s.KB()
				s.simulate(ag, kb)
				totTime = time.time() - stime
				mytime += totTime
				print(f"World #{count}: {totTime:.4} seconds")
				print()
				if totTime > max_time:
					worst_world = world
					max_time = totTime
				if count % 20 == 0:
					print("--------------------------------------------------------------")
					print("Worlds seen: ", count)
					print("--------------------------------------------------------------")
	print(count)
	print("Worst world:")
	print(f"{worst_world[3]}")
	print(f"{worst_world[2]}")
	print(f"{worst_world[1]}")
	print(f"{worst_world[0]}")
	print(f"Worst time: {max_time}")

	print(s.no_of_DPLL_calls)
	print(mytime)

if __name__ == '__main__':
	main()