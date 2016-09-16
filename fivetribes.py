from __future__ import print_function
from random import randint, seed, shuffle
from sys import maxint
from tabletop import TableTop
import scoring
import gen_moves

def minimax(depth, tt):
    if depth == 0:
        # TODO do we need static evaluator? how should we scale its value
        return 0, []

    best_move = []
    max_score = -maxint - 1  # negative infinity
    for move in gen_moves.gen_moves(tt):
        undo_stack = []

        meeple_count = make_move(move, tt.board, undo_stack) 

        last_step = move[-1]
        score = scoring.calc_score(last_step, meeple_count, undo_stack, tt)\
                - minimax(depth - 1, tt)[0]

        unmake(undo_stack)

        if (score > max_score):
            print("better score: %s" % score)
            max_score = score
            best_move = move
    return max_score, best_move

def alphabeta(depth, tt, net_score=0, alpha=-maxint, beta=maxint, max_node=True):
    if depth == 0:
        # TODO do we need static evaluator? how should we scale its value
        return net_score, []

    best_move = []
    undo_stack = []
    if max_node:
        v = -maxint-1  # negative infinity
        for move in gen_moves.gen_moves(tt, debug=True):
            tt.cur_player = 1 
            #print("max move %s: " % move)
            meeple_count = make_move(move, tt.board, undo_stack) 
            last_step = move[-1]
            score = net_score + scoring.calc_score(last_step, meeple_count, undo_stack, tt) 
            #print("scored: %s" % score)
            value = alphabeta(depth - 1, tt, score, alpha, beta, False)[0]
            #print("after alphabeta: %s" % value)
            unmake(undo_stack)

            if value > v:
                v = value
                best_move = move
                #print("new max: %d, %s" % (v, best_move))
            alpha = max(alpha, v)
            if beta <= alpha:
                break 
        return v, best_move
    else:
        v = maxint # positive infinity
        for move in gen_moves.gen_moves(tt):
            tt.cur_player = 2
            #print("min move %s: " % move)
            meeple_count = make_move(move, tt.board, undo_stack) 
            last_step = move[-1]
            score = net_score - scoring.calc_score(last_step, meeple_count, undo_stack, tt) 
            #print("min scored: %s" % score)
            value = alphabeta(depth - 1, tt, score, alpha, beta, True)[0]
            #print("after alphabeta: %s" % value)
            unmake(undo_stack)

            if value < v:
                v = value
                best_move = move
                #print("new min: %d, %s" % (v, best_move))
            beta = min(beta, v)
            if alpha >= beta:
                break
        return v, best_move

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

    # Remove all matching meeples from end tile
    count = 1 # move adds a meeple
    while True:
        try:
            board[idx]['meeples'].remove(meeple)
            count += 1
        except ValueError:
            return count

def unmake(stack):
    # TODO!! make this not unintelligible, 0 = swap, 1 = pop, 2 = append
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


if __name__ == '__main__':
        
    import time
    start_time = time.time()

    #TT = TableTop(1100)
    #TT = TableTop(3016)
    TT = TableTop()
    print("Board generated in %s secs" % (time.time() - start_time))
    print(TT)


    import cProfile
    ply = 2
    print("Calculating best move...")
    #cProfile.run('print("best score: %d, %s" % minimax(ply, TT))')
    #cProfile.run('print("best score: %d, %s" % alphabeta(ply, TT))')

    print("Best move - Net score %d, Move: %s" % alphabeta(ply, TT))
    print("Run time %s secs" % (time.time() - start_time))
    #print(TT)
