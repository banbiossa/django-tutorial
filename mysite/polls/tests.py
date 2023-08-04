from django.test import TestCase

# Create your tests here.
import datetime
from django.utils import timezone

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """was_published_recently returns False for questions
        whose pub_date is in the future
        """
        a_future_time = timezone.now() + datetime.timedelta(days=1)
        future_question = Question(pub_date=a_future_time)
        self.assertIs(future_question.was_published_recently(), False)
