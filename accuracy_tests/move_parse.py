from accuracy_tests.datasets import Dataset
from parsing.pre_processing import pre_process
from parsing.parse_move import move


if __name__ == '__main__':
    data = Dataset('../client_secret.json')

    targets = data.location_question_targets()

    for q_num, question_answers in enumerate(data.location_data()):
        # It may not be possible to describe some question answers, therefore ignore those questions.
        if targets[q_num] is None:
            continue

        total_correct = 0
        for answer in question_answers:
            parse_result = move().parse(pre_process(answer))

            if parse_result == targets[q_num]:
                total_correct += 1

        print('Question', q_num, ':', total_correct)

