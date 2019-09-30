import os

def get_questions():
    path = 'quiz-questions'
    questions_files = [file for file in os.listdir(path)]

    questions = []
    answers = []
    
    for questions_file in questions_files:
        current_path = os.path.join(path, questions_file)
        with open(current_path, encoding='KOI8-R') as file:
            data = file.read().split('\n\n')

        for chunk in data:
            if chunk.startswith('Вопрос'):
                question = ' '.join(chunk.split('\n')[1:])
                questions.append(question)

            elif chunk.startswith('Ответ'):
                answer = ' '.join(chunk.split('\n')[1:])
                answers.append(answer)

    return list(zip(questions, answers))
