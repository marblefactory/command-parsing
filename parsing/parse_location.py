from actions.location import *
from parsing.parser import *


def move_object_name() -> Parser:
    """
    :return: a parser which parses names of objects which can be moved to, i.e. table, door, desk.
    """
    object_names = ['table', 'door', 'desk', 'server', 'room', 'toilet']

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
    forwards_matcher = strongest_word(['forward', 'front'], make_parser=word_meaning)
    backwards_matcher = strongest_word(['backward', 'behind'], make_parser=word_meaning)

    forwards = forwards_matcher.ignore_parsed(MoveDirection.FORWARDS)
    backwards = backwards_matcher.ignore_parsed(MoveDirection.BACKWARDS)

    left = word_match('left').ignore_parsed(MoveDirection.LEFT)
    right = word_match('right').ignore_parsed(MoveDirection.RIGHT)

    return strongest([left, right, forwards, backwards])


def object_relative_direction() -> Parser:
    """
    :return: a parser for object relative directions. This defaults to objects in the vicinity if no left, right, etc is found.
    """
    return strongest([move_direction(), produce(ObjectRelativeDirection.VICINITY, 1.0)])


def absolute() -> Parser:
    """
    :return: a parser for absolute locations, e.g. '[go to] lab 201'.
    """
    # When describing a storage room, the player can optionally say 'room' too.xX
    storage_room_parser = strongest([produce('room', 1), maybe(word_match('room'))])
    storage_x = word_match('storage').then(append(storage_room_parser)).then(append(number()))

    lab = strongest_word(['lab', 'live']) # Because of speech parsing by Google.

    office_x = word_match('office').then(append(number()))
    computer_lab_x = word_match('computer').then(append(lab)).then(append(number()))
    lab_x = lab.then(append(number()))
    meeting_room_x = word_match('meeting').then(append(word_match('room'))).then(append(number()))
    workshop_x = word_match('workshop').then(append(number()))
    server_room_x = word_match('server').then(append(word_match('room'))).then(append(number()))

    reception = word_match('reception')
    kitchen = word_match('kitchen')
    gun_range = word_match('range')
    mortuary = word_match('mortuary')
    security_office = word_match('security').then(append(word_match('office')))

    places = [
        storage_x,
        office_x,
        computer_lab_x,
        lab_x,
        meeting_room_x,
        workshop_x,
        server_room_x,
        reception,
        kitchen,
        gun_range,
        mortuary,
        security_office
    ]

    return strongest(places).map_parsed(lambda place_name: Absolute(place_name))


def positional() -> Parser:
    """
    :return: a parser for positional locations, e.g. 'third door on your left'
    """
    def combine_ordinal_num(acc: List, r1: Response) -> Parser:
        # Parses an ordinal number, or defaults to 0 if there is no ordinal number.
        default = produce(parsed=0, response=0)
        ord = strongest([anywhere(ordinal_number()), default])

        return ord.map(lambda parsed_num, r2: (acc + [parsed_num], mix(r1, r2, 0.8)))

    def combine_direction(acc: List, r1: Response) -> Parser:
        default = produce(parsed=MoveDirection.FORWARDS, response=0)
        dir = strongest([anywhere(move_direction()), default])

        return dir.map(lambda parsed_dir, r2: (acc + [parsed_dir], mix(r1, r2, 0.8)))

    obj = anywhere(move_object_name()).map_parsed(lambda parsed_name: [parsed_name])

    return obj.then(combine_ordinal_num) \
              .then(combine_direction) \
              .map_parsed(lambda p: Positional(p[0], p[1], p[2]))


def directional() -> Parser:
    """
    :return: a parser for directions, e.g. go left, right, forwards, backwards.
    """
    return move_direction().map_parsed(lambda dir: Directional(dir))


def stairs() -> Parser:
    """
    :return: a parser for stair directions, e.g. upstairs, downstairs.
    """
    up = strongest_word(['up', 'upstairs']).ignore_parsed(FloorDirection.UP)
    down = strongest_word(['down', 'downstairs']).ignore_parsed(FloorDirection.DOWN)

    return strongest([up, down]).map_parsed(lambda dir: Stairs(dir))


def behind() -> Parser:
    """
    :return: a parser for behind object locations, e.g. behind the sofas.
    """
    other_side_verb = word_match('other').ignore_then(word_match('side'))
    verb = strongest([word_match('behind'), word_match('around'), other_side_verb])

    return verb.ignore_then(move_object_name()).map_parsed(lambda obj_name: Behind(obj_name))


def location() -> Parser:
    """
    :return: a parser which parses locations.
    """
    # Half the response to give bias towards positional locations since both use directions.
    dir = directional().map_response(lambda r: r/2)
    return strongest([absolute(), positional(), dir, stairs(), behind()])
