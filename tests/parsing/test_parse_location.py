import unittest
from parsing.pre_processing import pre_process
from parsing.parse_location import ordinal_number, move_direction, object_relative_direction, Parser, distance, description_number
from parsing.parse_action import statement
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
        assert statement().parse(s).parsed.location == Absolute('storage 5')

    def test_parses_storage_no_room(self):
        s = pre_process('go to storage 5')
        assert statement().parse(s).parsed.location == Absolute('storage 5')

    def test_parses_office(self):
        s = pre_process('go to office 10')
        assert statement().parse(s).parsed.location == Absolute('office 10')

    def test_parses_computer_lab(self):
        s = pre_process('go to computer lab 6')
        assert statement().parse(s).parsed.location == Absolute('computer lab 6')

    def test_parses_lab(self):
        s = pre_process('go to lab 3')
        assert statement().parse(s).parsed.location == Absolute('lab 3')

    def test_parses_live_as_lab(self):
        s = pre_process('go to live 3')
        assert statement().parse(s).parsed.location == Absolute('lab 3')

    def test_parses_love_as_lab(self):
        s = pre_process('go to love one')
        assert statement().parse(s).parsed.location == Absolute('lab 1')

    def test_parses_loved_as_lab(self):
        s = pre_process('go to loved 1')
        r = statement().parse(s).parsed
        self.assertEqual(r.location, Absolute('lab 1'))

    def test_parses_luck_as_lab(self):
        s = pre_process('go to luck 3')
        r = statement().parse(s).parsed
        self.assertEqual(r.location, Absolute('lab 3'))

    def test_app_as_lab(self):
        s = pre_process('go to app 2')
        r = statement().parse(s).parsed.location
        self.assertEqual(r, Absolute('lab 2'))

    def test_lap_as_lab(self):
        s = pre_process('go to lap 3')
        r = statement().parse(s).parsed.location
        self.assertEqual(r, Absolute('lab 3'))

    def test_parses_meeting_room(self):
        s = pre_process('go to meeting room 89')
        assert statement().parse(s).parsed.location == Absolute('meeting room 89')

    def test_parses_workshop(self):
        s = pre_process('go to workshop 2')
        assert statement().parse(s).parsed.location == Absolute('workshop 2')

    def test_parses_server_room(self):
        s = pre_process('go to server room 78')
        assert statement().parse(s).parsed.location == Absolute('server room 78')

    def test_parses_server(self):
        s = pre_process('go to server in one')
        r = statement().parse(s).parsed[0].location
        self.assertEqual(r, Absolute('server room 1'))

    def test_parses_server_at(self):
        s = pre_process('go to server room at 2')
        r = statement().parse(s).parsed
        self.assertEqual(r.location, Absolute('server room 2'))

    def test_parses_reception(self):
        s = pre_process('go to reception')
        assert statement().parse(s).parsed.location == Absolute('reception')

    def test_parses_kitchen(self):
        s = pre_process('go to the kitchen')
        assert statement().parse(s).parsed.location == Absolute('kitchen')

    def test_parses_kit_as_kitchen(self):
        s = pre_process('go to the kit')
        assert statement().parse(s).parsed.location == Absolute('kitchen')

    def test_parses_gun_range(self):
        s = pre_process('go to the gun range')
        assert statement().parse(s).parsed.location == Absolute('gun range')

    def test_parses_garage_as_gun_range(self):
        s = pre_process('go to the garage')
        assert statement().parse(s).parsed.location == Absolute('gun range')

    def test_parses_mortuary(self):
        s = pre_process('go to the mortuary')
        assert statement().parse(s).parsed.location == Absolute('mortuary')

    def test_parses_motor_as_mortuary(self):
        s = pre_process('go to the motor')
        assert statement().parse(s).parsed.location == Absolute('mortuary')

    def test_parse_security(self):
        s = pre_process('go to security')
        assert statement().parse(s).parsed.location == Absolute('security room')

    def test_parses_security_office(self):
        s = pre_process('go to the security office')
        assert statement().parse(s).parsed.location == Absolute('security room')

    def test_parses_basement(self):
        s = pre_process('go to the basement')
        assert statement().parse(s).parsed.location == Absolute('basement')

    def test_parses_floor_0_as_basement(self):
        s = pre_process('go to floor 0')
        assert statement().parse(s).parsed.location == Absolute('basement')

    def test_parses_floor_zero_as_basement(self):
        s = pre_process('go to floor zero')
        assert statement().parse(s).parsed.location == Absolute('basement')

    def test_parses_first_floor(self):
        s = pre_process('go to the first floor')
        assert statement().parse(s).parsed.location == Absolute('roof')

    def test_fails_with_unknown_floor_num(self):
        s = pre_process('go to floor 100')
        r = statement().parse(s)
        self.assertFalse(r.is_success())

    def test_fails_with_unknown_ordinal_floor_num(self):
        s = pre_process('go to the ninth floor')
        assert not statement().parse(s).is_success()

    def test_generator_room(self):
        s = pre_process('go to the generator room')
        assert statement().parse(s).parsed.location == Absolute('generator room')

    def test_car_park(self):
        s = pre_process('go to the car park')
        assert statement().parse(s).parsed.location == Absolute('car park')

    def test_toilet(self):
        s = pre_process('go to toilet 2')
        assert statement().parse(s).parsed.location == Absolute('toilet 2')

    def test_level(self):
        s = pre_process('go to level 0')
        assert statement().parse(s).parsed.location == Absolute('basement')


class PositionalTestCase(unittest.TestCase):
    def test_parses(self):
        s = pre_process('on your left take the second door')
        r = statement().parse(s).parsed
        self.assertEqual(r.location, Positional('door', 1, MoveDirection.LEFT))

    def test_direction_default_forwards(self):
        s = pre_process('go to the third desk')
        assert statement().parse(s).parsed.location == Positional('desk', 2, MoveDirection.FORWARDS)

    def test_ordinal_num_defaults_next(self):
        s = pre_process('go to the desk on your right')
        assert statement().parse(s).parsed.location == Positional('desk', 0, MoveDirection.RIGHT)

    def test_parses_with_all_missing(self):
        s = pre_process('go to the door')
        assert statement().parse(s).parsed.location == Positional('door', 0, MoveDirection.FORWARDS)

    def test_fails_if_missing_object(self):
        s = pre_process('go to the next on your right')
        assert type(statement().parse(s).parsed.location) is not Positional


class DirectionalTestCase(unittest.TestCase):
    def test_parses_left(self):
        s = pre_process('go left')
        assert statement().parse(s).parsed.location == Directional(MoveDirection.LEFT, Distance.MEDIUM)

    def test_parses_right(self):
        s = pre_process('go right')
        assert statement().parse(s).parsed.location == Directional(MoveDirection.RIGHT, Distance.MEDIUM)

    def test_parses_forwards(self):
        s = pre_process('go forwards')
        assert statement().parse(s).parsed.location == Directional(MoveDirection.FORWARDS, Distance.MEDIUM)

    def test_parses_affords_as_forwards(self):
        s = pre_process('affords')
        assert statement().parse(s).parsed.location == Directional(MoveDirection.FORWARDS, Distance.MEDIUM)

    def test_parses_backwards(self):
        s = pre_process('go backwards')
        assert statement().parse(s).parsed.location == Directional(MoveDirection.BACKWARDS, Distance.MEDIUM)

    def test_parses_short(self):
        s = pre_process('go backwards a little bit')
        assert statement().parse(s).parsed.location == Directional(MoveDirection.BACKWARDS, Distance.SHORT)

    def test_parses_medium(self):
        s = pre_process('go forwards a fair distance')
        assert statement().parse(s).parsed.location == Directional(MoveDirection.FORWARDS, Distance.MEDIUM)

    def test_parses_far(self):
        s = pre_process('go forwards a long way')
        r = statement().parse(s).parsed
        self.assertEqual(r.location, Directional(MoveDirection.FORWARDS, Distance.FAR))

    def test_swapped_direction_and_distance(self):
        s = pre_process('go a long way forwards')
        assert statement().parse(s).parsed.location == Directional(MoveDirection.FORWARDS, Distance.FAR)

    def test_ride_as_right(self):
        s = pre_process('go ride')
        r = statement().parse(s).parsed
        print(r)
        self.assertEqual(r.location, Directional(MoveDirection.RIGHT, Distance.MEDIUM))

    def test_alright_as_right(self):
        s = pre_process('go alright')
        r = statement().parse(s).parsed
        self.assertEqual(r.location, Directional(MoveDirection.RIGHT, Distance.MEDIUM))


class StairsTestCase(unittest.TestCase):
    def test_parses_up(self):
        s = pre_process('go up the stairs')
        assert statement().parse(s).parsed.location == Stairs(FloorDirection.UP)

    def test_parses_upstairs(self):
        s = pre_process('go upstairs')
        assert statement().parse(s).parsed.location == Stairs(FloorDirection.UP)

    def test_parses_down(self):
        s = pre_process('go down the stairs')
        assert statement().parse(s).parsed.location == Stairs(FloorDirection.DOWN)

    def test_parses_downstairs(self):
        s = pre_process('go downstairs')
        assert statement().parse(s).parsed.location == Stairs(FloorDirection.DOWN)

    def test_parses_up_floor(self):
        s = pre_process('go up a floor')
        assert statement().parse(s).parsed.location == Stairs(FloorDirection.UP)

    def test_parses_down_floor(self):
        s = pre_process('go down a floor')
        assert statement().parse(s).parsed.location == Stairs(FloorDirection.DOWN)

    def test_parses_no_direction(self):
        """
        This allowed the game to decide which direction the spy should go in.
        """
        s = pre_process('stairs')
        assert statement().parse(s).parsed.location == Stairs(direction=None)

    def test_next_floor(self):
        s = pre_process('go to the next floor')
        assert statement().parse(s).parsed.location == Stairs(direction=None)

    def test_next_floor_up(self):
        s = pre_process('go to the next floor up')
        assert statement().parse(s).parsed.location == Stairs(FloorDirection.UP)

    def test_next_floor_down(self):
        s = pre_process('go to the next floor down')
        assert statement().parse(s).parsed.location == Stairs(FloorDirection.DOWN)

    def test_fails_if_just_floor(self):
        s = pre_process('floor')
        assert statement().parse(s).is_failure()

    def test_fails_if_just_up(self):
        s = pre_process('go up')
        assert not statement().parse(s).is_success()

    def test_fails_if_just_down(self):
        s = pre_process('go down')
        assert not statement().parse(s).is_success()

    def test_got_as_up(self):
        s = pre_process('got the stairs')
        self.assertEqual(statement().parse(s).parsed.location, Stairs(FloorDirection.UP))

    def test_garden_as_go_up(self):
        s = pre_process('garden the stairs')
        self.assertEqual(statement().parse(s).parsed.location, Stairs(FloorDirection.UP))


class BehindTestCase(unittest.TestCase):
    def test_behind(self):
        s = pre_process('go behind the desk')
        assert statement().parse(s).parsed.location == Behind('desk')

    def test_around(self):
        s = pre_process('go around the desk')
        assert statement().parse(s).parsed.location == Behind('desk')

    def test_other_side(self):
        s = pre_process('go to the other side of the table')
        r = statement().parse(s).parsed
        self.assertEqual(r.location, Behind('table'))


class EndOfTestCase(unittest.TestCase):
    def test_parse_room(self):
        s = pre_process('go to the end of the room')
        assert statement().parse(s).parsed.location == EndOf('room')

    def test_parse_corridor(self):
        s = pre_process('go to the end of the corridor')
        assert statement().parse(s).parsed.location == EndOf('corridor')

    def test_parse_absolute(self):
        s = pre_process('go to the end of the gun range')
        assert statement().parse(s).parsed.location == EndOf('gun range')
