import unittest
from parsing.pre_processing import pre_process
from parsing.parse_location import location, ordinal_number, move_direction, object_relative_direction, Parser, distance, description_number
from actions.location import *


class DistanceTestCase(unittest.TestCase):
    def test_short(self):
        s = pre_process('little')
        assert distance().parse(s).parsed == Distance.SHORT

    def test_medium(self):
        s = pre_process('fair')
        assert distance().parse(s).parsed == Distance.MEDIUM

    def test_far(self):
        s = pre_process('long')
        assert distance().parse(s).parsed == Distance.FAR


class OrdinalNumberTestCase(unittest.TestCase):
    def parser(self) -> Parser:
        return ordinal_number()

    def test_parses_ordinal_numbers(self):
        """
        Tests 'first', 'second', 'third', etc are parsed to their respective integers.
        """
        words = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth']

        for num, word in enumerate(words):
            s = pre_process(word)
            assert self.parser().parse(s).parsed == num

    def test_parses_sorry_as_three(self):
        s = pre_process('sorry')
        assert self.parser().parse(s).parsed == 3


class DescriptionNumberTestCase(OrdinalNumberTestCase):
    def parser(self) -> Parser:
        return description_number()

    def test_parses_next(self):
        """
        Tests 'next' is considered as an ordinal number.
        """
        s = pre_process('next')
        assert self.parser().parse(s).parsed == 0


class MoveDirectionTestCase(unittest.TestCase):
    def parser(self) -> Parser:
        return move_direction()

    def test_parses_forwards(self):
        s = pre_process('forwards')
        assert self.parser().parse(s).parsed == MoveDirection.FORWARDS

    def test_parses_front(self):
        s = pre_process('front')
        assert self.parser().parse(s).parsed == MoveDirection.FORWARDS

    def test_parses_backwards(self):
        s = pre_process('backwards')
        assert self.parser().parse(s).parsed == MoveDirection.BACKWARDS

    def test_parses_behind(self):
        s = pre_process('behind')
        assert self.parser().parse(s).parsed == MoveDirection.BACKWARDS

    def test_parses_left(self):
        s = pre_process('left')
        assert self.parser().parse(s).parsed == MoveDirection.LEFT

    def test_parses_right(self):
        s = pre_process('right')
        assert self.parser().parse(s).parsed == MoveDirection.RIGHT


class ObjectRelativeDirectionTestCase(MoveDirectionTestCase):
    def parser(self) -> Parser:
        return object_relative_direction()

    def test_parse_defaults_to_vicinity(self):
        s = pre_process('nan')
        assert self.parser().parse(s).parsed == ObjectRelativeDirection.VICINITY


class AbsoluteTestCase(unittest.TestCase):
    def test_parses_storage(self):
        s = pre_process('go to storage room 5')
        assert location().parse(s).parsed == Absolute('storage room 5')

    def test_parses_default_number(self):
        s = pre_process('go to the storage room')
        assert location().parse(s).parsed == Absolute('storage room 1')

    def test_parses_storage_no_room(self):
        s = pre_process('go to storage 5')
        assert location().parse(s).parsed == Absolute('storage room 5')

    def test_parses_storage_same_response(self):
        s1 = pre_process('go to storage 5')
        s2 = pre_process('go to storage room 5')

        r1 = location().parse(s1).response
        r2 = location().parse(s2).response

        assert r1 == r2

    def test_parses_office(self):
        s = pre_process('go to office 10')
        assert location().parse(s).parsed == Absolute('office 10')

    def test_parses_computer_lab(self):
        s = pre_process('go to computer lab 6')
        assert location().parse(s).parsed == Absolute('computer lab 6')

    def test_parses_lab(self):
        s = pre_process('go to lab 3')
        assert location().parse(s).parsed == Absolute('lab 3')

    def test_parses_live_as_lab(self):
        s = pre_process('go to live 3')
        assert location().parse(s).parsed == Absolute('lab 3')

    def test_parses_love_as_lab(self):
        s = pre_process('go to love 3')
        assert location().parse(s).parsed == Absolute('lab 3')

    def test_parses_meeting_room(self):
        s = pre_process('go to meeting room 89')
        assert location().parse(s).parsed == Absolute('meeting room 89')

    def test_parses_workshop(self):
        s = pre_process('go to workshop 2')
        assert location().parse(s).parsed == Absolute('workshop 2')

    def test_parses_server_room(self):
        s = pre_process('go to server room 78')
        assert location().parse(s).parsed == Absolute('server room 78')

    def test_parses_reception(self):
        s = pre_process('go to reception')
        assert location().parse(s).parsed == Absolute('reception')

    def test_parses_kitchen(self):
        s = pre_process('go to the kitchen')
        assert location().parse(s).parsed == Absolute('kitchen')

    def test_parses_gun_range(self):
        s = pre_process('go to the gun range')
        assert location().parse(s).parsed == Absolute('range')

    def test_parses_gun_range_same_response(self):
        s1 = pre_process('go to the range')
        s2 = pre_process('go to the gun range')

        r1 = location().parse(s1).response
        r2 = location().parse(s2).response

        assert r1 == r2

    def test_parses_mortuary(self):
        s = pre_process('go to the mortuary')
        assert location().parse(s).parsed == Absolute('mortuary')

    def test_parses_motor_as_mortuary(self):
        s = pre_process('go to the motor')
        assert location().parse(s).parsed == Absolute('mortuary')

    def test_parses_security_office(self):
        s = pre_process('go to the security office')
        assert location().parse(s).parsed == Absolute('security office')

    def test_parses_basement(self):
        s = pre_process('go to the basement')
        assert location().parse(s).parsed == Absolute('basement')

    def test_parses_floor_0_as_basement(self):
        s = pre_process('go to floor 0')
        assert location().parse(s).parsed == Absolute('basement')

    def test_parses_floor_zero_as_basement(self):
        s = pre_process('go to floor zero')
        assert location().parse(s).parsed == Absolute('basement')

    def test_parses_first_floor(self):
        s = pre_process('go to the first floor')
        assert location().parse(s).parsed == Absolute('roof')

    def test_fails_with_unknown_floor_num(self):
        s = pre_process('go to floor 100')
        assert location().parse(s).is_failure()

    def test_fails_with_unknown_ordinal_floor_num(self):
        s = pre_process('go to the ninth floor')
        assert location().parse(s).is_failure()

    def test_generator_room(self):
        s = pre_process('go to the generator room')
        assert location().parse(s).parsed == Absolute('generator room')

    def test_car_park(self):
        s = pre_process('go to the car park')
        assert location().parse(s).parsed == Absolute('car park')


class PositionalTestCase(unittest.TestCase):
    def test_parses(self):
        s = pre_process('on your left take the second door')
        assert location().parse(s).parsed == Positional('door', 1, MoveDirection.LEFT)

    def test_direction_default_forwards(self):
        s = pre_process('go to the third server')
        assert location().parse(s).parsed == Positional('server', 2, MoveDirection.FORWARDS)

    def test_ordinal_num_defaults_next(self):
        s = pre_process('go to the server on your right')
        assert location().parse(s).parsed == Positional('server', 0, MoveDirection.RIGHT)

    def test_parses_with_all_missing(self):
        s = pre_process('go to the door')
        assert location().parse(s).parsed == Positional('door', 0, MoveDirection.FORWARDS)

    def test_fails_if_missing_object(self):
        s = pre_process('go to the next on your right')
        assert type(location().parse(s)) is not Positional


class DirectionalTestCase(unittest.TestCase):
    def test_parses_left(self):
        s = pre_process('go left')
        assert location().parse(s).parsed == Directional(MoveDirection.LEFT, Distance.MEDIUM)

    def test_parses_right(self):
        s = pre_process('go right')
        assert location().parse(s).parsed == Directional(MoveDirection.RIGHT, Distance.MEDIUM)

    def test_parses_forwards(self):
        s = pre_process('go forwards')
        assert location().parse(s).parsed == Directional(MoveDirection.FORWARDS, Distance.MEDIUM)

    def test_parses_affords_as_forwards(self):
        s = pre_process('affords')
        assert location().parse(s).parsed == Directional(MoveDirection.FORWARDS, Distance.MEDIUM)

    def test_parses_backwards(self):
        s = pre_process('go backwards')
        assert location().parse(s).parsed == Directional(MoveDirection.BACKWARDS, Distance.MEDIUM)

    def test_parses_short(self):
        s = pre_process('go backwards a little bit')
        assert location().parse(s).parsed == Directional(MoveDirection.BACKWARDS, Distance.SHORT)

    def test_parses_medium(self):
        s = pre_process('go forwards a fair distance')
        assert location().parse(s).parsed == Directional(MoveDirection.FORWARDS, Distance.MEDIUM)

    def test_parses_far(self):
        s = pre_process('go forwards a long way')
        assert location().parse(s).parsed == Directional(MoveDirection.FORWARDS, Distance.FAR)

    def test_swapped_direction_and_distance(self):
        s = pre_process('go a long way forwards')
        assert location().parse(s).parsed == Directional(MoveDirection.FORWARDS, Distance.FAR)


class StairsTestCase(unittest.TestCase):
    def test_parses_up(self):
        s = pre_process('go up the stairs')
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_parses_upstairs(self):
        s = pre_process('go upstairs')
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_parses_down(self):
        s = pre_process('go down the stairs')
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)

    def test_parses_downstairs(self):
        s = pre_process('go downstairs')
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)

    def test_parses_up_floor(self):
        s = pre_process('go up a floor')
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_parses_down_floor(self):
        s = pre_process('go down a floor')
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)

    def test_parses_no_direction(self):
        """
        This allowed the game to decide which direction the spy should go in.
        """
        s = pre_process('stairs')
        assert location().parse(s).parsed == Stairs(direction=None)

    def test_next_floor(self):
        s = pre_process('go to the next floor')
        assert location().parse(s).parsed == Stairs(direction=None)

    def test_next_floor_up(self):
        s = pre_process('go to the next floor up')
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_next_floor_down(self):
        s = pre_process('go to the next floor down')
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)

    def test_fails_if_just_floor(self):
        s = pre_process('floor')
        assert location().parse(s).is_failure()

    def test_fails_if_just_up(self):
        s = pre_process('go up')
        assert location().parse(s).is_failure()

    def test_fails_if_just_down(self):
        s = pre_process('go down')
        assert location().parse(s).is_failure()


class BehindTestCase(unittest.TestCase):
    def test_behind(self):
        s = pre_process('go behind the desk')
        assert location().parse(s).parsed == Behind('desk')

    def test_around(self):
        s = pre_process('go around the server')
        assert location().parse(s).parsed == Behind('server')

    def test_fails_if_missing_object(self):
        s = pre_process('go around the')
        assert location().parse(s).is_failure()

    def test_other_side(self):
        s = pre_process('go to the other side of the table')
        assert location().parse(s).parsed == Behind('table')

    def test_fails_if_side_other_incorrect_order(self):
        s = pre_process('go to the side other of the table')
        assert type(location().parse(s).parsed) is not Behind


class EndOfTestCase(unittest.TestCase):
    def test_parse_room(self):
        s = pre_process('go to the end of the room')
        assert location().parse(s).parsed == EndOf('room')

    def test_parse_corridor(self):
        s = pre_process('go to the end of the corridor')
        assert location().parse(s).parsed == EndOf('corridor')

    def test_parse_absolute(self):
        s = pre_process('go to the end of the gun range')
        assert location().parse(s).parsed == EndOf('range')
