def gen_moves(tt, debug=False):
    tot_route_count = 0
    tot_move_count = 0
    
    for idx in xrange(len(tt.board)):
        #TODO {key: [] for key in MEEPLES}
        cache = {'r':[], 'g':[], 'b':[], 'y':[], 'w':[]}
        route_count = 0
        for route in gen_routes(idx, tt):
            #print("Trying route: %s" % route) 
            route_count += 1
            move_count = 0
            for move in permute_meeples_over_route(route, tt.board, cache):
                #print("move %s" % move)
                move_count += 1
                yield move
    
            tot_move_count += move_count
        tot_route_count += route_count
    #print("Total Routes found: %d" % (tot_route_count))
    #print("Total Moves found: %d" % (tot_move_count))

def gen_routes(idx, tt):
    n_meeples = num_meeples(tt.board[idx])
    if n_meeples == 0:
        return [] # tiles with no meeples have no routes
    else:
        return _gen_routes(n_meeples, '', idx, [idx], tt)

# returns number of meeples on a given tile
def num_meeples(tile):
    return len(tile['meeples'])

def _gen_routes(n, prev_dir, curr_idx, route, tt):
    if n <= 0:
        # FIXME hack to prevent a route from starting and stopping on same tile 
        return [route] if route[-1] != route[0] else [] 
        #return [route] 
    
    n_rows = tt.n_rows 
    n_cols = tt.n_cols 
    result = []
    # if not top row
    if curr_idx >= n_cols and prev_dir != 'S' :                 
        next_idx = curr_idx - n_cols
        # move up 
        result += _gen_routes(n-1, 'N', next_idx, route+[next_idx], tt)  
    # if not right column
    if curr_idx % n_cols < n_cols-1 and prev_dir != 'W':
        next_idx = curr_idx + 1
        # move right 
        result += _gen_routes(n-1, 'E', next_idx, route+[next_idx], tt)  
    # if not bottom row
    if curr_idx < (n_rows-1) * n_cols and prev_dir != 'N':      
        next_idx = curr_idx + n_cols
        # move down 
        result += _gen_routes(n-1, 'S', next_idx, route+[next_idx], tt)  
    # if not left column
    if curr_idx % n_cols != 0 and prev_dir != 'E': 
        next_idx = curr_idx - 1
        # move left 
        result += _gen_routes(n-1, 'W', next_idx, route+[next_idx], tt)  
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

def valid_end_meeples(route, board):
    start_idx = route[0]
    end_idx = route[-1]
    if start_idx == end_idx:
        return [] # route stopping on starting tile confuses meeple matcher
    
    starting_meeples = board[start_idx]['meeples']
    ending_meeples = board[end_idx]['meeples']
    return list(set(starting_meeples) & set(ending_meeples))

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

