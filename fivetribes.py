
test_board = "3r,5r,6b,2r,11r,3b,13r,5r,7r,12b,7r,8r"
num_cols = 3
num_rows = 4

def init_board(s):
	print s 
	temp = []
	board = []

	# TODO convert to list comprehension?
	for tile in s.split(','):
		temp.append((int(tile[:-1]), tile[-1])) # store tile value and color as tuple
	
	for i in range(num_rows):
		row_index = num_cols * i
		board.append(temp[row_index:row_index + num_cols])
	
	print board


#TODO represent meeples, other board state - type of tile, palms & palaces, camels
#	  represent hand? merchent deck? djinn deck?
#	  from a given tile, determine moves, valid moves, scoring
#	  conversely, what are tiles with most potential points (even if not accessible right now)


init_board(test_board)
