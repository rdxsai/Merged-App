"""
Question-related Pydantic models for the Canvas Quiz Manager.

This module contains all Pydantic models related to quiz questions,
including questions, answers, and question updates.
"""

from typing import List
from pydantic import BaseModel


class Answer(BaseModel):
    """
    Pydantic model representing a quiz answer option.

    Attributes:
        id (int): Unique identifier for the answer
        text (str): The answer text content
        html (str): HTML formatted version of the answer text
        comments (str): Feedback comments for this answer
        comments_html (str): HTML formatted version of the comments
        weight (float): Weight/score for this answer (0-100)
    """

    id: int
    text: str
    html: str = ""
    comments: str = ""
    comments_html: str = ""
    weight: float = 0.0


class Question(BaseModel):
    """
    Pydantic model representing a complete quiz question.

    Attributes:
        id (int): Unique identifier for the question
        quiz_id (int): ID of the quiz this question belongs to
        question_name (str): Name/title of the question
        question_type (str): Type of question (e.g., 'multiple_choice_question')
        question_text (str): The main question text
        points_possible (float): Maximum points for this question
        correct_comments (str): Feedback shown when answer is correct
        incorrect_comments (str): Feedback shown when answer is incorrect
        neutral_comments (str): General feedback for the question
        correct_comments_html (str): HTML formatted correct comments
        incorrect_comments_html (str): HTML formatted incorrect comments
        neutral_comments_html (str): HTML formatted neutral comments
        answers (List[Answer]): List of answer options for this question
    """

    id: int
    quiz_id: int
    question_name: str
    question_type: str
    question_text: str
    points_possible: float
    correct_comments: str = ""
    incorrect_comments: str = ""
    neutral_comments: str = ""
    correct_comments_html: str = ""
    incorrect_comments_html: str = ""
    neutral_comments_html: str = ""
    answers: List[Answer] = []


class QuestionUpdate(BaseModel):
    """
    Pydantic model for updating existing questions.

    Attributes:
        question_text (str): Updated question text
        topic (str): Topic/category for the question
        tags (str): Comma-separated tags for the question
        learning_objective (str): Associated learning objective
        correct_comments (str): Feedback for correct answers
        incorrect_comments (str): Feedback for incorrect answers
        neutral_comments (str): General feedback
        correct_comments_html (str): HTML formatted correct comments
        incorrect_comments_html (str): HTML formatted incorrect comments
        neutral_comments_html (str): HTML formatted neutral comments
        answers (List[Answer]): Updated list of answer options
    """

    question_text: str
    topic: str = "general"
    tags: str = ""
    learning_objective: str = ""
    correct_comments: str = ""
    incorrect_comments: str = ""
    neutral_comments: str = ""
    correct_comments_html: str = ""
    incorrect_comments_html: str = ""
    neutral_comments_html: str = ""
    answers: List[Answer] = []


class NewQuestion(BaseModel):
    """
    Pydantic model for creating new questions.

    Attributes:
        question_text (str): The question text
        question_type (str): Type of question
        topic (str): Topic/category for the question
        tags (str): Comma-separated tags
        learning_objective (str): Associated learning objective
        points_possible (float): Maximum points for the question
        neutral_comments (str): General feedback
        answers (List[Answer]): List of answer options
    """

    question_text: str
    question_type: str = "multiple_choice_question"
    topic: str = "general"
    tags: str = ""
    learning_objective: str = ""
    points_possible: float = 1.0
    neutral_comments: str = ""
    answers: List[Answer] = []
