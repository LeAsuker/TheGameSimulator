# This is a simulation of the The Game card game, where one has a deck of
# cards from 2-99 and has to stack them onto 4 stacks -
# two go from 100 down, two from 1 up. For the former, each card has to have
# a smaller number than the one currently on top, and for the latter
# the reverse applies.

# Over 10 clause.

"""
Now how to go about it - let us create classes for everything.
Field class that includes the deck we will be playing on.
CardStack class that will go from one number to another and will include a list.
Deck class that will include cards
Player class that will include an AI and the cards it will have in its hand.


"""

import math
import random

DOWN = 0
UP = 1


def valid_play_up(card: int, card_stack: "CardStack") -> bool:
    return card > card_stack.peek() or card == card_stack.peek() - 10


def valid_play_down(card: int, card_stack: "CardStack") -> bool:
    return card < card_stack.peek() or card == card_stack.peek() + 10


class Deck:
    def __init__(self, smallest: int, largest: int) -> None:
        self.smallest = smallest
        self.largest = largest
        self.cards = [card for card in range(smallest, largest + 1)]

        self.empty = False
        if len(self.cards) == 0:
            self.empty = True

        random.shuffle(self.cards)
        return


class Player:
    def __init__(self, id_num: int) -> None:
        self.id: int = id_num
        self.hand: set[int] = set()
        self.options: set[tuple[int, int]] = set()
        return

    def draw(self, deck: "Deck", amount: int) -> None:
        if deck.empty:
            return

        for _ in range(amount):
            if len(deck.cards) == 0:
                break
            self.hand.add(deck.cards.pop())

        if len(deck.cards) == 0:
            deck.empty = True

        return

    def play_card(self, card: int, target: "CardStack") -> None:
        assert card in self.hand

        if target.direction == DOWN:
            assert valid_play_down(card, target)
            target.cards.append(card)
        elif target.direction == UP:
            assert valid_play_up(card, target)
            target.cards.append(card)

        self.hand.remove(card)

    def calc_options(self, field: "Field") -> int:
        possibilities = 0
        for card in self.hand:
            for card_stack in field.card_stacks_down:
                if valid_play_down(card, card_stack):
                    self.options.add((card, card_stack.id))
                    possibilities += 1
            for card_stack in field.card_stacks_up:
                if valid_play_up(card, card_stack):
                    self.options.add((card, card_stack.id))
                    possibilities += 1
        return possibilities

    # This is the playing AI, it currently calculates
    # the option that locally changes the numbers the least
    # It does not communicate, does not look into the future,
    # and always resets by 10 when possible.
    def best_option(self, field: "Field") -> tuple[int, int]:
        assert len(self.options) > 0
        curr_best = math.inf
        to_play = None

        for option in self.options:
            curr_dist = field.stack_score_distance(option)
            if curr_dist < curr_best:
                curr_best = curr_dist
                to_play = option
        assert to_play is not None
        return to_play

    def empty_hand(self) -> bool:
        return len(self.hand) == 0


class CardStack:
    def __init__(self, id_num: int, direction: int, min_bound: int, max_bound: int):
        self.id = id_num
        self.direction = direction
        self.min_bound = min_bound
        self.max_bound = max_bound
        self.cards: list[int] = []

    def peek(self) -> int:
        if len(self.cards) > 0:
            return self.cards[-1]
        elif self.direction == DOWN:
            return self.max_bound
        elif self.direction == UP:
            return self.min_bound

        assert False


class Field:
    def __init__(
        self,
        deck: Deck,
        player_number: int,
        stack_amount: int,
        stack_min: int,
        stack_max: int,
    ):
        self.deck = deck

        self.card_stacks_up: list[CardStack] = [
            CardStack(i, UP, stack_min, stack_max) for i in range(stack_amount)
        ]
        self.card_stacks_down: list[CardStack] = [
            CardStack(i + stack_amount, DOWN, stack_min, stack_max)
            for i in range(stack_amount)
        ]

        self.players: list[Player] = [Player(i) for i in range(player_number)]
        self.curr_player_id: int = 0
        self.stack_amount = stack_amount
        self.player_number = player_number

    def first_draw(self, card_amount: int) -> None:
        for player in self.players:
            player.draw(self.deck, card_amount)

    def stack_score_distance(self, option: tuple[int, int]) -> int:
        card, stack_id = option
        card_stack = self.get_stack_from_id(stack_id)

        if card_stack.direction == UP:
            return card - card_stack.peek()
        else:
            return card_stack.peek() - card

    def all_hands_empty(self) -> bool:
        for player in self.players:
            if not player.empty_hand():
                return False
        return True

    def next_turn(self) -> None:
        self.curr_player_id += 1
        self.curr_player_id %= playing_field.player_number

    def print_state(self) -> None:
        for stack in self.card_stacks_up:
            print("UP Stack", stack.id, "top:", stack.peek())
        for stack in self.card_stacks_down:
            print("DOWN Stack", stack.id, "top:", stack.peek())
        for player in self.players:
            print("Player", player.id, "hand:", player.hand)
        print("=========")

    def get_stack_from_id(self, stack_id: int) -> CardStack:
        if stack_id >= playing_field.stack_amount:
            return playing_field.card_stacks_down[stack_id - playing_field.stack_amount]
        else:
            return playing_field.card_stacks_up[stack_id]


# Used to track statistics
Losses = 0
Wins = 0

for game in range(1000):
    # while Wins == 0:
    playing_field = Field(Deck(2, 99), 4, 2, 1, 100)
    playing_field.first_draw(6)
    curr_player = playing_field.players[playing_field.curr_player_id]

    # each while True loop is a game of The Game
    loss_flag = False
    while True:
        curr_player = playing_field.players[playing_field.curr_player_id]
        for _ in range(2):
            possible_moves = curr_player.calc_options(playing_field)
            if possible_moves == 0 and not curr_player.empty_hand():
                loss_flag = True
                break
            # empty hand
            elif possible_moves == 0:
                break

            best_play = curr_player.best_option(playing_field)
            card, stack_id = best_play

            card_stack = playing_field.get_stack_from_id(stack_id)

            curr_player.play_card(card, card_stack)
            assert card_stack.peek() == card
            curr_player.options = set()

            print("played card", card, "to stack", stack_id)

        if loss_flag:
            print("LOSS")
            playing_field.print_state()
            Losses += 1
            break

        if playing_field.deck.empty and playing_field.all_hands_empty():
            print("WIN")
            playing_field.print_state()
            Wins += 1
            break

        curr_player.draw(playing_field.deck, 2)
        playing_field.next_turn()


print("Wins: ", Wins)
print("Losses: ", Losses)
