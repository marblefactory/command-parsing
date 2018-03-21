from actions.location import *
from parsing.parser import *
from functools import partial
from utils import partial_class
import itertools


def move_object_name() -> Parser:
    """
    :return: a parser which parses names of objects which can be moved to, i.e. table, door, desk.
    """
    object_names = [
        'table', 'door', 'desk', 'server', 'room', 'toilet', 'lavatory', 'corridor', 'wall', 'pillar', 'couch', 'sofa'
    ]

    def condition(input_word: Word) -> Response:
        return float(input_word in object_names)

    return predicate(condition)


def ordinal_number() -> Parser:
    """
    :return: a parser for ordinal numbers, e.g. next, first, second, third, which are converted to their numerical
             representation.
    """
    words = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth']
    word_matchers = [word_match(word).ignore_parsed(num) for num, word in enumerate(words)] + [word_match('next').ignore_parsed(0)]
    return strongest(word_matchers)


def move_direction() -> Parser:
    """
    :return: a parser for movement directions, e.g. left, right, forwards, backwards, which are converted to Direction enums.
    """
    forwards_parser = strongest_word(['forward', 'front'], parser_constructors=[word_meaning])
    backwards_parser = strongest_word(['backward', 'behind'], parser_constructors=[word_match])

    forwards = forwards_parser.ignore_parsed(MoveDirection.FORWARDS)
    backwards = backwards_parser.ignore_parsed(MoveDirection.BACKWARDS)

    left = word_match('left').ignore_parsed(MoveDirection.LEFT)
    right = word_match('right').ignore_parsed(MoveDirection.RIGHT)

    return strongest([left, right, forwards, backwards])


def object_relative_direction() -> Parser:
    """
    :return: a parser for object relative directions. This defaults to objects in the vicinity if no left, right, etc is found.
    """
    return strongest([move_direction(), produce(ObjectRelativeDirection.VICINITY, 1.0)])


def distance() -> Parser:
    """
    :return a parser for different distances, e.g. short, far, etc
    """
    # Returns a parser to recognise the given words and return the given distance.
    def make_parser(words: List[Word], dist: Distance) -> Parser:
        return strongest_word(words, parser_constructors=[word_spelling, word_meaning]).ignore_parsed(dist)

    short_words = ['short', 'close', 'little', 'bit']
    medium_words = ['medium', 'fair']
    far_words = ['far', 'long', 'great', 'along']

    short = make_parser(short_words, Distance.SHORT)
    medium = make_parser(medium_words, Distance.MEDIUM)
    far = make_parser(far_words, Distance.FAR)

    return strongest([short, medium, far])


def absolute_place_names() -> Parser:
    """
    :return: a parser for absolute location place names, i.e. the result of the parser is a string.
    """

    # Parsers a number, or if no number was parsed, returns '1'.
    def number_or_1() -> Parser:
        parsers = [number(), produce('1', response=0.0)]
        return strongest(parsers)

    # When describing a storage room, the player can optionally say 'room' too.
    storage_room_parser = strongest([produce('room', 1), maybe(word_match('room'))])
    storage_x = word_match('storage').then(append(storage_room_parser)).then(append(number_or_1()))

    lab = word_spelling('lab', dist_threshold=0.24)  # Because of errors in speech parsing.

    office_x = word_match('office').then(append(number_or_1()))
    computer_lab_x = word_match('computer').then(append(lab)).then(append(number_or_1()))
    lab_x = lab.then(append(number_or_1()))
    meeting_room_x = word_match('meeting').then(append(word_match('room'))).then(append(number_or_1()))
    workshop_x = word_match('workshop').then(append(number_or_1()))
    server_room_x = word_match('server').then(append(word_match('room'))).then(append(number_or_1()))

    reception = word_match('reception')
    kitchen = word_match('kitchen')
    gun_range = word_match('range')
    mortuary = strongest_word(['mortuary', 'motor']).ignore_parsed('mortuary')
    security_office = word_match('security').then(append(word_match('office')))

    places = [
        reception,
        kitchen,
        gun_range,
        mortuary,
        security_office,

        storage_x,
        office_x,
        computer_lab_x,
        lab_x,
        meeting_room_x,
        workshop_x,
        server_room_x,
    ]

    return strongest(places)


def absolute() -> Parser:
    """
    :return: a parser for absolute locations, e.g. '[go to] lab 201'.
    """
    return absolute_place_names().map_parsed(lambda place_name: Absolute(place_name))


def positional() -> Parser:
    """
    :return: a parser for positional locations, e.g. 'third door on your left'
    """
    def combine_ordinal_num(makePos: Callable, r1: Response) -> Parser:
        # Parses an ordinal number, or defaults to 0 if there is no ordinal number.
        default = produce(parsed=0, response=0)
        ord = strongest([anywhere(ordinal_number()), default])

        # Partially applies the parsed position to the constructor of Positional.
        return ord.map(lambda parsed_num, r2: (partial(makePos, parsed_num), mix(r1, r2, 0.2)))

    def combine_direction(makePos: Callable, r1: Response) -> Parser:
        default = produce(parsed=MoveDirection.FORWARDS, response=0)
        dir = strongest([anywhere(move_direction()), default])

        # Completes the Positional constructor by supplying the direction.
        return dir.map(lambda parsed_dir, r2: (makePos(parsed_dir), mix(r1, r2, 0.2)))


    # Partially applies the parsed object name to the Positional init.
    obj = anywhere(move_object_name()) \
         .map_parsed(lambda parsed_name: partial_class(Positional, parsed_name))

    return obj.then(combine_ordinal_num) \
              .then(combine_direction)


def directional() -> Parser:
    """
    :return: a parser for directions, e.g. go left, right, forwards, backwards.
    """
    def combine_distance(dir: MoveDirection, dir_resp: Response) -> Parser:
        # Defaults to going medium distance.
        dist_parser = strongest([distance(), produce(Distance.MEDIUM, 0)])
        return dist_parser.map(lambda dist, _: (Directional(dir, dist), dir_resp))

    return anywhere(move_direction()).then(combine_distance)


def stairs() -> Parser:
    """
    :return: a parser for stair directions, e.g. upstairs, downstairs.
    """
    directions = [
        ('up', FloorDirection.UP),
        ('down', FloorDirection.DOWN)
    ]

    location_words = ['stairs', 'floor']

    # Parses a direction, optionally followed by a location.
    # E.g. 'go up' or 'go up the stairs', where the latter has a stronger response.
    def make_parser(dir: (str, FloorDirection), loc: str) -> Parser:
        # Increase the penalty for not having the location. This allows change stances to be parsed correctly.
        combine = lambda r1, r2: mix(r1, r2, 0.8)

        return anywhere(word_match(dir[0])) \
              .then_ignore(maybe(word_match(loc)), combine) \
              .ignore_parsed(dir[1])

    parsers = [make_parser(dir, loc) for dir, loc  in itertools.product(directions, location_words)]

    upstairs = word_match('upstairs').ignore_parsed(FloorDirection.UP)
    downstairs = word_match('downstairs').ignore_parsed(FloorDirection.DOWN)

    return strongest(parsers + [upstairs, downstairs]).map_parsed(lambda dir: Stairs(dir))


def behind() -> Parser:
    """
    :return: a parser for behind object locations, e.g. behind the sofas.
    """
    other_side = word_match('other').ignore_then(word_match('side'))
    verb = strongest([word_match('behind'), word_match('around'), other_side])

    return verb.ignore_then(move_object_name()).map_parsed(lambda obj_name: Behind(obj_name))


def end_of() -> Parser:
    """
    :return: a parser for end of rooms/corridors, e.g. end of room 102.
    """
    parser = word_match('end').ignore_then(word_match('of'))
    # Parses the name of the room/corridor to go to the end of.
    loc = strongest([
        move_object_name(),
        absolute_place_names()
    ])

    return parser.ignore_then(loc).map_parsed(lambda obj_name: EndOf(obj_name))


def location() -> Parser:
    """
    :return: a parser which parses locations.
    """
    # Half the response to give bias towards positional locations since both use directions.
    dir = directional().map_response(lambda r: r/2)
    return strongest([end_of(), absolute(), positional(), dir, stairs(), behind()])
