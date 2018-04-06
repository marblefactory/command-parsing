import unittest
from parsing.pre_processing import pre_process
from parsing.parse_conversation import player_name


class PlayerNameTestCase(unittest.TestCase):
    def test_parse_just_name(self):
        s = pre_process('brian')
        assert player_name().parse(s).parsed == 'brian'

    def test_parse_name_is(self):
        s = pre_process('my name is dave')
        assert player_name().parse(s).parsed == 'dave'

    def test_parse_i_am(self):
        s = pre_process('i am jane')
        assert player_name().parse(s).parsed == 'jane'

    def test_parse_marker_names(self):
        """
        Tests that the parser works for the names of all the game markers.
        """
        names = ['Neill', 'Aisling', 'Conor', 'Carl', 'Ian', 'Tilo', 'Beth', 'Richard']
        for name in names:
            s = pre_process(name)
            assert player_name().parse(s).parsed == name.lower()
