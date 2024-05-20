import csv
from typing import List
from app.schemas.result_quizes import GeneralQuizResultSchema


def generate_csv(results: List[GeneralQuizResultSchema], file_path: str):
    with open(file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(["user_id", "quiz_id", "company_id", "score", "total_correct_answers", "total_questions_answered"])

        for result in results:
            csv_writer.writerow([result.user_id, result.quiz_id, result.company_id, result.score, result.total_correct_answers, result.total_questions_answered])

    return file_path
