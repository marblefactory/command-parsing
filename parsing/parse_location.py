from actions.location import *
from parsing.parser import *
from functools import partial
import itertools


def hackable_object_name() -> Parser:
    """
    :return: a parser for the names of objects which can be hacked. Returns a tuple containing the name of the
             hacked object (e.g. server) and the type of object it is (e.g. TERMINAL).
    """
    terminal_words = ['terminal', 'computer', 'console', 'server', 'mainframe']
    return strongest_word(terminal_words, make_word_parsers=[word_spelling])


def pickupable_object_name(other_noun_response: Optional[float] = 0.25) -> Parser:
    """
    :param include_other_nouns: whether to search for other nouns, not only objects in the game.
    :return: a parser for the names of objects which can be picked up and thrown.
    """
    # Objects the player can actually pick up.
    names = ['rock', 'hammer', 'bottle', 'cup', 'can', 'beaker']

    rock_correction = word_match('ra', consume=Consume.WORD_ONLY).ignore_parsed('rock')
    # Strongly recognises the names of actual objects in the game, and weakly matches on other nouns.
    match = partial(word_match, consume=Consume.WORD_ONLY)

    p1 = object_spelled(names, other_noun_response=other_noun_response)
    p2 = strongest_word(names, make_word_parsers=[match])
    objects = p1 if other_noun_response else p2

    return strongest([objects, rock_correction])


def interactable_object_name(other_noun_response: Optional[float] = 0.25) -> Parser:
    """
    :param include_other_nouns: whether to search for other nouns, not only objects in the game.
    :return: a parser for the names of objects which be interacted with, e.g. picked up, hacked, thrown.
    """
    # Inhibited by directions because 'left', 'right' etc, are counted as nouns.
    return none(move_direction()) \
          .ignore_then(strongest([hackable_object_name(), pickupable_object_name(other_noun_response)]))


def move_object_name() -> Parser:
    """
    :return: a parser which parses names of objects which can be moved to, i.e. table, door, desk.
    """
    object_names = ['table', 'door', 'desk', 'room', 'corridor', 'wall', 'pillar', 'couch', 'sofa']
    object = strongest_word(object_names)

    return object


def ordinal_number() -> Parser:
    """
    :return: a parser for ordinal numbers, e.g. first, second, third, which are converted to their numerical
             representation.
    """
    words = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth']
    word_parsers = [word_match(word).ignore_parsed(num) for num, word in enumerate(words)]

    corrections = [('sorry', 3)]
    correction_parsers = [word_match(word).ignore_parsed(num) for word, num in corrections]

    return strongest(word_parsers + correction_parsers)


def description_number() -> Parser:
    """
    :return: a parser for ordinal numbers, e.g. first, second, etc, and adverbs which can be used to describe a
             number, e.g. next. Outputs a numerical representation.
    """
    adverbs = [('next', 0)]
    parsers = [word_match(word).ignore_parsed(num) for word, num in adverbs]
    return strongest(parsers + [ordinal_number()])


def move_direction() -> Parser:
    """
    :return: a parser for movement directions, e.g. left, right, forwards, backwards, which are converted to Direction enums.
    """
    forwards_words = ['forward', 'front']
    forwards_corrections = ['afford', 'for']

    forwards_parser = words_and_corrections(forwards_words, forwards_corrections, make_word_parsers=[word_spelling, word_meaning])
    backwards_parser = strongest_word(['backward', 'behind'], make_word_parsers=[word_match])

    forwards = forwards_parser.ignore_parsed(MoveDirection.FORWARDS)
    backwards = backwards_parser.ignore_parsed(MoveDirection.BACKWARDS)

    left = word_match('left').ignore_parsed(MoveDirection.LEFT)

    right_corrections = ['alright', 'ride']
    right = words_and_corrections(['right'], corrections=right_corrections, make_word_parsers=[word_spelling]) \
           .ignore_parsed(MoveDirection.RIGHT)

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
        spelling = partial(word_spelling, match_first_letter=True)
        return strongest_word(words, make_word_parsers=[spelling, word_meaning]).ignore_parsed(dist)

    short_words = ['short', 'close', 'little', 'bit']
    medium_words = ['medium', 'fair']
    far_words = ['far', 'long', 'great', 'along']

    short = make_parser(short_words, Distance.SHORT)
    medium = make_parser(medium_words, Distance.MEDIUM)
    far = make_parser(far_words, Distance.FAR)

    return strongest([short, medium, far])


def absolute_floor_name() -> Parser:
    """
    :return: a parser for names of floors, e.g. floor 0, basement, roof, etc.
    """
    floor_names = ['basement', 'ground', 'roof']

    floor_parsers = strongest_word(floor_names)
    # Parses floor 0, floor 1, and floor 2 as basement, ground, and roof respectively.
    floor_words = ['floor', 'level']
    numerical_parsers = strongest_word(floor_words).ignore_then(number()).then(index_array(floor_names))
    # Parses 'first floor', 'second floor' etc. +2 because the first floor is the roof.
    ordinal_parsers = ordinal_number().then_ignore(word_match('floor')).map_parsed(lambda n: n+2).then(index_array(floor_names))

    return strongest([floor_parsers, numerical_parsers, ordinal_parsers])


def absolute_place_names() -> Parser:
    """
    :return: a parser for absolute location place names, i.e. the result of the parser is a string.
    """

    # Parsers a number, or if no number was parsed, returns '1'.
    lab_corrections = strongest_word(['app', 'live'], make_word_parsers=[word_spelling])
    lab_spelling = word_spelling('lab', min_word_length=2, dist_threshold=0.24)
    lab = strongest([lab_spelling, lab_corrections]).ignore_parsed('lab')

    storage_x = word_match('storage').then(append(number_str()))
    office_x = word_match('office').then(append(number_str()))
    computer_lab_x = word_match('computer').then(append(lab)).then(append(number_str()))
    lab_x = lab.then(append(number_str()))
    meeting_room_x = word_match('meeting').then(append(word_match('room'))).then(append(number_str()))
    workshop_x = word_match('workshop').then(append(number_str()))
    server_room_x = word_match('server').ignore_parsed('server room').then(append(number_str()))
    toilet_x = word_match('toilet').then(append(number_str()))

    reception = word_match('reception')
    kitchen = strongest_word(['kitchen', 'kit']).ignore_parsed('kitchen')
    gun_range = strongest_word(['range', 'garage']).ignore_parsed('gun range')
    mortuary = strongest_word(['mortuary', 'motor']).ignore_parsed('mortuary')
    security_office = word_match('security').ignore_parsed('security room')
    generator_room = word_match('generator').then(append(word_match('room')))
    car_park = word_match('car').then(append(word_match('park')))
    research_lab = word_match('research').ignore_parsed('research lab')

    helicopter_words = ['chopper', 'heli', 'helicopter']
    helicopter = strongest_word(helicopter_words, make_word_parsers=[word_spelling, word_meaning_pos(POS.noun)]) \
                .ignore_parsed('helicopter')

    places = [
        reception,
        kitchen,
        gun_range,
        mortuary,
        security_office,
        car_park,
        generator_room,
        research_lab,

        storage_x,
        office_x,
        computer_lab_x,
        lab_x,
        meeting_room_x,
        workshop_x,
        server_room_x,
        toilet_x,

        helicopter,

        absolute_floor_name()
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
        ord = strongest([non_consuming(description_number()), default])

        # Partially applies the parsed position to the constructor of Positional.
        return ord.map(lambda parsed_num, r2: (partial(makePos, parsed_num), mix(r1, r2, 0.2)))

    def combine_direction(default_dir: ObjectRelativeDirection) -> Callable[[Callable, Response], Parser]:
        def f(makePos: Callable, r1: Response) -> Parser:
            default = produce(parsed=default_dir, response=0)
            dir = strongest([non_consuming(move_direction()), default])

            # Completes the Positional constructor by supplying the direction.
            return dir.map(lambda parsed_dir, r2: (makePos(parsed_dir), mix(r1, r2, 0.2)))

        return f

    def make_parser(move_obj: Parser, default_dir: ObjectRelativeDirection) -> Parser:
        # Partially applies the parsed object name to the Positional init.
        obj = non_consuming(move_obj) \
             .map_parsed(lambda parsed_name: partial(Positional.partial_init(), parsed_name))

        return obj.then(combine_ordinal_num) \
              .then(combine_direction(default_dir))


    obj = make_parser(move_object_name(), ObjectRelativeDirection.FORWARDS)
    pickupable = make_parser(pickupable_object_name(other_noun_response=None), ObjectRelativeDirection.VICINITY)

    return strongest([obj, pickupable])


def directional(default: Optional[MoveDirection] = None) -> Parser:
    """
    :return: a parser for directions, e.g. go left, right, forwards, backwards.
    """
    def combine_distance(dir: MoveDirection, dir_resp: Response) -> Parser:
        # Defaults to going medium distance.
        dist_parser = strongest([distance(), produce(Distance.MEDIUM, 0)])
        return dist_parser.map(lambda dist, _: (Directional(dir, dist), dir_resp))

    if default:
        dir = strongest([move_direction(), produce(default, 0)])
    else:
        dir = move_direction()

    return non_consuming(dir).then(combine_distance)


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

        return non_consuming(word_match(dir[0])) \
              .then_ignore(word_match(loc), combine) \
              .ignore_parsed(dir[1])

    # E.g. up stairs or down stairs, as opposed to upstairs or downstairs.
    separate_word_parsers = [make_parser(dir, loc) for dir, loc in itertools.product(directions, location_words)]

    # Only 'stairs' can be used without a direction, e.g. take the stairs. This is because 'take the floor' does not
    # make sense. None indicates that there is no direction.
    next_floor = word_match('next').then_ignore(word_match('floor'))
    stairs = word_match('stairs')
    no_direction_parser = strongest([next_floor, stairs]).ignore_parsed(None)

    upstairs = word_match('upstairs').ignore_parsed(FloorDirection.UP)
    downstairs = word_match('downstairs').ignore_parsed(FloorDirection.DOWN)

    up_correction_words = ['got', 'garden']
    up_corrections = strongest_word(up_correction_words) \
                     .ignore_then(stairs)\
                     .ignore_parsed(FloorDirection.UP)

    # All the parsers used to parse stairs.
    all_parsers = separate_word_parsers + [up_corrections, no_direction_parser, upstairs, downstairs]

    return strongest(all_parsers) \
          .map_parsed(lambda dir: Stairs(dir))


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
    dir = directional().map_response(lambda r: r*0.7)
    return strongest([end_of(), absolute(), positional(), dir, stairs(), behind()])
