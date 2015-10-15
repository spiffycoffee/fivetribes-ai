
# Boards are represented by a string of tiles, separated with commas

# Tiles definitions have 2 components, always in the following order:
# 1) The Value - a 1 or 2 digit number from 3 to 12
# 2) The Type  - 1 of the 5 corresponding characters defined below:
VILLAGE       = 'v'  # (Palace tile,    Blue)  
OASSIS        = 'o'  # (Palm tree tile, Red)
SACRED_PLACE  = 's'  # (Djinn tile,     Blue)
HALF_MARKET   = 'h'  # (3 coin market,  Red)
FULL_MARKET   = 'f'  # (6 coin market,  Red)
# ** Each tile type is always Red/Blue, so we do not need to declare color separately
test_board = "3v,5o,6s,2h,11f,3s,13o,5h,7f,12s,7o,8h"
# TODO include palm trees, palaces, camels

# Meeples are represented with the below characters
RED    = 'r'  # Assassins
BLUE   = 'b'  # Builders
GREEN  = 'g'  # Merchants
WHITE  = 'w'  # Elders
YELLOW = 'y'  # Viziers
# Declare meeple positions and counts with another comma separated string. 
# Use multiple letters for multiple meeples 
test_meeples = "r,g,b,y,w,rgb,yw,rr,rrb,rrbb,rgbyw,rrggbbyyww"

# or take as input diagram?
# -------------------------
# | rrgby   |
# | 12o-ctp |

num_cols = 3
num_rows = 4

def init_board(s):
	print s 
	temp = []
	board = []

	# TODO convert to list comprehension?
	# TODO filter out whitespace? make whitespace the deliminator?
	for tile in s.split(','):
		# TODO make this a dict?
		temp.append([int(tile[:-1]), tile[-1], 0, 0, '']) # store tile value and type to tuple, 
														 # initialize palm trees, palaces, camels to zero
	for i in range(num_rows):
		row_index = num_cols * i
		board.append(temp[row_index:row_index + num_cols])
	
	print board

# for each tile
# find all tiles that can be moved to 
#	of those, which are valid (meeple match)	
#	of those, compute score
#	highest scoring? save all possible scores?
def calc_meeple_score(meeple, tile, meeple_tile):
	if meeple not in meeple_tile:
		return 0

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
			return 20
	elif meeple == WHITE:
			return score_elder()
	elif meeple == YELLOW:
			# Each vizier is worth 1 point	
			# TODO 10pts for everyone with less viziers?
			return tile.count(meeple) + 1
	return 0

def score_elder(tile):
	return ((tile.count(WHITE) + 1) * 2   # Each elder is worth 2 points
		     + camel_points(WHITE, tile) 
		     + calc_tile_score(tile))

# If tile only contains passed in meeple type, put a camel on the tile and return its score
def camel_points(meeple, tile, meeple_tile):
	if meeple_tile.replace(meeple, '') == '':
		tile[4] = '+'
		return tile[0] # tile score
	return 0

def calc_tile_score(tile):
	return 0
	

#TODO represent meeples, other board state - type of tile, palms & palaces, camels
#	  represent hand? merchent deck? djinn deck?
#	  from a given tile, determine moves, valid moves, scoring
#	  conversely, what are tiles with most potential points (even if not accessible right now)


init_board(test_board)
test_tile = [9,VILLAGE,0,0,'']
test_meeple_tile = 'rrr'
print test_tile
print camel_points(RED, test_tile, test_meeple_tile)
print test_tile
