import os

def get_questions():
    path = 'quiz-questions'
    questions_files = [file for file in os.listdir(path) if os.path.splitext(file)[1] == '.txt']
    questions = {'questions': [], 'answers': []}
    
    for questions_file in questions_files:
        current_path = os.path.join(path, questions_file)
        with open(current_path, encoding='KOI8-R') as file:
            data = file.read().split('\n\n')

        for chunk in data:
            if chunk.startswith('Вопрос'):
                questions['questions'].append(chunk)

            elif chunk.startswith('Ответ'):
                questions['answers'].append(chunk)

    return questions
