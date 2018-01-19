import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List
import numpy as np


class Dataset():
    """
    An object that has cridentials to read Drive documents.
    """
    def __init__(self, credsFile='client_secret.json'):
        self.scope  = ['https://spreadsheets.google.com/feeds']
        self.creds  = ServiceAccountCredentials.from_json_keyfile_name(credsFile, self.scope)
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

    def location_ideal_answers(self) -> List[str]:
        """
        :return: an ideal answer for each question.
        """
        return [
            # Scenario 1
            'go through the door in front of you',
            # Scenario 2
            'take the first door on your right',
            # Scenario 3
            'take the first door on your right',
            # Scenario 4
            'go through the door on your right',
            # Scenario 5
            'go behind the desk',
            # Scenario 6
            'go through the door in front of you then turn left',
            # Scenario 7
            'go around the corridor',
            # Scenario 8
            'take the first door on your left',
            # Scenario 9
            'go to room 2 behind you',
            # Scenario 10
            'go to room 2',
            # Scenario 11
            'take the double doors on your left',
            # Scenario 12
            'go upstairs',
            # Scenario 13
            'go out of the room and then go through the next room on the right',
            # Scenario 14
            'go into the garden',
            # Scenario 15
            'go into the garden behind you',
            # Scenario 16
            'go behind the desk',
            # Scenario 17
            'go behind the sofas',
            # Scenario 18
            'walk forwards a little bit',
            # Scenario 19
            'go into the boardroom'
        ]

    def location_question_targets(self) -> List[np.array]:
        """
        :return: a list of targets for each question about locations. These can be used to check the performance of
                 the classifier on locations. The questions can be found here:
                    https://docs.google.com/forms/d/1aneFYVkj3aK3hPpsC0egHf0fFnNNhcNsxML5NM6GDMk/edit
        """


        # Vectors are in the form:
        # [ Absolute    ] e.g. Go to room 201
        # [ Contextual  ] e.g. Take the door behind you
        # [ Directional ] e.g. Go forwards a little bit
        # [ Stairs      ] e.g. Go downstairs
        # [ Behind      ] e.g. Go behind the sofas

        vectors = [
            # Scenario 1, 'go through the door in front of you'
            [0, 1, 0, 0, 0],

            # Scenario 2, 'take the first door on your right'
            [0, 1, 0, 0, 0],

            # Scenario 3, 'take the first door on your right'
            [0, 1, 0, 0, 0],

            # Scenario 4, 'go through the door on your right'
            [0, 1, 0, 0, 0],

            # Scenario 5, 'go behind the desk'
            [0, 0, 0, 0, 1],

            # Scenario 6, 'go through the door in front of you then turn left'
            [0, 1, 0, 0, 0],

            # Scenario 7, 'go around the corridor'
            [0, 1, 0, 0, 0],

            # Scenario 8, 'take the first door on your left'
            [0, 1, 0, 0, 0],

            # Scenario 9, 'go to room 2 behind you'
            [1, 0, 0, 0, 0],

            # Scenario 10, 'go to room 2'
            [1, 0, 0, 0, 0],

            # Scenario 11, 'take the double doors on your left'
            [0, 1, 0, 0, 0],

            # Scenario 12, 'go upstairs'
            [0, 0, 0, 1, 0],

            # Scenario 13, 'go out of the room and then go through the next room on the right'
            [0, 1, 0, 0, 0],

            # Scenario 14, 'go into the garden'
            [1, 0, 0, 0, 0],

            # Scenario 15, 'go into the garden behind you'
            [1, 0, 0, 0, 0],

            # Scenario 16, 'go behind the desk'
            [0, 0, 0, 0, 1],

            # Scenario 17, 'go behind the sofas'
            [0, 0, 0, 0, 1],

            # Scenario 18, 'walk forwards a little bit'
            [0, 1, 0, 0, 0],

            # Scenario 19, 'go into the boardroom'
            [1, 0, 0, 0, 0],
        ]

        return [np.array(vec) for vec in vectors]
