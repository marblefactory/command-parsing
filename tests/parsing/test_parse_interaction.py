import unittest
from parsing.pre_processing import pre_process
from parsing.parse_action import statement
from actions.interaction import *
from actions.location import *


class PickUpTestCase(unittest.TestCase):
    def test_parse_pick_up(self):
        s = pre_process('pick up the rock on your left')
        assert statement().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.LEFT)

    def test_parse_take(self):
        s = pre_process('take the rock on your left')
        assert statement().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.LEFT)

    def test_tape_as_take(self):
        s = pre_process('tape the rock')
        assert statement().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.VICINITY)

    def test_get(self):
        s = pre_process('get the bottle')
        r = statement().parse(s).parsed
        self.assertEqual(r, PickUp('bottle', ObjectRelativeDirection.VICINITY))

    def test_direction_defaults_to_vicinity(self):
        s = pre_process('pick up the hammer')
        assert statement().parse(s).parsed == PickUp('hammer', ObjectRelativeDirection.VICINITY)

    def test_take_fails_if_no_object1(self):
        s = pre_process('take the on your left')
        assert type(statement().parse(s)) != PickUp

    def test_pick_up_partial_if_no_object1(self):
        # Tests that a partial is returned asking for more information if the object name is not given.
        s = pre_process('pick up')
        result = statement().parse(s)
        self.assertEqual(result.marker, PickUp)

    def test_take_is_partial(self):
        # Tests that a partial is returned if you say 'take'.
        s = pre_process('take')
        r = statement().parse(s)
        self.assertEqual(r.marker, PickUp)

    def test_ra_as_rock(self):
        s = pre_process('pick up the ra')
        assert statement().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.VICINITY)

    def test_parses_noun(self):
        """
        Tests that other nouns that haven't been explicitly listed can also be recognised.
        """
        s = pre_process('pick up the phone')
        r = statement().parse(s).parsed
        self.assertEqual(r, PickUp('phone', ObjectRelativeDirection.VICINITY))

    def test_parses_noun_lower_response(self):
        """
        Tests that although other nouns can be recognised, they have a lower response than objects in the game.
        """
        real_obj_s = pre_process('pick up the rock')
        fake_obj_s = pre_process('pick up the phone')

        real_r = statement().parse(real_obj_s)
        fake_r = statement().parse(fake_obj_s)

        assert fake_r.response < real_r.response

    def test_parses_rocket_as_rock(self):
        s = pre_process('pick up the rocket')
        assert statement().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.VICINITY)

    def test_picks_up_if_only_object_name(self):
        s = pre_process('the rock')
        assert statement().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.VICINITY)

    def test_only_object_name_with_direction(self):
        s = pre_process('the rock on the left')
        assert statement().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.LEFT)


class ThrowTestCase(unittest.TestCase):
    def test_parse_directional(self):
        s = pre_process('chuck the rock to your left')

        expected_loc = Directional(MoveDirection.LEFT, Distance.MEDIUM)
        assert statement().parse(s).parsed == Throw(expected_loc)

    def test_parse_positional(self):
        s = pre_process('throw the rock to the next door')

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert statement().parse(s).parsed == Throw(expected_loc)

    def test_throw_behind_object(self):
        s = pre_process('throw the hammer behind the desk')
        assert statement().parse(s).parsed == Throw(Behind('desk'))

    def test_defaults_forwards(self):
        s = pre_process('throw the rock')

        expected_loc = Directional(MoveDirection.FORWARDS, Distance.MEDIUM)
        assert statement().parse(s).parsed == Throw(expected_loc)

    def test_show_as_throw(self):
        s = pre_process('show the rock')

        expected_loc = Directional(MoveDirection.FORWARDS, Distance.MEDIUM)
        assert statement().parse(s).parsed == Throw(expected_loc)

    def test_through_as_throw(self):
        s = pre_process('through the rock')

        expected_loc = Directional(MoveDirection.FORWARDS, Distance.MEDIUM)
        assert statement().parse(s).parsed == Throw(expected_loc)

    def test_fails_if_no_object(self):
        s = pre_process('throw')
        assert type(statement().parse(s)) != Throw

    def test_shut_as_chuck(self):
        s = pre_process('shut the rock')
        assert statement().parse(s).parsed == Throw(Directional(MoveDirection.FORWARDS, Distance.MEDIUM))

    def test_left_long_distance(self):
        s = pre_process('throw the rock left a long way')
        r = statement().parse(s).parsed
        self.assertEqual(r, Throw(Directional(MoveDirection.LEFT, Distance.FAR)))

    def test_short_distance(self):
        s = pre_process('throw the rock a little way')
        assert statement().parse(s).parsed == Throw(Directional(MoveDirection.FORWARDS, Distance.SHORT))

    def test_long_distance(self):
        s = pre_process('throw the rock a long way')
        assert statement().parse(s).parsed == Throw(Directional(MoveDirection.FORWARDS, Distance.FAR))

    def test_throw_backwards(self):
        s = pre_process('throw the bottle backwards')
        assert statement().parse(s).parsed == Throw(Directional(MoveDirection.BACKWARDS, Distance.MEDIUM))

    def test_grow_as_throw(self):
        s = pre_process('grow the rock')
        self.assertEqual(statement().parse(s).parsed, Throw(Directional(MoveDirection.FORWARDS, Distance.MEDIUM)))


class ThrowAtGuardTestCase(unittest.TestCase):
    def test_throw_at_guard(self):
        s = pre_process('throw at the guard')
        assert statement().parse(s).parsed == ThrowAtGuard(ObjectRelativeDirection.VICINITY)

    def test_direction(self):
        s = pre_process('chuck at the enemy on your left')
        assert statement().parse(s).parsed == ThrowAtGuard(ObjectRelativeDirection.LEFT)

    def test_shut_as_chuck(self):
        s = pre_process('shut the rock at the guard')
        assert statement().parse(s).parsed == ThrowAtGuard(ObjectRelativeDirection.VICINITY)

    def test_security(self):
        s = pre_process('throw at the security')
        assert statement().parse(s).parsed == ThrowAtGuard(ObjectRelativeDirection.VICINITY)

    def test_card(self):
        s = pre_process('throw at the card')
        r = statement().parse(s).parsed
        self.assertEqual(r, ThrowAtGuard(ObjectRelativeDirection.VICINITY))

    def test_god(self):
        s = pre_process('throw at the god')
        r = statement().parse(s).parsed
        self.assertEqual(r, ThrowAtGuard(ObjectRelativeDirection.VICINITY))

    def test_aids(self):
        s = pre_process('throw at the aids')
        r = statement().parse(s).parsed
        self.assertEqual(r, ThrowAtGuard(ObjectRelativeDirection.VICINITY))

    def test_jobs(self):
        s = pre_process('throw at the jobs')
        r = statement().parse(s).parsed
        self.assertEqual(r, ThrowAtGuard(ObjectRelativeDirection.VICINITY))

    def test_car(self):
        s = pre_process('throw at the car')
        r = statement().parse(s).parsed
        self.assertEqual(r, ThrowAtGuard(ObjectRelativeDirection.VICINITY))

    def test_dogs(self):
        s = pre_process('throw at the dogs')
        r = statement().parse(s).parsed
        self.assertEqual(r, ThrowAtGuard(ObjectRelativeDirection.VICINITY))

    def test_ga(self):
        s = pre_process('throw at the ga')
        r = statement().parse(s).parsed
        self.assertEqual(r, ThrowAtGuard(ObjectRelativeDirection.VICINITY))

    def test_girl(self):
        s = pre_process('throw at the girl')
        r = statement().parse(s).parsed
        self.assertEqual(r, ThrowAtGuard(ObjectRelativeDirection.VICINITY))

    def test_good(self):
        s = pre_process('throw at the good')
        r = statement().parse(s).parsed
        self.assertEqual(r, ThrowAtGuard(ObjectRelativeDirection.VICINITY))

class StrangleGuardTestCase(unittest.TestCase):
    def test_strangle(self):
        s = pre_process('strangle the guard')
        assert statement().parse(s).parsed == StrangleGuard(ObjectRelativeDirection.VICINITY)

    def test_strangle_direction(self):
        s = pre_process('strangle the guard on your left')
        assert statement().parse(s).parsed == StrangleGuard(ObjectRelativeDirection.LEFT)


class AutoTakeOutGuardTestCase(unittest.TestCase):
    def test_kill(self):
        s = pre_process('kill the guard')
        assert statement().parse(s).parsed == AutoTakeOutGuard(ObjectRelativeDirection.VICINITY)

    def test_knock_out(self):
        s = pre_process('knock out the guard')
        assert statement().parse(s).parsed == AutoTakeOutGuard(ObjectRelativeDirection.VICINITY)

    def test_take_out(self):
        s = pre_process('take out the guard')
        assert statement().parse(s).parsed == AutoTakeOutGuard(ObjectRelativeDirection.VICINITY)

    def test_direction(self):
        s = pre_process('take out the guard behind you')
        assert statement().parse(s).parsed == AutoTakeOutGuard(ObjectRelativeDirection.BACKWARDS)

    def test_take_guard_out(self):
        s = pre_process('take the guard out')
        assert statement().parse(s).parsed == AutoTakeOutGuard(ObjectRelativeDirection.VICINITY)

    def test_attack_guard(self):
        s = pre_process('attack the guard')
        r = statement().parse(s).parsed
        self.assertTrue(r, AutoTakeOutGuard(ObjectRelativeDirection.VICINITY))

    def test_security(self):
        s = pre_process('attack the security')
        assert statement().parse(s).parsed == AutoTakeOutGuard(ObjectRelativeDirection.VICINITY)

    def test_hildegard(self):
        s = pre_process('hildegard')
        assert statement().parse(s).parsed == AutoTakeOutGuard(ObjectRelativeDirection.VICINITY)

    def test_kildegaard(self):
        s = pre_process('kildegaard')
        r = statement().parse(s).parsed
        self.assertEqual(r, AutoTakeOutGuard(ObjectRelativeDirection.VICINITY))

    def test_waste_him(self):
        s = pre_process('waste him')
        assert statement().parse(s).parsed == AutoTakeOutGuard(ObjectRelativeDirection.VICINITY)

    def test_keel_as_kill(self):
        s = pre_process('keel him')
        assert statement().parse(s).parsed == AutoTakeOutGuard(ObjectRelativeDirection.VICINITY)

    def test_man(self):
        s = pre_process('kill the man in front of you')
        r = statement().parse(s).parsed
        self.assertEqual(r, AutoTakeOutGuard(ObjectRelativeDirection.FORWARDS))

    def test_tear_apart(self):
        s = pre_process('tear him apart')
        self.assertEqual(statement().parse(s).parsed, AutoTakeOutGuard(ObjectRelativeDirection.VICINITY))

    def test_mother_fucker(self):
        s = pre_process('kill that mother f*****')
        self.assertEqual(statement().parse(s).parsed, AutoTakeOutGuard(ObjectRelativeDirection.VICINITY))

    def test_girl_as_guard(self):
        s = pre_process('kill the girl')
        self.assertEqual(statement().parse(s).parsed, AutoTakeOutGuard(ObjectRelativeDirection.VICINITY))

    def test_text_as_attack(self):
        s = pre_process('text the guard')
        result = statement().parse(s).parsed
        self.assertEqual(result, AutoTakeOutGuard(ObjectRelativeDirection.VICINITY))

    def test_fights_the_guard(self):
        s = pre_process('fights the guard')
        result = statement().parse(s).parsed
        self.assertEqual(result, AutoTakeOutGuard(ObjectRelativeDirection.VICINITY))


class DropTestCase(unittest.TestCase):
    def test_drop(self):
        s = pre_process('drop the rock')
        assert statement().parse(s).parsed == Drop()

    def test_put_down(self):
        s = pre_process('put down the rock')
        assert statement().parse(s).parsed == Drop()

    def test_place(self):
        s = pre_process('place the rock')
        assert statement().parse(s).parsed == Drop()

    def test_in(self):
        s = pre_process('place the rock in front of you')
        assert statement().parse(s).parsed == Drop()


class HackTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('hack the terminal on your left')
        assert statement().parse(s).parsed == Hack('terminal', ObjectRelativeDirection.LEFT)

    def test_direction_defaults_to_vicinity(self):
        s = pre_process('hack the terminal')
        assert statement().parse(s).parsed == Hack('terminal', ObjectRelativeDirection.VICINITY)

    def test_hacked_as_hack(self):
        s = pre_process('hacked the computer')
        assert statement().parse(s).parsed == Hack('computer', ObjectRelativeDirection.VICINITY)

    def test_have_as_hack(self):
        s = pre_process('have the console')
        self.assertEqual(statement().parse(s).parsed, Hack('console', ObjectRelativeDirection.VICINITY))

    def test_text_as_hack(self):
        # Because speech recognition mistakes 'hack' as 'text'
        s = pre_process('text the server')
        assert statement().parse(s).parsed == Hack('server', ObjectRelativeDirection.VICINITY)

    def test_hack_into(self):
        s = pre_process('hack into a computer')
        assert statement().parse(s).parsed == Hack('computer', ObjectRelativeDirection.VICINITY)

    def test_log_into(self):
        s = pre_process('log into the computer')
        assert statement().parse(s).parsed == Hack('computer', ObjectRelativeDirection.VICINITY)

    def test_break_into(self):
        s = pre_process('break into the server')
        assert statement().parse(s).parsed == Hack('server', ObjectRelativeDirection.VICINITY)

    def test_breaking(self):
        s = pre_process('breaking the mainframe')
        assert statement().parse(s).parsed == Hack('mainframe', ObjectRelativeDirection.VICINITY)

    def test_attack(self):
        s = pre_process('attack their server')
        assert statement().parse(s).parsed == Hack('server', ObjectRelativeDirection.VICINITY)

    def test_partial_if_no_object1(self):
        s = pre_process('hack')
        result = statement().parse(s)
        self.assertEqual(result.marker, Hack)

    def test_partial_if_no_object2(self):
        s = pre_process('hack something')
        result = statement().parse(s)
        assert result.marker == Hack

    def test_at_as_hack(self):
        s = pre_process('at their server')
        assert statement().parse(s).parsed == Hack('server', ObjectRelativeDirection.VICINITY)

    def test_actor_as_hack(self):
        s = pre_process('actor terminal')
        assert statement().parse(s).parsed == Hack('terminal', ObjectRelativeDirection.VICINITY)

    def test_just_terminal(self):
        s = pre_process('terminal')
        assert statement().parse(s).parsed == Hack('terminal', ObjectRelativeDirection.VICINITY)

    def test_hyperterminal(self):
        s = pre_process('hyperterminal')
        result = statement().parse(s).parsed
        self.assertEqual(result, Hack('terminal', ObjectRelativeDirection.VICINITY))

    def test_hyperterminal_with_direction(self):
        s = pre_process('hyperterminal on your left')
        result = statement().parse(s).parsed
        self.assertEqual(result, Hack('terminal', ObjectRelativeDirection.LEFT))

    def test_criminal_as_terminal(self):
        s = pre_process('hack the criminal')
        r = statement().parse(s).parsed
        self.assertEqual(r, Hack('terminal', ObjectRelativeDirection.VICINITY))

    def test_determinant_as_terminal(self):
        s = pre_process('hack the determinant')
        r = statement().parse(s).parsed
        self.assertEqual(r, Hack('terminal', ObjectRelativeDirection.VICINITY))

    def test_determine_as_terminal(self):
        s = pre_process('hack the determine')
        r = statement().parse(s).parsed
        self.assertEqual(r, Hack('terminal', ObjectRelativeDirection.VICINITY))

    def test_determiners_as_terminal(self):
        s = pre_process('hack the determiners')
        r = statement().parse(s).parsed
        self.assertEqual(r, Hack('terminal', ObjectRelativeDirection.VICINITY))


class PickpocketTestCase(unittest.TestCase):
    def test_parse_pickpocket(self):
        s = pre_process('pickpocket the guard')
        assert statement().parse(s).parsed == Pickpocket(ObjectRelativeDirection.VICINITY)

    def test_parse_steal(self):
        s = pre_process('steal from the guard')
        assert statement().parse(s).parsed == Pickpocket(ObjectRelativeDirection.VICINITY)

    def test_parse_direction(self):
        s = pre_process('take from the guard behind you')
        assert statement().parse(s).parsed == Pickpocket(ObjectRelativeDirection.BACKWARDS)

    def test_parse_take(self):
        s = pre_process('take from the guard')
        assert statement().parse(s).parsed == Pickpocket(ObjectRelativeDirection.VICINITY)

    def test_parse_take_object(self):
        s = pre_process('take the rock from the guard')
        assert statement().parse(s).parsed == Pickpocket(ObjectRelativeDirection.VICINITY)

    def test_security(self):
        s = pre_process('pickpocket the security')
        assert statement().parse(s).parsed == Pickpocket(ObjectRelativeDirection.VICINITY)


class DestroyGeneratorTestCase(unittest.TestCase):
    def test_parse_destroy(self):
        s = pre_process('destroy the generator')
        assert statement().parse(s).parsed == DestroyGenerator()

    def test_parse_take_out(self):
        s = pre_process('take out the generator')
        assert statement().parse(s).parsed == DestroyGenerator()

    def test_take_generator_out(self):
        s = pre_process('take the generator out')
        assert statement().parse(s).parsed == DestroyGenerator()

    def test_parse_kill(self):
        s = pre_process('kill the generator')
        assert statement().parse(s).parsed == DestroyGenerator()

    def test_parse_attack(self):
        s = pre_process('attack the generator')
        assert statement().parse(s).parsed == DestroyGenerator()
