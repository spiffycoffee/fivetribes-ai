from __future__ import print_function
from random import randint, seed

# Boards are represented by a string of tiles, separated with commas

# Tiles definitions have 2 components, always in the following order:
# 1) The Value - a 1 or 2 digit number from 3 to 12
# 2) The Type  - 1 of the 5 corresponding characters defined below:
OASSIS        = 'o'  # (Palm tree tile, Red)
VILLAGE       = 'v'  # (Palace tile,    Blue)  
SACRED_PLACE  = 's'  # (Djinn tile,     Blue)
HALF_MARKET   = 'h'  # (3 coin market,  Red)
FULL_MARKET   = 'f'  # (6 coin market,  Red)
# ** Each tile type is always Red/Blue, so we do not need to declare color separately

MY_CAMEL = '+'
OPPONENT_CAMEL = '-'
NO_CAMEL = ''


# Meeples are represented with the below characters
RED    = 'r'  # Assassins
BLUE   = 'b'  # Builders
GREEN  = 'g'  # Merchants
WHITE  = 'w'  # Elders
YELLOW = 'y'  # Viziers
# Declare meeple positions and counts with another comma separated string. 
# Use multiple letters for multiple meeples 

# or take as input diagram?
# -------------------------
# | rrgby   |
# | 12o-ctp |


test_board = "3v,5o,6s,2h,11f,3s,13o,5h,7f,12s,7o,8h"
test_meeples = "r,g,b,y,w,rgb,yw,rr,rrb,rrbb,rgbyw,rrggbbyyww"
num_cols = 3
num_rows = 4

test_board = "3v,5o,6s,2h,11f,3s,13o,5h,7f"
test_meeples = "r,g,b,y,w,rgb,yw,rr,rrb"
num_cols = 3
num_rows = 3

#test_board = "3v,5o,6s,2h"
#test_meeples = "r,r,b,b"
#num_cols = 2
#num_rows = 2


def init_board(t,m):
	board = []
	
	# TODO filter out whitespace? make whitespace the deliminator?
	for tile in t.split(','):
		board.append({'meeples': [],
					 'value'   : int(tile[:-1]), 
					 'type'    : tile[-1], 
					 'trees'   : 0, 
					 'palaces' : 0, 
					 'camel'   : ''}) 
	for i, meeples in enumerate(m.split(',')):
		board[i]['meeples'] = list(meeples)
	
	pretty_print_board2(board, num_rows, num_cols)
	return board

# for each tile
def find_moves(board, n_rows, n_cols):
	result = []
	for i, tile in enumerate(board):
		if tile['meeples']:  
			#result += moves(len(tile['meeples']), '', i, i, (board, n_rows, n_cols))
			#TODO remove meeples from starting tile, deep copy at every recursion?
			#     instead of n, pass list of meeples?
			temp = moves(len(tile['meeples']), '', i, i, (board, n_rows, n_cols))
			print("tile %d:\n%s" % (i, set(temp)))
	# TODO implement pretty print?
	#pretty_print_result(result)

def moves(n, prev_dir, curr_idx, start_idx, board_info):
#	print n
	if n == 0:  
		tile_result = check_end_tile(start_idx, curr_idx, board_info) 
#		tile_result = check_end_tile(board_info[0][start_idx], 
#									 board_info[0][curr_idx], 
#									 board_info) 
#		print tile_result
		return [(curr_idx, r) for r in tile_result] if tile_result else []
	
	n_rows = board_info[1]
	n_cols = board_info[2]
	result = []
	# if not top row
	if curr_idx >= n_cols and prev_dir != 'S' : 				
		# move up 
		result += moves(n-1, 'N', curr_idx-n_cols, start_idx, board_info)  
	# if not right column
	if curr_idx % n_cols < n_cols-1 and prev_dir != 'W':
		# move right 
		result += moves(n-1, 'E', curr_idx+1, start_idx, board_info)  
	# if not bottom row
	if curr_idx < (n_rows-1) * n_cols and prev_dir != 'N':	    
		# move down 
		result += moves(n-1, 'S', curr_idx+n_cols, start_idx, board_info)  
	# if not left column
	if curr_idx % n_cols != 0 and prev_dir != 'E': 
		# move left 
		result += moves(n-1, 'W', curr_idx-1, start_idx, board_info)  
	return result

# find all tiles that can be moved to 
#	of those, which are valid (meeple match)	
#	of those, compute score
#	highest scoring? save all possible scores?
# TODO replace start_idx with list of starting meeple?
def check_end_tile(curr_idx, start_idx, board_info):
#def check_end_tile(end_tile, start_tile, board_info):
	starting_meeples = board_info[0][start_idx]['meeples']
	end_tile = board_info[0][curr_idx]
	
	if not end_tile['meeples']:
		return []  # can't end on tile with no meeples
	
	result = []
	#for m in set(board_info[0][start_idx]['meeples']):
	for m in set(starting_meeples):
		if m in end_tile['meeples']:
			result += [(m, calc_score(m, curr_idx, board_info))]
	return result 


def calc_score(meeple, curr_idx, board_info):
	tile = board_info[0][curr_idx].copy() # shallow copy, ok b/c not changing meeples
	return meeple_score(meeple, curr_idx, board_info) \
			+ tile_score(tile) \
			+ camel_score(meeple, tile)

def meeple_score(meeple, curr_idx, board_info):
	tile = board_info[0][curr_idx]

	# TODO fakirs?
	if meeple == RED:
		# Assasin - murder-able tile in range?
		#			kiling vizier knocks their count below yours?
		#			elders?
		return 10
	elif meeple == GREEN:
		# Merchant - what's up for grabs? (not full amount grab-able...)
		#			 what's in your hand?
		#			 how far along are you in your sets,etc
		return 15
	elif meeple == BLUE:
		# Builder - number of blue tiles around this one?
		return score_builders(curr_idx, board_info)	
	elif meeple == WHITE:
		return 2 * (tile['meeples'].count(WHITE) + 1)    # Each elder is worth 2 points
	elif meeple == YELLOW:
		# TODO 10pts for everyone with less viziers?
		return tile['meeples'].count(meeple) + 1 # Each vizier is worth 1 point	
	print('ERROR - THE TRIBES ARE ANGRY')
	return ''

def score_builders(curr_idx, board_info):
	# TODO need whole board to find surrounding tiles?
	return 10

# returns true if all meeples on tile match passed in meeple 
def tile_cleared(meeple, tile):
	return all(m == meeple for m in tile['meeples'])

# Check if a camel can be placed and compute the score for doing so
def camel_score(meeple, tile):
	if tile['camel'] == NO_CAMEL and tile_cleared(meeple, tile):
		tile['camel'] = MY_CAMEL
		return tile['value'] + 3 * tile['trees'] + 5 * tile['palaces'] 
	else:
		return 0

def tile_score(tile):
	if (tile['type']) == OASSIS:
		tile['trees'] += 1 
		return 3 if tile['camel'] == MY_CAMEL else 0
	elif (tile['type']) == VILLAGE:
		tile['palaces'] += 1 
		return 5 if tile['camel'] == MY_CAMEL else 0
	elif (tile['type']) == SACRED_PLACE:
		# TODO return highest value djinn?
		return 10
	elif (tile['type']) == HALF_MARKET:
		# TODO return market calculation, enough coins to buy?
		return 5
	elif (tile['type']) == FULL_MARKET:
		# TODO return market calculation, enough coins to buy?
		return 10
	print('ERROR - THE DJINNS ARE ANGRY')
	return '' 

def pretty_print_board2(board, n_rows, n_cols):
	tile_width = 11 	# min of 10 or alignment breaks
	width = n_cols * tile_width + 1
	n = 0

	print('-' * width)
	for r in range(n_rows):
		row_tiles = board[r*n_cols:(r+1)*n_cols]
		print(end='|')

		# print tile header row
		for tile in row_tiles:
			values = '('+repr(tile['value'])+')'
			print('{:2}: {}{}'.format(n, tile['type'], values.rjust(tile_width-6)), end='|')
			n += 1
		print('\n', end='|')
		
		# print meeples row
		for tile in row_tiles:
			print(''.join(tile['meeples']).center(tile_width-1), end='|')
		print('\n', end='|')

		# print tree/palace/camel row
		for tile in row_tiles:
			camel = '('+tile['camel']+')'
			tree_palaces = 't'*tile['trees'] + 'p'*tile['palaces']
			print('{}{}'.format(tree_palaces.center(tile_width-4), camel.rjust(3)), end='|')

		print('\n'+'-' * width)

def pretty_print_result(result):
#	for r in result:
		#print "S: %i, E: %i, Move: %i" % index_to_coord(, i%num_cols, r[2]
	print([])

def index_to_coord(i, n_rows, n_cols):
	return (i / n_cols, i % n_cols)

def generate_random_board(s):
	seed(s)
	print("Generating random board with seed %s" % s)

	n_cols = 5
	n_rows = 6
	tile_type = [VILLAGE, OASSIS, SACRED_PLACE, HALF_MARKET, FULL_MARKET]
	camel_type = [MY_CAMEL] + [OPPONENT_CAMEL] + [NO_CAMEL]*5

	board = [] 
	for i in range(n_cols * n_rows):
		board.append({'meeples' : [],
						'value': randint(3,12), 
	 					'type' : tile_type[randint(0,4)], 
						'trees': 0, 
						'palaces' : 0, 
						'camel': camel_type[randint(0,len(camel_type)-1)]
						}) 
	for i in range(18):	
		board[randint(0, n_rows * n_cols - 1)]['meeples'] += RED
	for i in range(18):	
		board[randint(0, n_rows * n_cols - 1)]['meeples'] += BLUE
	for i in range(18):	
		board[randint(0, n_rows * n_cols - 1)]['meeples'] += GREEN
	for i in range(20):	
		board[randint(0, n_rows * n_cols - 1)]['meeples'] += WHITE
	for i in range(16):	
		board[randint(0, n_rows * n_cols - 1)]['meeples'] += YELLOW

	pretty_print_board2(board, n_rows, n_cols)
	return board, n_rows, n_cols

#TODO 
#	  from a given tile, determine moves, valid moves, scoring
#	  handle looping moves, handle moves that go back to starting tile properly
#	  represent hand? merchent deck? djinn deck?
#	  conversely, what are tiles with most potential points (even if not accessible right now)


test_tile = {'meeples' : ['r','r','r'],
			 'value': 9, 
			 'type' : VILLAGE, 
			 'trees': 2, 
			 'palaces': 1, 
			 'camel': ''}
print('\n')
print(test_tile)
print(camel_score(RED, test_tile))
print(tile_cleared(RED, test_tile))
print(test_tile)

print('-'*80)
print('| 0: OASSIS (12)| 1: o (12)|')
print('|rrbbbgggwwwwyyy|rrbbb     |')
#print('|r:10 g:22 b:23 |')
#print('|   y:32 w:43   |')
print('|ttttttttppp ( )|t      ( )|')
print('-'*80)

print('\n')
find_moves(init_board(test_board, test_meeples), num_rows, num_cols)

#b = generate_random_board(randint(0,10000))
#b = generate_random_board(6715)
board, n_rows, n_cols = generate_random_board(3492)
find_moves(board, n_rows, n_cols)
pretty_print_board2(board, n_rows, n_cols)
