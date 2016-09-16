import config


# Lookup array for scoring Merchant Sets
#   index represents the set length
#   e.g. 2 card set = 3 pts, 3 card set = 7 pts, etc.
score_merchant_set = [0, 1, 3, 7, 13, 21, 30, 40, 50, 60]


def calc_score(last_step, meeple_count, undo_stack, tt):
    """Calculate the score of ending a move on a given tile with a given meeple"""
    idx, meeple = last_step
    tile = tt.board[idx]
    return meeple_score(meeple, meeple_count, idx, undo_stack, tt) \
            + tile_score(tile, undo_stack, tt) \
            + camel_score(meeple, tile, undo_stack)


def meeple_score(meeple, meeple_count, idx, undo_stack, tt):
    """Calculate portion of score due to matching different kinds of meeples"""
    # TODO fakirs?
    if meeple == config.RED:
        return score_assassins(meeple_count, idx, undo_stack, tt)
    elif meeple == config.GREEN:
        undo_stack.append((0, tt, 'merchant_deck', tt.merchant_deck[:]))
        score = 0
        for _ in xrange(meeple_count):
            card = tt.merchant_deck.pop() # TODO handle if merchant deck runs out
            score += score_merchants(card, tt.player[tt.cur_player], undo_stack)
        return score
    elif meeple == config.BLUE:
        return score_builders(meeple_count, idx, tt) 
    elif meeple == config.WHITE:
        return 2 * meeple_count    # Each elder is worth 2 points
    elif meeple == config.YELLOW:
        # TODO 10pts for everyone with less viziers?
        return meeple_count     # Each vizier is worth 1 point 
    else:
        raise ValueError('Not a valid meeple type: %s' % meeple) 


def score_assassins(meeple_count, idx, undo_stack, tt):
    # TODO!! only assasinate in range, pick best scoring, assassinate viziers, elders?
    max_score = 0
    for tile in tt.board:
        if len(tile['meeples']) == 1 and tile['camel'] == '':
            undo_stack.append((0, tile, 'meeples', tile['meeples']))
            undo_stack.append((0, tile, 'camel', ''))
            tile['meeples'] = [] 
            tile['camel'] = config.MY_CAMEL
            return tile['value']
    
            # if tile in assasin range
            if tile['value'] > max_score:
                max_score = tile['value']
                # do assasination, how to undo?
    return max_score 


def score_merchants(card, player, undo_stack):
    """
    Score the value of adding card to player's hand. 
    Works on only one card at a time, call repeatedly to handle multiple cards
    """
    if card == config.FAKIR:
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


def score_builders(meeple_count, idx, tt):
    return meeple_count * tt.surrounding_blue_tiles[idx]


def tile_score(tile, undo_stack, tt):
    """Calculate portion of score due to landing on particular tiles"""
    tile_type = tile['type']
    if tile_type == config.OASSIS:
        undo_stack.append((0, tile, 'trees', tile['trees']))
        tile['trees'] += 1 
        return 3 if tile['camel'] == config.MY_CAMEL else 0

    elif tile_type == config.VILLAGE:
        undo_stack.append((0, tile, 'palaces', tile['palaces']))
        tile['palaces'] += 1 
        return 5 if tile['camel'] == config.MY_CAMEL else 0

    elif tile_type == config.SACRED_PLACE:
        return score_sacred_place(undo_stack, tt)

    elif tile_type == config.HALF_MARKET:
        # TODO enough coins to buy?
        player_hand = tt.player[tt.cur_player]
        half_market = tt.merchant_deck[-3:]
        _, idx = best_cards(half_market, player_hand['merchant_sets'])[0]
        undo_stack.append((0, tt, 'merchant_deck', tt.merchant_deck[:]))
        card = tt.merchant_deck.pop(idx-3)
        return score_merchants(card, player_hand, undo_stack)

    elif tile_type == config.FULL_MARKET:
        # TODO enough coins to buy?
        player_hand = tt.player[tt.cur_player]
        full_market = tt.merchant_deck[-6:]

        top_2_cards = best_cards(full_market, player_hand['merchant_sets'])[:2]
        # if necessary, rearrange results so popping won't make the indexes invalid
        if top_2_cards[0][1] > top_2_cards[1][1]:
            top_2_cards[0], top_2_cards[1] = top_2_cards[1], top_2_cards[0]

        undo_stack.append((0, tt, 'merchant_deck', tt.merchant_deck[:]))
        score = 0
        for _, idx in top_2_cards:
            card = tt.merchant_deck.pop(idx-6)
            score += score_merchants(card, player_hand, undo_stack)
        return score

    else:
        raise ValueError('Not a valid tile type: %s' % tile_type) 


def score_sacred_place(undo_stack, tt):
    """
    Choose highest score value djinn. 
    Completely ignore djinn effects as that is a whole 'nother level of complicated 
    """
    # TODO check player has enough elders / fakirs
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


def best_cards(merchant_cards, player_sets):
    """Sort merchant_cards by highest score for given player_sets"""
    score = [(set_size(merchant_cards[i], player_sets), i) for i in xrange(len(merchant_cards))]
    score.sort(reverse=True) 
    return score


def set_size(card, merchant_sets):
    """Return the size of the largest set that doesn't contain the card"""
    if card == config.FAKIR:
        return 0

    for set_ in merchant_sets:
        if card not in set_:
            return len(set_)
    return 0 


def camel_score(meeple, tile, undo_stack):
    """Check if a camel can be placed and compute the score for doing so"""
    if tile['camel'] == config.NO_CAMEL and not tile['meeples']:
        undo_stack.append((0, tile, 'camel', ''))
        tile['camel'] = config.MY_CAMEL
        return tile['value'] + 3 * tile['trees'] + 5 * tile['palaces'] 
    else:
        return 0
