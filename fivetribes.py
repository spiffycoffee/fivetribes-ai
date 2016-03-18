from __future__ import print_function
from random import randint, seed, shuffle
from sys import maxint
import cPickle

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

# Merchant Deck
FAKIR   = 0
IVORY   = 1
JEWELS  = 2
GOLD    = 3
PAPYRUS = 4
SILK    = 5
SPICE   = 6
FISH    = 7
WHEAT   = 8
POTTERY = 9 

# Lookup array for scoring Merchant Sets
#   index represents the set length
#   e.g. 2 card set = 3 pts, 3 card set = 7 pts, etc.
score_merchant_set = [0, 1, 3, 7, 13, 21, 30, 40, 50, 60]

    #board = []
    #n_rows = 0
    #n_cols = 0
    #merchant_deck = []
    #djinn_deck = []
    #player = []

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
        self.player = kwargs.get('player', [])

    # TODO remove
    def __deepcopy__(self):
        copy = TableTop()
        copy.board = list(self.board)
        for i in xrange(len(self.board)):
            copy.board[i] = dict(self.board[i])
            copy.board[i]['meeples'] = list(self.board[i]['meeples'])
        copy.n_cols = self.n_cols
        copy.n_rows = self.n_rows
        copy.merchant_deck = list(self.merchant_deck)
        copy.djinn_deck = list(self.djinn_deck)
        return copy

    # TODO remove
    def save_state(self, move_start, move_end):
        #copy = TableTop(board=TableTop.board)
        copy = TableTop()
        copy.board = self.board  # direct reference 
        copy.n_cols = self.n_cols
        copy.n_rows = self.n_rows
        copy.merchant_deck = list(self.merchant_deck)
        copy.djinn_deck = list(self.djinn_deck)

        starting_meeples = self.board[move_start]['meeples']
        copied_end_tile = copy_tile(self.board[move_end])
        return (copy, starting_meeples, copied_end_tile)

    # TODO remove
    def load_state(self, state):
        self.merchant_deck = state.merchant_deck
        self.djinn_deck = state.djinn_deck

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        #TODO make this return strings
        pretty_print_board2(self.board, self.n_rows, self.n_cols)
        print("merchant %s" % self.merchant_deck)
        print("djinn %s" % self.djinn_deck)
        print("player %s" % self.player)
        return ''

    def board_info(self):
        return (self.board, self.n_rows, self.n_cols)

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

# calculate the score of matching a number of meeples on a tile
def calc_score(last_step, meeple_count, undo_stack, tt):
    idx, meeple = last_step
    tile = tt.board[idx]
    return meeple_score(meeple, meeple_count, idx, undo_stack, tt) \
            + tile_score(tile, undo_stack, tt) \
            + camel_score(meeple, tile, undo_stack)

def meeple_score(meeple, meeple_count, idx, undo_stack, tt):
    #meeple_count = end_tile_match(meeple, tile['meeples'])
    #print(meeple, tt.board[idx])
    #raw_input()
    
    # TODO fakirs?
    if meeple == RED:
        # Assasin - murder-able tile in range?
        #           kiling vizier knocks their count below yours?
        #           elders?
        return score_assassins(meeple_count, idx, undo_stack, tt)
    elif meeple == GREEN:
        # Merchant - what's up for grabs? (not full amount grab-able...)
        # TODO undo merchant deck changes, player hand / fakirs
        #return 5 * meeple_count

        undo_stack.append((0, tt, 'merchant_deck', tt.merchant_deck[:]))
        score = 0
        for _ in xrange(meeple_count):
            card = tt.merchant_deck.pop()
            score += score_merchants(card, tt.player[1], undo_stack) # TODO actual player
        return score
    elif meeple == BLUE:
        return score_builders(meeple_count, idx, tt) 
    elif meeple == WHITE:
        return 2 * meeple_count    # Each elder is worth 2 points
    elif meeple == YELLOW:
        # TODO 10pts for everyone with less viziers?
        return meeple_count     # Each vizier is worth 1 point 
    else:
        raise ValueError('Not a valid meeple type: %s' % meeple) 

def score_assassins(meeple_count, idx, undo_stack, tt):
    max_score = 0
    for tile in tt.board:
        if len(tile['meeples']) == 1 and tile['camel'] == '':
            undo_stack.append((0, tile, 'meeples', tile['meeples']))
            undo_stack.append((0, tile, 'camel', ''))
            tile['meeples'] = [] 
            tile['camel'] = MY_CAMEL
            #print(tt)
            #raw_input('assasinating: %s' % tile)
            return tile['value']
    
    # TODO only assasinate in range, pick best scoring, assassinate viziers?
            # if tile in assasin range
            if tile['value'] > max_score:
                max_score = tile['value']
                # do assasination, how to undo?
    return max_score 

def score_merchants(card, player, undo_stack):
    # TODO test undo moves
    if card == 0:  # fakir
        undo_stack.append((0, player, 'fakirs', player['fakirs']))
        player['fakirs'] += 1
        return 0

    player_sets = player['merchant_sets']
    for i, set_ in enumerate(player_sets):
        if card not in set_:
            undo_stack.append((0, player_sets, i, set(set_)))
            set_.add(card)
            return score_merchant_set[len(set_)]

    # no existing sets / card already in all existing sets
    undo_stack.append((1, player, 'merchant_sets'))
    player_sets.append(set([card]))
    return 1

def set_size(card, merchant_sets):
    """ returns the size of the largest set that doesn't contain the card """
    if card == 0:  # fakir
        return 0

    for set_ in merchant_sets:
        if card not in set_:
            return len(set_)
    return 0 
    

def score_builders(meeple_count, idx, tt):
    # TODO precompute surrounding blue tiles for whole board
    surrounding_blues = blue_tiles(idx, tt)
    return meeple_count * surrounding_blues 

def blue_tiles(i, tt):
    def is_blue_tile(tile):
        return tile['type'] == VILLAGE or tile['type'] == SACRED_PLACE
    
    left       = i - 1
    center     = i
    right      = i + 1
    top        = -n_cols
    bot        = n_cols
    on_left    = center % n_cols == 0
    on_right   = right % n_cols == 0
    on_top_row = center+top < 0
    on_bot_row = center+bot >= len(tt.board)
    
    blues = 0
    # check a given tile and its 8 neighbors (less if on an edge) 
    if not on_top_row:
        if not on_left and is_blue_tile(tt.board[top+left]):
            blues += 1
        if is_blue_tile(tt.board[top+center]):
            blues += 1
        if not on_right and is_blue_tile(tt.board[top+right]):
            blues += 1
    if not on_left and is_blue_tile(tt.board[left]):
        blues += 1
    if is_blue_tile(tt.board[center]):
        blues += 1
    if not on_right and is_blue_tile(tt.board[right]):
        blues += 1
    if not on_bot_row:
        if not on_left and is_blue_tile(tt.board[bot+left]):
            blues += 1
        if is_blue_tile(tt.board[bot+center]):
            blues += 1
        if not on_right and is_blue_tile(tt.board[bot+right]):
            blues += 1
    return blues

def tile_score(tile, undo_stack, tt):
    tile_type = tile['type']
    if tile_type == OASSIS:
        undo_stack.append((0, tile, 'trees', tile['trees']))
        tile['trees'] += 1 
        return 3 if tile['camel'] == MY_CAMEL else 0

    elif tile_type == VILLAGE:
        undo_stack.append((0, tile, 'palaces', tile['palaces']))
        tile['palaces'] += 1 
        return 5 if tile['camel'] == MY_CAMEL else 0

    elif tile_type == SACRED_PLACE:
        return score_sacred_place(undo_stack, tt)
        #return max(tt.djinn_deck[-3:])
        #return 8 

    elif tile_type == HALF_MARKET:
        # TODO return market calculation, enough coins to buy?
        #return 5
        #return 1

        player_hand = tt.player[1]
        half_market = tt.merchant_deck[-3:]
        _, idx = best_cards(half_market, player_hand['merchant_sets'])[0]
        undo_stack.append((0, tt, 'merchant_deck', tt.merchant_deck[:]))
        card = tt.merchant_deck.pop(idx-3)
        return score_merchants(card, player_hand, undo_stack)

#        best_card = None
#        best_set = 0
#        for card in tt.merchant_deck[-3:]:
#            s = set_size(card, tt.player[1]['merchant_sets']) # TODO actual player
#            if s > best_set: 
#                best_card = card
#                best_set = s
#        return score_merchants(best_card, tt.player[1], undo_stack) 

    elif tile_type == FULL_MARKET:
        # TODO return market calculation, enough coins to buy?
        #return 10
        #return 2

        player_hand = tt.player[1]
        full_market = tt.merchant_deck[-6:]

        top_2_cards = best_cards(full_market, player_hand['merchant_sets'])[:2]
        # if necessary, rearrange results so popping won't make the indexes invalid
        if top_2_cards[0][1] > top_2_cards[1][1]:
            top_2_cards[0], top_2_cards[1] = top_2_cards[1], top_2_cards[0]

        undo_stack.append((0, tt, 'merchant_deck', tt.merchant_deck[:]))
        score = 0
        for _, idx in top_2_cards:
            #print(tt.merchant_deck)
            card = tt.merchant_deck.pop(idx-6)
            score += score_merchants(card, player_hand, undo_stack)
        return score

    else:
        raise ValueError('Not a valid tile type: %s' % tile_type) 

def best_cards(merchant_cards, player_sets):
    score = [(set_size(merchant_cards[i], player_sets), i) for i in xrange(len(merchant_cards))]
    score.sort(reverse=True) 
    return score
#    return sorted(score, reverse=True)
    #return [score[i][1] for i in xrange(n)] # return index of top n cards

def score_sacred_place(undo_stack, tt):
    # TODO player has enough elders / fakirs
    idx = len(tt.djinn_deck)-1 # index of end of list
    best_score = 0
    for i in xrange(idx, idx-3, -1):  # first 3 cards on the deck
        if tt.djinn_deck[i] > best_score:
            best_score = tt.djinn_deck[i]
            idx = i
    
    # TODO re-insert popped card instead of replacing whole thing?
    undo_stack.append((0, tt, 'djinn_deck', tt['djinn_deck'][:]))
    tt.djinn_deck.pop(idx)
    return best_score

# returns true if all meeples on tile match passed in meeple 
# TODO remove 
def tile_cleared(meeple, tile):
    for m in tile['meeples']:
        if m != meeple:
            return False
    return True

# Check if a camel can be placed and compute the score for doing so
def camel_score(meeple, tile, undo_stack):
    #if tile['camel'] == NO_CAMEL and tile_cleared(meeple, tile):
    if tile['camel'] == NO_CAMEL and not tile['meeples']:
        undo_stack.append((0, tile, 'camel', ''))
        tile['camel'] = MY_CAMEL
        #raw_input(tile)
        return tile['value'] + 3 * tile['trees'] + 5 * tile['palaces'] 
    else:
        return 0

def minimax(depth, tt):
    if depth == 0:
        # TODO do we need static evaluator? how should we scale its value
        return 0, []

    best_move = []
    max_score = -maxint - 1  # negative infinity
    for move in gen_moves(tt.board_info()):
        #board = board_info[0]
        undo_stack = []
        debug = True
        debug = False
        if(debug):
            print("move %s: " % move)
            print(tt)

        #starting_meeples = tt.board[move[0][0]]['meeples']
        #copied_end_tile = copy_tile(tt.board[move[-1][0]])
        #save_state = tt.fast_copy()
        #save_state = tt.save_state(move[0][0], move[-1][0])
        meeple_count = make_move(move, tt.board, undo_stack) 
        #tt.merchant_deck.pop()
        if(debug):
            print(tt)

        last_step = move[-1]
        score = calc_score(last_step, meeple_count, undo_stack, tt)\
                - minimax(depth - 1, tt)[0]

        #print(tt)
        #unmake_move(move, tt.board, starting_meeples, copied_end_tile)

        #unmake_move(move, *save_state) 
        #tt.load_state(save_state[0])
        unmake(undo_stack)

        #tt = save_state
        if(debug):
            print(tt)
            #print(ending_meeples)
            raw_input()

        if (score > max_score):
            print("better score: %s" % score)
            #print(move)
            #print(tt)
            max_score = score
            best_move = move
    return max_score, best_move

def alphabeta(depth, tt, net_score, alpha, beta, max_node):
    if depth == 0:
        # TODO do we need static evaluator? how should we scale its value
        return net_score, []

    board_info = tt.board_info()
    board = board_info[0]
    best_move = []
    undo_stack = []
    if max_node:
        v = -maxint - 1  # negative infinity
        for move in gen_moves(board_info):
            #print("max move %s: " % move)
            #starting_meeples = board[move[0][0]]['meeples']
            #copied_end_tile = copy_tile(board[move[-1][0]])
            #save_state = tt.save_state(move[0][0], move[-1][0])
            meeple_count = make_move(move, tt.board, undo_stack) 

            last_step = move[-1]
            score = net_score + calc_score(last_step, meeple_count, undo_stack, tt) 
            #print("scored: %s" % score)
            value = alphabeta(depth - 1, tt, score, alpha, beta, False)[0]
            #print("after alphabeta: %s" % score)

            #unmake_move(move, *save_state) 
            #tt.load_state(save_state[0])
            unmake(undo_stack)

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
            #starting_meeples = board[move[0][0]]['meeples']
            #copied_end_tile = copy_tile(board[move[-1][0]])
            #save_state = tt.save_state(move[0][0], move[-1][0])
            meeple_count = make_move(move, tt.board, undo_stack) 

            last_step = move[-1]
            score = net_score - calc_score(last_step, meeple_count, undo_stack, tt) 
            #print("scored: %s" % score)
            value = alphabeta(depth - 1, tt, score, alpha, beta, True)[0]
            #print("after alphabeta: %s" % score)

            #unmake_move(move, *save_state) 
            #tt.load_state(save_state[0])
            unmake(undo_stack)

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
    #saved_tile = tile.copy() 
    saved_tile = dict(tile)
    saved_tile['meeples'] = tile['meeples'][:] 
    return saved_tile

def make_move(move, board, undo_stack):
    # start
    start_tile = board[move[0][0]]
    undo_stack.append((0, start_tile, 'meeples', start_tile['meeples']))
    start_tile['meeples'] = []

    for idx, meeple in move[1:-1]:
        # middles
        undo_stack.append((1, board[idx], 'meeples'))
        board[idx]['meeples'] += meeple

    # end, copy original, reference to existing
    end_tile = board[move[-1][0]]
    undo_stack.append((0, end_tile, 'meeples', end_tile['meeples'][:]))
    idx, meeple = move[-1]
    count = 1 # move adds a meeple
    while True:
        try:
            board[idx]['meeples'].remove(meeple)
            #undo_stack.append((2, board[idx]['meeples'], meeple))
            count += 1
        except ValueError:
            #print("count: %s" % count)
            return count

def unmake(stack):
    # TODO make this not unintelligible, 0 = swap, 1 = pop, 2 = append
    while stack:
        args = stack.pop()
        action = args[0]
        
        if action == 0:
            args[1][args[2]] = args[3]
        elif action == 1:
            args[1][args[2]].pop() 
        elif action == 2:
            args[1].append(args[2])
        else:
            raise ValueError('Invalid action type: %s' % action)


#def unmake_move(move, board, starting_meeples, end_tile):
def unmake_move(move, tt, starting_meeples, end_tile):
    for idx, meeple in move[1:-1]:
        try:
            tt.board[idx]['meeples'].remove(meeple)
        except ValueError:
            #print(move)
            #pretty_print_board2(*board_info)
            #raw_input("meeple gone") 
            pass    # if meeple was already removed (e.g. by assassin or loop) do nothing

    tt.board[move[0][0]]['meeples'] = starting_meeples
    #board[move[-1][0]]['meeples'] = ending_meeples
    tt.board[move[-1][0]] = end_tile

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
    TT = TableTop(board=board, n_cols=n_cols)
    TT.merchant_deck = [FAKIR]*18 + [IVORY, JEWELS, GOLD]*2 + [PAPYRUS, SILK, SPICE]*4 + [FISH, WHEAT, POTTERY]*6
    shuffle(TT.merchant_deck)
    TT.djinn_deck = [4]*4 + [5] + [6]*10 + [8]*5 + [10]*2
    shuffle(TT.djinn_deck)
    n_players = 2
    TT.player = [None]  + [{ 'coins' : 50, 
                             'camels' : 8,
                             'fakirs' : 0, 
                             'viziers' : 0,
                             'elders' : 0,
                             'djinns' : [],
                             'merchant_sets' : []
                             }] * n_players
    print(TT)
    print([blue_tiles(i, TT) for i in xrange(len(TT.board))])
    print("Run time: %s" % (time.time() - start_time))


    import cProfile
    #cProfile.run('gen_moves((board, n_rows, n_cols))')
    ply = 3
    #cProfile.run('print("best score: %d, %s" % minimax(ply, TT))')
    cProfile.run('print("best score: %d, %s" % alphabeta(ply, TT, 0, -maxint, maxint, True))')

    print(TT)

    # Test scaffolding
    testing = True
    testing = False
    if (testing):
        print(TT.merchant_deck[:])
        print("stuff %s " % TT['merchant_deck'])
        
        ##print("Run time: %s" % (time.time() - start_time))   if depth == 0:

