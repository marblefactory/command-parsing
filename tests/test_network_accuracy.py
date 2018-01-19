from datasets import Dataset
from networks import LocationNN
import numpy as np
from typing import List
from collections import Counter


# def question_labels(data_getter: DataGetter) -> List[np.array]:
#     """
#     :return: the label associated with each question.
#     """
#     ideal_answers = data_getter.location_ideal_answers()
#     labels = [LocationNN().run(answer) for answer in ideal_answers]
#     return labels


def testing_responses(dataset: Dataset) -> List[List[np.array]]:
    """
    :return: the response of the location neural net for each answer for each question.
    """
    return [list(map(LocationNN().run, answers)) for answers in dataset.location_data()]


def mode_response(responses: List[np.array]) -> (str, int):
    """
    :return: the most common neural net response for a question in the form (vector, count).
    """
    # Need to turn the vectors into a form that can be hashed by Counter.
    str_responses = [str(response) for response in responses]
    return Counter(str_responses).most_common(1)[0]


def compare(labels: List[np.array], responses: List[List[np.array]]) -> List[float]:
    """
    :return: the percentage of correct answer responses for each question.
    """
    percentages_correct = []

    for label, answer_responses in zip(labels, responses):
        # An array of 0s and 1s indicating whether the answer matches the label.
        are_equal = [np.array_equal(label, answer) for answer in answer_responses]
        num_correct = sum(are_equal)
        percentages_correct.append(num_correct / len(answer_responses))

    return percentages_correct

if __name__ == '__main__':
    dataset = Dataset()

    ideal_answers = dataset.location_ideal_answers()
    labels = dataset.location_question_targets()
    answer_responses = testing_responses(dataset)

    modes = [mode_response(answers) for answers in answer_responses]
    percentages_correct = compare(labels, answer_responses)
    mean_correct = sum(percentages_correct) / len(percentages_correct)

    print('Mean Correct:', round(mean_correct, 2), '\n')

    for question_num, (label, (mode_vec, mode_count), percentage_correct) in enumerate(zip(labels, modes, percentages_correct)):
        print('Question', question_num + 1, ideal_answers[question_num])
        print('\tIdeal Answer          :', ideal_answers[question_num])
        print('\tLabel                 :', label)
        print('\tIdeal Answer Response :', LocationNN().run(ideal_answers[question_num]))
        print('\tMode Response         :', mode_vec)
        print('\tMode Count            :', mode_count)
        print('\tNum Answers           :', len(answer_responses[question_num]))
        print('\tCorrect               :', round(percentage_correct, 2))
        print('\n')