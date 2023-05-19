from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Text, DateTime
from typing import Optional
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.max_age = 0
    return response


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

class Question(db.Model):
    id: int = Column(Integer, primary_key=True)
    api_id: Optional[int] = Column(Integer)
    question_text: Optional[str] = Column(Text)
    answer_text: Optional[str] = Column(Text)
    value: Optional[int] = Column(Integer)
    airdate: Optional[datetime] = Column(DateTime)
    created_at: Optional[datetime] = Column(DateTime)
    updated_at: Optional[datetime] = Column(DateTime)
    category_id: Optional[int] = Column(Integer)
    game_id: Optional[int] = Column(Integer)

    def __init__(
        self,
        api_id: Optional[int],
        question_text: Optional[str],
        answer_text: Optional[str],
        value: Optional[int],
        airdate: Optional[datetime],
        created_at: Optional[datetime],
        updated_at: Optional[datetime],
        category_id: Optional[int],
        game_id: Optional[int]
    ):
        self.api_id = api_id
        self.question_text = question_text
        self.answer_text = answer_text
        self.value = value
        self.airdate = airdate
        self.created_at = created_at
        self.updated_at = updated_at
        self.category_id = category_id
        self.game_id = game_id


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/questions', methods=['POST'])
def get_questions():
    data = request.get_json()
    questions_num = data.get('questions_num')

    if questions_num is None:
        return jsonify({'error': 'Missing questions_num parameter'}), 400

    questions_num = int(questions_num)

    unique_questions = []
    while len(unique_questions) < questions_num:
        response = requests.get(f'https://jservice.io/api/random?count={questions_num - len(unique_questions)}')
        if response.status_code == 200:
            questions_data = response.json()
            for question_data in questions_data:
                existing_question = Question.query.filter_by(api_id=question_data['id']).first()
                if existing_question is None:
                    created_at = datetime.strptime(question_data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    updated_at = datetime.strptime(question_data['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    airdate = datetime.strptime(question_data['airdate'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    question = Question(
                        api_id=question_data['id'],
                        question_text=question_data['question'],
                        answer_text=question_data['answer'],
                        value=question_data['value'],
                        airdate=airdate,
                        created_at=created_at,
                        updated_at=updated_at,
                        category_id=question_data['category']['id'],
                        game_id=question_data['game_id']
                    )
                    unique_questions.append(question)
                    db.session.add(question)
                    db.session.commit()
                if len(unique_questions) >= questions_num:
                    break
        else:
            return jsonify({'error': 'Failed to fetch questions from the API'}), 500

    return jsonify({
        'questions': [
            {
                'id': question.id,
                'api_id': question.api_id,
                'question_text': question.question_text,
                'answer_text': question.answer_text,
                'value': question.value,
                'airdate': question.airdate.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'created_at': question.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'updated_at': question.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'category_id': question.category_id,
                'game_id': question.game_id
            }
            for question in unique_questions
        ]
    })


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)