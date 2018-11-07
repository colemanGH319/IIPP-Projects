try:
    import simplegui
except:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import random

# load card sprite - 936x384 - source: jfitz.com
CARD_SIZE = (72, 96)
CARD_CENTER = (36, 48)
card_images = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/cards_jfitz.png")

CARD_BACK_SIZE = (72, 96)
CARD_BACK_CENTER = (36, 48)
card_back = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/card_jfitz_back.png")    

# initialize some useful global variables
in_play = False
outcome = ""


# define globals for cards
SUITS = ('C', 'S', 'H', 'D')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K')
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':10, 'Q':10, 'K':10}
score = 0
total = "Total score: " + str(score)
current_hand = "Current hand: 0"

# define card class
class Card:
    def __init__(self, suit, rank):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print("Invalid card: ", suit, rank)

    def __str__(self):
        return self.suit + self.rank

    def get_suit(self):
        return self.suit

    def get_rank(self):
        return self.rank

    def draw(self, canvas, pos, hidden=False):
        card_loc = (CARD_CENTER[0] + CARD_SIZE[0] * RANKS.index(self.rank), 
                    CARD_CENTER[1] + CARD_SIZE[1] * SUITS.index(self.suit))
        if not hidden:
            canvas.draw_image(card_images, card_loc, CARD_SIZE, [pos[0] + CARD_CENTER[0], pos[1] + CARD_CENTER[1]], CARD_SIZE)
        else:
            canvas.draw_image(card_back, (36,48), CARD_SIZE, [pos[0] + CARD_CENTER[0], pos[1] + CARD_CENTER[1]], CARD_SIZE)
# define hand class
class Hand:
    def __init__(self, dealer = False):
        self.cards = []
        self.is_dealer = dealer
    def __str__(self):
        card_list = [card.__str__() for card in self.cards]
        return str(card_list)

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        rank_list = [card.get_rank() for card in self.cards]
        self.score = sum([VALUES[rank] for rank in rank_list])
        if 'A' in rank_list and self.score <= 11:
            self.score += 10
        return self.score
    
    def draw(self, canvas, pos):
        if self.is_dealer:
            if not in_play:
                i = 0
                while i < len(self.cards):
                    self.cards[i].draw(canvas, pos)
                    i += 1
                    pos[0] += CARD_SIZE[0]
            else:
                self.cards[0].draw(canvas, pos)
                self.cards[1].draw(canvas, [pos[0] + CARD_BACK_SIZE[0],	pos[1]], True)
        else:
            i = 0
            while i < len(self.cards):
                self.cards[i].draw(canvas, pos)
                i += 1
                pos[0] += CARD_SIZE[0]
            
            
# define deck class 
class Deck:
    def __init__(self, suits, ranks):
        self.cards = []
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self, hand):
        new_card = self.cards.pop()
        hand.add_card(new_card)
    
    def __str__(self):
        card_list = [card.__str__() for card in self.cards]
        return str(card_list)
    


#define event handlers for buttons
def deal():
    global outcome, in_play, player, dealer, new_deck, status, score, current_hand, total
    if in_play:
        status = "You lose! Hit or stand?"
        score -= 1
        total = "Total score: " + str(score)
    else:
        status = "Hit or stand?"
    player = Hand()
    dealer = Hand(True)
    new_deck = Deck(SUITS, RANKS)
    new_deck.shuffle()
    new_deck.deal_card(player)
    new_deck.deal_card(dealer)
    new_deck.deal_card(player)
    new_deck.deal_card(dealer)
    current_hand = "Current hand: " + str(player.get_value())
    in_play = True
    

def stand():
    global in_play, status, score, current_hand, total
    current_hand = "Current hand: " + str(player.get_value())
    if player.get_value() > 21:
        status = "You have busted. Deal again?"
        in_play = False
        score -= 1
    else:
        while dealer.get_value() < 17:
            new_deck.deal_card(dealer)
        if dealer.get_value() > 21:
            status = "Dealer has busted. Player wins! Deal again?"
            in_play = False
            score += 1
        elif dealer.get_value() >= player.get_value():
            status = "Dealer wins."
            in_play = False
            score -= 1
        else:
            status = "Player wins!"
            in_play = False
            score += 1
    total = "Total score: " + str(score)
            
def hit():
    global in_play, player, new_deck, status, score, current_hand, total
    if in_play:
        if player.get_value() < 21:
            new_deck.deal_card(player)
            if player.get_value() > 21:
                status = "You have busted. Deal again?"
                in_play = False
                score -= 1
                total = "Total score: " + str(score)
            elif player.get_value() == 21:
                in_play = False
                stand()
            else:
                status = "Hit or stand?"

        else:
            status = "You have busted. Deal again?"
            in_play = False
        current_hand = "Current hand: " + str(player.get_value())
        
        

# draw handler    
def draw(canvas):
    try:
        player.draw(canvas, [200,450])
        dealer.draw(canvas, [150, 100])
        canvas.draw_text(status, [275, 280], 15, 'White')
        canvas.draw_text(total, [275, 300], 15, 'Blue')
        canvas.draw_text(current_hand, [275, 320], 15, 'Blue')
        canvas.draw_text("Blackjack", [251, 41], 35, 'Yellow')
        canvas.draw_text("Blackjack", [250, 40], 35, 'Black')
    except:
        pass

# initialization frame

frame = simplegui.create_frame("Blackjack", 600, 600)
frame.set_canvas_background("Green")

#create buttons and canvas callback
frame.add_button("Deal", deal, 200)
frame.add_button("Hit",  hit, 200)
frame.add_button("Stand", stand, 200)
frame.set_draw_handler(draw)


# get things rolling

frame.start()
deal()
