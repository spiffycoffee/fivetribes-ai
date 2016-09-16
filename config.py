# Common name constants for representing game objects like meeples, tiles, etc.

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
    
# Camels are represented by these when printing the board
MY_CAMEL       = '+'
OPPONENT_CAMEL = '-'
NO_CAMEL       = ''

# Meeples are represented with the below characters
RED    = 'r'  # Assassins
BLUE   = 'b'  # Builders
GREEN  = 'g'  # Merchants
WHITE  = 'w'  # Elders
YELLOW = 'y'  # Viziers
# Bag of meeples at the start, each color has a specific count
NEW_MEEPLE_BAG = [RED, BLUE, GREEN]*18 + [WHITE]*20 + [YELLOW] * 16

# Merchant card representation (rarer cards = higher num, but basically an enum)
FAKIR   = 0
FISH    = 1
WHEAT   = 2
POTTERY = 3
PAPYRUS = 4
SILK    = 5
SPICE   = 6
IVORY   = 7
JEWELS  = 8
GOLD    = 9
# Merchant deck at game start, each card has a specific count 
NEW_MERCHANT_DECK = [FAKIR]*18 + [FISH, WHEAT, POTTERY]*6 + \
                    [PAPYRUS, SILK, SPICE]*4 + \
                    [IVORY, JEWELS, GOLD]*2

# Declare meeple positions and counts with another comma separated string. 
# Use multiple letters for multiple meeples 

# or take as input diagram?
# -------------------------
# | rrgby   |
# | 12o-ctp |
