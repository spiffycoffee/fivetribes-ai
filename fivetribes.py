from __future__ import print_function
from random import randint, seed
from itertools import izip

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

def find_moves(board, n_rows, n_cols):
    result = []
    tot_route_count = 0
    tot_move_count = 0
    for i, tile in enumerate(board):
        #if i == 4 : # TODO temp
            print("tile %d:" % i) 
            routes = gen_routes(num_meeples(tile), '', i, [], (board, n_rows, n_cols))
            move_count = 0
            for move in gen_moves(routes, tile, board):
                # TODO acutally do something with moves
                move_count += 1
                meeple = move[-1][1]
                end_idx = move[-1][0]
                score = calc_score(meeple, end_idx, (board, n_rows, n_cols))
                if move_count % 100000 == 1:
                    print(list(move))
                    print("score: %d, tile: %s, %s " % (score, end_idx, meeple))

            print("Routes found: %d" % (len(routes)))
            print("Moves found: %d" % (move_count))
            tot_move_count += move_count
            tot_route_count += len(routes)
    print("Total Routes found: %d" % (tot_route_count))
    print("Total Moves found: %d" % (tot_move_count))

def gen_moves(routes, start_tile, board):
    #TODO {key: [] for key in MEEPLES}
    cache = {'r':[], 'g':[], 'b':[], 'y':[], 'w':[]}
    for route in routes: 
        if route:
            #print("Trying route: %s" % route) 
            a = start_tile['meeples']
            b = board[route[-1]]['meeples']
            for meeple in matching_meeples(a, b):
                # generate meeple permutations for route
                #print("End meeple: %s" % meeple) 
                for p in permute_meeples_over_route(route, a, meeple, cache):
                    yield p
                #permute_meeples_over_route(route, start_tile['meeples'], meeple, cache))

def matching_meeples(a, b):
    return list(set(a) & set(b))

def permute_meeples_over_route(route, meeples, end_meeple, cache):
    if cache[end_meeple]:
        #return [izip(route, p + [end_meeple]) for p in cache[end_meeple]]
        for p in cache[end_meeple]:
            #yield izip(route, p + [end_meeple])
            yield zip(route, p + [end_meeple])
    else: 
        meeples = copy_and_remove(meeples, end_meeple)
        permutations = permute_meeples(meeples, [], len(meeples))
        cache[end_meeple] = permutations 
        print("Permuting %s, length %s" % (end_meeple, len(permutations)))
        #return [izip(route, p + [end_meeple]) for p in permutations]
        for p in permutations:
            #yield izip(route, p + [end_meeple])
            yield zip(route, p + [end_meeple])

def permute_meeples(remainder, result, n):
    if not remainder or n == 0:
        #print("done: %s" % remainder)
        return [result]
    else:
        total = []
        for r in set(remainder):
            #print("remainder: %s" % remainder)
            copy_remainder = copy_and_remove(remainder, r)
            total += permute_meeples(copy_remainder, result + [r], n-1)
        return total

# returns a shallow copy of a list with the given item removed
def copy_and_remove(a_list, item):
    copy_list = list(a_list)
    copy_list.remove(item)
    return copy_list

# returns number of meeples on a given tile
def num_meeples(tile):
    return len(tile['meeples'])

def gen_routes(n, prev_dir, curr_idx, route, board_info):
    if n <= 0:
        return [route]

    n_rows = board_info[1]
    n_cols = board_info[2]
    result = []
    # if not top row
    if curr_idx >= n_cols and prev_dir != 'S' :                 
        next_idx = curr_idx - n_cols
        # move up 
        result += gen_routes(n-1, 'N', next_idx, route + [next_idx], board_info)  
    # if not right column
    if curr_idx % n_cols < n_cols-1 and prev_dir != 'W':
        next_idx = curr_idx + 1
        # move right 
        result += gen_routes(n-1, 'E', next_idx, route + [next_idx], board_info)  
    # if not bottom row
    if curr_idx < (n_rows-1) * n_cols and prev_dir != 'N':      
        next_idx = curr_idx + n_cols
        # move down 
        result += gen_routes(n-1, 'S', next_idx, route + [next_idx], board_info)  
    # if not left column
    if curr_idx % n_cols != 0 and prev_dir != 'E': 
        next_idx = curr_idx - 1
        # move left 
        result += gen_routes(n-1, 'W', next_idx, route + [next_idx], board_info)  
    return result

# find all tiles that can be moved to 
#   of those, which are valid (meeple match)    
#   of those, compute score
#   highest scoring? save all possible scores?

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
        #           kiling vizier knocks their count below yours?
        #           elders?
        return 10
    elif meeple == GREEN:
        # Merchant - what's up for grabs? (not full amount grab-able...)
        #            what's in your hand?
        #            how far along are you in your sets,etc
        return 5 * (tile['meeples'].count(GREEN) + 1)
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
    tile_width = 11     # min of 10 or alignment breaks
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

def generate_random_board(s, n_rows, n_cols):
    seed(s)
    print("Generating random board with seed %s" % s)

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
    return board



if __name__ == '__main__':
    #TODO 
    #from a given tile, determine moves, valid moves, scoring
    #handle looping moves, handle moves that go back to starting tile properly
    #represent hand? merchent deck? djinn deck?
    #conversely, what are tiles with most potential points (even if not accessible right now)


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

    n_rows = 6
    n_cols = 5
        
    import time
    start_time = time.time()
    #b = generate_random_board(6715)
    #board = generate_random_board(randint(0,10000), n_rows, n_cols)
    #board = generate_random_board(3492, n_rows, n_cols)
    #board = generate_random_board(47, n_rows, n_cols) # 3 million!
    board = generate_random_board(6557, n_rows, n_cols) # 10 million :O
    #find_moves(board, n_rows, n_cols)
    print("Run time: %s" % (time.time() - start_time))
    pretty_print_board2(board, n_rows, n_cols)

    import cProfile
    cProfile.run('find_moves(board, n_rows, n_cols)')

    # Test scaffolding
    a = [1,2,3,4]
    b = ['a','b','c','d']
    start_time = time.time()
    #for i in range(10000000):
    #    zip(a, b)
    #print("Run time: %s" % (time.time() - start_time))
