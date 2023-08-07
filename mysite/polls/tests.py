from django.test import TestCase

# Create your tests here.
import datetime
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """was_published_recently returns False for questions
        whose pub_date is in the future
        """
        a_future_time = timezone.now() + datetime.timedelta(days=1)
        future_question = Question(pub_date=a_future_time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions
        whose pub_date is older than 1 day
        """
        old_time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=old_time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions
        whose pub_date is within the last day
        """
        good_time = timezone.now() - datetime.timedelta(
            hours=23, minutes=59, seconds=59
        )
        recent_question = Question(pub_date=good_time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    create a question with the given `question_text`
    and published the given number of `days` offset to
    now (negative for question published in the past,
    positive for questions that have not yet been published.)

    Args:
        question_text (_type_): _description_
        days (_type_): _description_
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questionsj(self):
        """
        if no questions exist, an appropriate message is displayed
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])

    def test_future_question(self):
        """
        questions with a pub_date in the future aren't displayed on the
        index page
        """
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        even if both past and future questions exist,
        only past questions are displayed
        """
        question = create_question(question_text="past question", days=-30)
        create_question(question_text="future", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questons(self):
        """the questions index page may display multilple questions"""
        q1 = create_question("past 1", days=-1)
        q2 = create_question("past 2", days=-2)

        response = self.client.get(reverse("polls:index"))

        self.assertQuerysetEqual(response.context["latest_question_list"], [q1, q2])


class QuestionDetailViewTests(TestCase):
    def test_future_questions(self):
        """
        the detail view of a question with a pub_date
        in the future returns a 404 not found
        """
        future_question = create_question("future", 5)
        url = reverse("polls:detail", args=(future_question.id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
