# This is a simulation of the The Game card game, where one has a deck of
# cards from 2-99 and has to stack them onto 4 stacks -
# two go from 100 down, two from 1 up. For the former, each card has to have
# a smaller number than the one currently on top, and for the latter
# the reverse applies.

# Over 10 clause - one can also add a card that is 10 points 'in reverse' to a stack. This
# is a necessary mechanic that greatly increases the win rate.

import math
import random

DOWN = 0
UP = 1

# Config
KEEP_PLAYING_THRESHOLD = -10  # How big of a diff to keep playing cards?
GAME_AMOUNT = 1000  # How many games to simulate
DEBUG_INFO = False


def valid_play(card: int, card_stack: "CardStack", direction: int) -> bool:
    if direction == UP:
        return card > card_stack.peek() or card == card_stack.peek() - 10
    return card < card_stack.peek() or card == card_stack.peek() + 10


def best_play_helper(curr_player: "Player", field: "Field") -> tuple[int, "CardStack"]:
    best_play = curr_player.best_option(playing_field)
    card, stack_id = best_play
    card_stack = playing_field.get_stack_from_id(stack_id)
    return card, card_stack


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
                if DEBUG_INFO:
                    print("Player", self.id, "Deck empty, no draw!")
                break
            if DEBUG_INFO:
                print("Player", self.id, "drew card", deck.cards[-1])
            self.hand.add(deck.cards.pop())

        if len(deck.cards) == 0:
            deck.empty = True

        return

    def play_card(self, card: int, target: "CardStack") -> None:
        assert card in self.hand
        if DEBUG_INFO:
            print("Player", self.id, "Played card", card, "to stack", target.id)

        if target.direction == DOWN:
            assert valid_play(card, target, DOWN)
            target.cards.append(card)
        elif target.direction == UP:
            assert valid_play(card, target, UP)
            target.cards.append(card)

        self.hand.remove(card)

    # This gets all legal moves
    def calc_options(self, field: "Field") -> int:
        self.options = set()
        possibilities = 0
        for card in self.hand:
            for card_stack in field.card_stacks_down:
                if valid_play(card, card_stack, DOWN):
                    self.options.add((card, card_stack.id))
                    possibilities += 1
            for card_stack in field.card_stacks_up:
                if valid_play(card, card_stack, UP):
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

    def no_id_stack_score_distance(self, option: tuple[int, "CardStack"]) -> int:
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
        print("== Final State ==")
        for stack in self.card_stacks_up:
            print("UP Stack", stack.id, "top:", stack.peek())
            print(stack.cards)
        for stack in self.card_stacks_down:
            print("DOWN Stack", stack.id, "top:", stack.peek())
            print(stack.cards)
        for player in self.players:
            print("Player", player.id, "hand:", player.hand)
        print(len(self.deck.cards), " cards left in deck")
        print(self.deck.cards)
        print("=========")
        return None

    def get_stack_from_id(self, stack_id: int) -> CardStack:
        if stack_id >= playing_field.stack_amount:
            return playing_field.card_stacks_down[stack_id - playing_field.stack_amount]
        else:
            return playing_field.card_stacks_up[stack_id]

    def card_amount_check(self) -> bool:
        card_amount = 0
        for stack in self.card_stacks_up:
            card_amount += len(stack.cards)
        for stack in self.card_stacks_down:
            card_amount += len(stack.cards)

        card_amount += len(self.deck.cards)
        for player in self.players:
            card_amount += len(player.hand)

        return card_amount == 98

    def player_hand_check(self) -> bool:
        for player in self.players:
            if len(player.hand) > 6:
                return False

        if self.deck.empty:
            return True

        for player in self.players:
            if len(player.hand) not in [0, 6]:
                return False

        return True


Losses = 0
Wins = 0
Option_numerator = 0
Option_denominator = 0

for game in range(GAME_AMOUNT):
    playing_field = Field(Deck(2, 99), 4, 2, 1, 100)
    playing_field.first_draw(6)
    curr_player = playing_field.players[playing_field.curr_player_id]

    # each while True loop is a game of The Game
    loss_flag = False
    min_card_play = 2
    while True:
        if playing_field.deck.empty:
            min_card_play = 1

        curr_player = playing_field.players[playing_field.curr_player_id]
        # First minimum amount of cards is played
        for _ in range(min_card_play):
            if curr_player.empty_hand():
                break

            possible_moves = curr_player.calc_options(playing_field)

            Option_numerator += possible_moves  # Not skewed due to empty hands
            Option_denominator += 1

            # We know hand is not empty
            if possible_moves == 0:
                loss_flag = True
                break

            card, card_stack = best_play_helper(curr_player, playing_field)

            curr_player.play_card(card, card_stack)
            assert card_stack.peek() == card

        # This is disgusting, I know
        # if there is a play
        extra_draw = 0
        if curr_player.calc_options(playing_field) != 0:
            # find best play
            best_play = best_play_helper(curr_player, playing_field)
            diff = playing_field.no_id_stack_score_distance(best_play)
            card, card_stack = best_play
            # while best play is good enough
            while diff <= KEEP_PLAYING_THRESHOLD:
                # play it
                curr_player.play_card(card, card_stack)
                extra_draw += 1
                # if no play leave
                if curr_player.calc_options(playing_field) == 0:
                    break

                card, card_stack = best_play_helper(curr_player, playing_field)
                diff = playing_field.no_id_stack_score_distance((card, card_stack))

        curr_player.draw(playing_field.deck, min_card_play + extra_draw)
        if not loss_flag:
            # why is print_state() not returning anything a problem according to mypy
            assert playing_field.card_amount_check(), playing_field.print_state()  # type: ignore
            assert playing_field.player_hand_check(), playing_field.print_state()  # type: ignore

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

        playing_field.next_turn()


print("Wins: ", Wins)
print("Losses: ", Losses)
print("Winrate of", (Wins / GAME_AMOUNT) * 100, "%")
print(
    "Players had an average of",
    round(Option_numerator / Option_denominator, 2),
    "options each turn",
)
