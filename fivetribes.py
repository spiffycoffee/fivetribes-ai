from __future__ import print_function
from random import randint, seed, shuffle
from sys import maxint

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

    #board = []
    #n_rows = 0
    #n_cols = 0
    #merchant_deck = []
    #djinn_deck = []
    #player_hands = []

# decorator to count function calls, slow :(
def count(func):
    def count_closure(*args, **kwargs):
        count_closure.count += 1
        return func(*args, **kwargs)
    count_closure.count = 0
    return count_closure

class TableTop(object):
    def __init__(self, **kwargs):
        self.board = kwargs.get('board', [])
        self.n_cols = kwargs.get('n_cols', 1)
        self.n_rows = len(self.board) / self.n_cols
        self.merchant_deck = kwargs.get('merchant_deck', [])
        self.djinn_deck = kwargs.get('djinn_deck', [])
        self.player_hands = kwargs.get('player_hands', [])


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

def gen_moves(board_info):
    tot_route_count = 0
    tot_move_count = 0
    board = board_info[0]
    for idx in xrange(len(board)):
        #TODO {key: [] for key in MEEPLES}
        cache = {'r':[], 'g':[], 'b':[], 'y':[], 'w':[]}
        route_count = 0
        for route in gen_routes(idx, board_info):
            #print("Trying route: %s" % route) 
            route_count += 1
            move_count = 0
            for move in permute_meeples_over_route(route, board, cache):
                #print("move %s" % move)
                move_count += 1
                yield move
    
            tot_move_count += move_count
        tot_route_count += route_count
    print("Total Routes found: %d" % (tot_route_count))
    print("Total Moves found: %d" % (tot_move_count))

def valid_end_meeples(route, board):
    start_idx = route[0]
    end_idx = route[-1]
    if start_idx == end_idx:
        return [] # route stopping on starting tile confuses meeple matcher
    
    starting_meeples = board[start_idx]['meeples']
    ending_meeples = board[end_idx]['meeples']
    return list(set(starting_meeples) & set(ending_meeples))

def gen_routes(idx, board_info):
    n_meeples = num_meeples(board_info[0][idx])
    if n_meeples == 0:
        return [] # tiles with no meeples have no routes
    else:
        return _gen_routes(n_meeples, '', idx, [idx], board_info)

def _gen_routes(n, prev_dir, curr_idx, route, board_info):
    if n <= 0:
        # FIXME hack to prevent a route from starting and stopping on same tile 
        return [route] if route[-1] != route[0] else [] 
        #return [route] 
    
    n_rows = board_info[1]
    n_cols = board_info[2]
    result = []
    # if not top row
    if curr_idx >= n_cols and prev_dir != 'S' :                 
        next_idx = curr_idx - n_cols
        # move up 
        result += _gen_routes(n-1, 'N', next_idx, route+[next_idx], board_info)  
    # if not right column
    if curr_idx % n_cols < n_cols-1 and prev_dir != 'W':
        next_idx = curr_idx + 1
        # move right 
        result += _gen_routes(n-1, 'E', next_idx, route+[next_idx], board_info)  
    # if not bottom row
    if curr_idx < (n_rows-1) * n_cols and prev_dir != 'N':      
        next_idx = curr_idx + n_cols
        # move down 
        result += _gen_routes(n-1, 'S', next_idx, route+[next_idx], board_info)  
    # if not left column
    if curr_idx % n_cols != 0 and prev_dir != 'E': 
        next_idx = curr_idx - 1
        # move left 
        result += _gen_routes(n-1, 'W', next_idx, route+[next_idx], board_info)  
    return result

def permute_meeples_over_route(route, board, cache):
    starting_meeples = board[route[0]]['meeples']
    #print("starting_meeples %s" % starting_meeples)
    for end_meeple in valid_end_meeples(route, board):
        if not cache[end_meeple]:
            meeples = copy_and_remove(starting_meeples, end_meeple)
            permutations = permute_meeples(meeples, [], len(meeples))
            cache[end_meeple] = permutations 
            #print("Permuting %s, length %s" % (end_meeple, len(permutations)))

        for p in cache[end_meeple]:
            yield zip(route, [''] + p + [end_meeple])

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
    copy_list = a_list[:]
    copy_list.remove(item)
    return copy_list

# returns number of meeples on a given tile
def num_meeples(tile):
    return len(tile['meeples'])

# find all tiles that can be moved to 
#   of those, which are valid (meeple match)    
#   of those, compute score
#   highest scoring? save all possible scores?

# calculate the score of matching a number of meeples on a tile
def calc_score(meeple, meeple_count, idx, board_info):
    tile = board_info[0][idx]
    return meeple_score(meeple, meeple_count, idx, board_info) \
            + tile_score(tile) \
            + camel_score(meeple, tile)

#def meeple_score(meeple, tile, idx, board_info):
def meeple_score(meeple, meeple_count, idx, board_info):
    #meeple_count = end_tile_match(meeple, tile['meeples'])

    # TODO fakirs?
    if meeple == RED:
        # Assasin - murder-able tile in range?
        #           kiling vizier knocks their count below yours?
        #           elders?
        return score_assassins(idx, board_info)
    elif meeple == GREEN:
        # Merchant - what's up for grabs? (not full amount grab-able...)
        #            what's in your hand?
        #            how far along are you in your sets,etc
        return 5 * meeple_count
    elif meeple == BLUE:
        # Builder - number of blue tiles around this one?
        return score_builders(meeple_count, idx, board_info) 
    elif meeple == WHITE:
        return 2 * meeple_count    # Each elder is worth 2 points
    elif meeple == YELLOW:
        # TODO 10pts for everyone with less viziers?
        return meeple_count     # Each vizier is worth 1 point 
    else:
        raise ValueError('Not a valid meeple type: %s' % meeple) 

def score_assassins(idx, board_info):
    #TODO 
    return 10

def score_builders(meeple_count, curr_idx, board_info):
    # TODO need whole board to find surrounding tiles?
    return meeple_count * 4 

def tile_score(tile):
    tile_type = tile['type']
    if (tile_type) == OASSIS:
        tile['trees'] += 1 
        return 3 if tile['camel'] == MY_CAMEL else 0
    elif (tile_type) == VILLAGE:
        tile['palaces'] += 1 
        return 5 if tile['camel'] == MY_CAMEL else 0
    elif (tile_type) == SACRED_PLACE:
        # TODO return highest value djinn?
        return 8 
    elif (tile_type) == HALF_MARKET:
        # TODO return market calculation, enough coins to buy?
        return 5
    elif (tile_type) == FULL_MARKET:
        # TODO return market calculation, enough coins to buy?
        return 10
    else:
        raise ValueError('Not a valid tile type: %s' % tile_type) 

# returns true if all meeples on tile match passed in meeple 
# TODO remove 
def tile_cleared(meeple, tile):
    for m in tile['meeples']:
        if m != meeple:
            return False
    return True

# Check if a camel can be placed and compute the score for doing so
def camel_score(meeple, tile):
    if tile['camel'] == NO_CAMEL and tile_cleared(meeple, tile):
        tile['camel'] = MY_CAMEL
        #raw_input()
        return tile['value'] + 3 * tile['trees'] + 5 * tile['palaces'] 
    else:
        return 0

def minimax(depth, board_info):
    if depth == 0:
        # TODO do we need static evaluator? how should we scale its value
        return 0, []

    board = board_info[0]
    best_move = []
    max_score = -maxint - 1  # negative infinity
    for move in gen_moves(board_info):
        #print("move %s: " % move)
        #pretty_print_board2(*board_info)
        starting_meeples = board[move[0][0]]['meeples']
        copied_end_tile = copy_tile(board[move[-1][0]])
        meeple_count = make_move(move, board)
        #pretty_print_board2(*board_info)

        score = calc_score(move[-1][1], meeple_count, move[-1][0], board_info)\
                - minimax(depth - 1, board_info)[0]

        #pretty_print_board2(*board_info)
        unmake_move(move, board, starting_meeples, copied_end_tile)
        #pretty_print_board2(*board_info)
        #raw_input()

        if (score > max_score):
            #print("better score: %s" % score)
            max_score = score
            best_move = move
    return max_score, best_move

def alphabeta(depth, board_info, net_score, alpha, beta, max_node):
    if depth == 0:
        # TODO do we need static evaluator? how should we scale its value
        return net_score, []

    board = board_info[0]
    best_move = []
    if max_node:
        v = -maxint - 1  # negative infinity
        for move in gen_moves(board_info):
            #print("max move %s: " % move)
            starting_meeples = board[move[0][0]]['meeples']
            copied_end_tile = copy_tile(board[move[-1][0]])
            meeple_count = make_move(move, board)

            score = net_score + calc_score(move[-1][1], meeple_count, move[-1][0], board_info) 
            #print("scored: %s" % score)
            value = alphabeta(depth - 1, board_info, score, alpha, beta, False)[0]
            #print("after alphabeta: %s" % score)

            unmake_move(move, board, starting_meeples, copied_end_tile)

            #v = max(v, value)
            if value > v:
                v = value
                best_move = move
                #print("new max: %d, %s" % (v, best_move))
            alpha = max(alpha, v)
            if beta <= alpha:
                #print("beta cut-off")
                break 
                #return -beta, best_move
        return v, best_move
    else:
        v = maxint # positive infinity
        for move in gen_moves(board_info):
            #print("min move %s: " % move)
            starting_meeples = board[move[0][0]]['meeples']
            copied_end_tile = copy_tile(board[move[-1][0]])
            meeple_count = make_move(move, board)

            score = net_score - calc_score(move[-1][1], meeple_count, move[-1][0], board_info) 
            #print("scored: %s" % score)
            value = alphabeta(depth - 1, board_info, score, alpha, beta, True)[0]
            #print("after alphabeta: %s" % score)

            unmake_move(move, board, starting_meeples, copied_end_tile)

            #v = min(v, value)
            if value < v:
                v = value
                best_move = move
                #print("new min: %d, %s" % (v, best_move))
            beta = min(beta, v)
            if alpha >= beta:
                #print("alpha: %d, beta: %d" % (alpha, beta))
                #raw_input()
                #print("alpha cut-off")
                break
                #return -alpha, best_move 
        return v, best_move

def copy_tile(tile):
    # deep copying manually because deepcopy() was slow
    # only the meeples array needs to be deep copied, the rest is primitives 
    saved_tile = tile.copy() 
    saved_tile['meeples'] = tile['meeples'][:] 
    return saved_tile

#def end_tile_match(meeple, tile_meeples):
#    initial_count = len(tile_meeples)
#    filter_matches = [m for m in tile_meeples if m != meeple]
#    tile_meeples = filter_matches
#    return initial_count - len(filter_matches)

def make_move(move, board):
    board[move[0][0]]['meeples'] = []

    for idx, meeple in move[1:-1]:
        board[idx]['meeples'] += meeple

    idx, meeple = move[-1]
    count = 1 # move adds a meeple
    while True:
        try:
            board[idx]['meeples'].remove(meeple)
            count += 1
        except ValueError:
            #print("count: %s" % count)
            return count

def unmake_move(move, board, starting_meeples, end_tile):
    for idx, meeple in move[1:-1]:
        try:
            board[idx]['meeples'].remove(meeple)
        except ValueError:
            #print(move)
            #pretty_print_board2(*board_info)
            #raw_input("meeple gone") 
            pass    # if meeple was already removed (e.g. by assassin or loop) do nothing

    board[move[0][0]]['meeples'] = starting_meeples
    board[move[-1][0]] = end_tile

def pretty_print_board2(board, n_rows, n_cols):
    tile_width = 11     # min of 10, below that alignment will break
    width = n_cols * tile_width + 1
    n = 0

    print('-' * width)
    for r in range(n_rows):
        row_tiles = board[r*n_cols:(r+1)*n_cols]

        # print tile header row
        print('|', end='')
        for tile in row_tiles:
            value = '('+repr(tile['value'])+')'
            print('{:2}: {}{:>{}s}'.format(n, tile['type'], value, tile_width-6), end='|')
            n += 1
        
        # print meeples row
        print('\n', end='|')
        for tile in row_tiles:
            meeples = ''.join(tile['meeples'])
            print('{:^{}s}'.format(meeples, tile_width-1), end='|')

        # print tree/palace/camel row
        print('\n', end='|')
        for tile in row_tiles:
            camel = '('+tile['camel']+')'
            tree_palaces = 't'*tile['trees'] + 'p'*tile['palaces']
            print('{:^{}s}{:>3}'.format(tree_palaces, tile_width-4, camel), end='|')

        print('\n' + '-' * width)

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

    return board

def generate_starting_board(s, n_rows, n_cols):
    seed(s)
    print("Generating starting board with seed %s" % s)

    tile_type = [VILLAGE, OASSIS, SACRED_PLACE, HALF_MARKET, FULL_MARKET]
    bag_of_meeples = list((RED + BLUE + GREEN) * 18 + WHITE * 20 + YELLOW * 16)
    shuffle(bag_of_meeples)

    board = [] 
    for i in range(n_cols * n_rows):
        board.append({'meeples' : [],
                        'value': randint(3,12), 
                        'type' : tile_type[randint(0,4)], 
                        'trees': 0, 
                        'palaces' : 0, 
                        'camel': NO_CAMEL
                        }) 
        for _ in range(3):
            board[i]['meeples'] += bag_of_meeples.pop()

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

    n_cols = 5
    n_rows = 6
        
    import time
    start_time = time.time()
    #b = generate_random_board(6715)
    #board = generate_starting_board(randint(0,10000), n_rows, n_cols)
    board = generate_starting_board(1100, n_rows, n_cols)
    #board = generate_random_board(randint(0,10000), n_rows, n_cols)
    #board = generate_random_board(3492, n_rows, n_cols)
    #board = generate_random_board(6845, n_rows, n_cols) # 1 million
    #board = generate_random_board(47, n_rows, n_cols) # 3 million!
    #board = generate_random_board(6557, n_rows, n_cols) # 10 million :O
    #gen_moves(board, n_rows, n_cols)
    tt = TableTop(board=board, n_cols=n_cols)
    board_info = (tt.board, tt.n_rows, tt.n_cols)
    #board_info = (board, n_rows, n_cols)
    pretty_print_board2(*board_info)
    print("Run time: %s" % (time.time() - start_time))


    import cProfile
    #cProfile.run('gen_moves((board, n_rows, n_cols))')
    ply = 3
    #cProfile.run('print("best score: %d, %s" % minimax(ply, board_info))')
    cProfile.run('print("best score: %d, %s" % alphabeta(ply, board_info, 0, -maxint, maxint, True))')

    pretty_print_board2(*board_info)

    # Test scaffolding
    ##print("Run time: %s" % (time.time() - start_time))   if depth == 0:
