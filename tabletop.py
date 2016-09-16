from __future__ import print_function
from random import randint, seed, shuffle
import config


class TableTop(object):
    def __init__(self, seed=randint(0,10000)):
        """Set up a standard game of fivetribes for the beginning of play"""
        self.n_cols = 5 
        self.n_rows = 6
        self.board = self.generate_starting_board(seed) 

        self.merchant_deck = config.NEW_MERCHANT_DECK
        shuffle(self.merchant_deck)

        self.djinn_deck = [4]*4 + [5] + [6]*10 + [8]*5 + [10]*2
        shuffle(self.djinn_deck)

        self.n_players = 2
        self.player = [None] # dummy to shift indexes to match Player 1 / Player 2 
        for _ in range(self.n_players):
            self.player.append({ 'coins' : 50, 
                                 'camels' : 8,
                                 'fakirs' : 0, 
                                 'viziers' : 0,
                                 'elders' : 0,
                                 'djinns' : [],
                                 'merchant_sets' : []
                                 })

        self.surrounding_blue_tiles = self._precompute_blue_tiles()
        self.cur_player = 1
    
    def generate_starting_board(self, s):
        seed(s)
        print("Generating starting board with seed %s" % s)

        # TODO use actual tiles, not just randomly generated ones
        tile_type = [config.VILLAGE, config.OASSIS, config.SACRED_PLACE, \
                     config.HALF_MARKET, config.FULL_MARKET]
        bag_of_meeples = config.NEW_MEEPLE_BAG
        shuffle(bag_of_meeples)

        board = [] 
        for i in range(self.n_cols * self.n_rows):
            board.append({'meeples' : [],
                            'value': randint(3,12), 
                            'type' : tile_type[randint(0,4)], 
                            'trees': 0, 
                            'palaces' : 0, 
                            'camel': config.NO_CAMEL
                            }) 
            for _ in range(3):
                board[i]['meeples'] += bag_of_meeples.pop()
        return board


    def _precompute_blue_tiles(self):
        """
        Create a lookup table of the number of blue tiles around a given tile.
        Used when scoring builders.
        """
        def is_blue_tile(tile):
            """Determine if the given tile is a blue tile"""
            return tile['type'] == config.VILLAGE or tile['type'] == config.SACRED_PLACE

        table = []
        # do a computation for every tile
        for i in range(self.n_cols * self.n_rows):
            left       = i - 1
            center     = i
            right      = i + 1
            top        = -self.n_cols
            bot        = self.n_cols
            on_left    = center % self.n_cols == 0
            on_right   = right % self.n_cols == 0
            on_top_row = center+top < 0
            on_bot_row = center+bot >= len(self.board)
            
            blues = 0
            # check a given tile and its 8 neighbors for count of blues tiles
            if not on_top_row:
                if not on_left and is_blue_tile(self.board[top+left]):
                    blues += 1
                if is_blue_tile(self.board[top+center]):
                    blues += 1
                if not on_right and is_blue_tile(self.board[top+right]):
                    blues += 1
            if not on_left and is_blue_tile(self.board[left]):
                blues += 1
            if is_blue_tile(self.board[center]):
                blues += 1
            if not on_right and is_blue_tile(self.board[right]):
                blues += 1
            if not on_bot_row:
                if not on_left and is_blue_tile(self.board[bot+left]):
                    blues += 1
                if is_blue_tile(self.board[bot+center]):
                    blues += 1
                if not on_right and is_blue_tile(self.board[bot+right]):
                    blues += 1
            table += [blues] # store each tile's blue count for future lookup 
        return table


    def __getitem__(self, key):
        return self.__dict__[key]


    def __setitem__(self, key, value):
        self.__dict__[key] = value


    def __repr__(self):
        #TODO make this return strings
        self.pretty_print_board(self.board, self.n_rows, self.n_cols)
        print("merchant %s" % self.merchant_deck)
        print("djinn %s" % self.djinn_deck)
        print("player %s" % self.player)
        return ''


    def pretty_print_board(self, board, n_rows, n_cols):
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
