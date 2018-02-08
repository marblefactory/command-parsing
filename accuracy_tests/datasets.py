import gspread
from oauth2client.service_account import ServiceAccountCredentials
from actions.move import *
from actions.location import *
from typing import List


class Dataset():
    """
    An object that has credentials to read Drive documents.
    """
    def __init__(self, creds_file='client_secret.json'):
        self.scope  = ['https://spreadsheets.google.com/feeds']
        self.creds  = ServiceAccountCredentials.from_json_keyfile_name(creds_file, self.scope)
        self.client = gspread.authorize(self.creds)

    def location_data(self) -> List[List[str]]:
        """
        :return: a list of answers for each question about locations.
        """
        # All the answers a single user provided.
        rows = self.client.open("MovementTrainingData").sheet1.get_all_records()
        # The rows after removing the first column, which is a timestamp.
        all_user_answers = [list(row.values())[1:] for row in rows]
        # All the answers for a question.
        question_answers = [[] for _ in range(19)]

        for user_answers in all_user_answers:
            for question_index, answer in enumerate(user_answers):
                if answer != '':
                    question_answers[question_index].append(answer.lower())

        return question_answers

    def location_question_targets(self) -> List[Move]:
        """
        :return: a list of targets for each question about locations. These can be used to check the performance of
                 the classifier on locations. The questions can be found here:
                    https://docs.google.com/forms/d/1aneFYVkj3aK3hPpsC0egHf0fFnNNhcNsxML5NM6GDMk/edit
        """

        locations = [
            # Scenario 1, 'go through the door in front of you'
            Positional('door', 0, MoveDirection.FORWARDS),

            # Scenario 2, 'take the first door on your right'
            Positional('door', 0, MoveDirection.RIGHT),

            # Scenario 3, 'take the first door on your right'
            Positional('door', 0, MoveDirection.RIGHT),

            # Scenario 4, 'go through the door on your right'
            Positional('door', 0, MoveDirection.RIGHT),

            # Scenario 5, 'go behind the desk'
            Behind('desk'),

            # Scenario 6, 'go through the door in front of you'
            Positional('door', 0, MoveDirection.FORWARDS),

            # Scenario 7, 'go around the corridor'
            None,

            # Scenario 8, 'take the first door on your left'
            Positional('door', 0, MoveDirection.LEFT),

            # Scenario 9, 'go to room 2 behind you'
            Positional('room', 0, MoveDirection.BACKWARDS),

            # Scenario 10, 'go to room 2'
            Absolute('room 2'),

            # Scenario 11, 'take the double doors on your left'
            Positional('door', 0, MoveDirection.LEFT),

            # Scenario 12, 'go upstairs'
            Stairs(FloorDirection.UP),

            # Scenario 13, 'go out of the room and then go through the next room on the right'
            None,

            # Scenario 14, 'go into the garden'
            None,

            # Scenario 15, 'go into the garden behind you'
            None,

            # Scenario 16, 'go behind the desk'
            Behind('desk'),

            # Scenario 17, 'go behind the sofas'
            Behind('sofas'),

            # Scenario 18, 'walk forwards a little bit'
            Directional(MoveDirection.FORWARDS),

            # Scenario 19, 'go into the boardroom'
            None
        ]

        moves: List[Move] = []
        for loc in locations:
            if loc is None:
                moves.append(None)
            else:
                moves.append(Move(Speed.NORMAL, loc, Stance.STAND))

        return moves
