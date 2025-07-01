from django.test import TestCase
from .models import *
from .serializers import *
from datetime import date

"""
Testing Models:

Can create authors, books, genres, etc.
Can update them
Can delete them
Can link them
Can fetch them
"""

class CopySerializerValidationTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            blurb="A test book",
            rating=4.0
        )

    def test_valid_copy_when_lent_true(self):
        data = {
            "book": self.book.id,
            "lent": True,
            "lent_by": "Ali",
            "return_date": "2025-08-01"
        }
        serializer = CopySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_lent_by_when_lent_true(self):
        data = {
            "book": self.book.id,
            "lent": True,
            "return_date": "2025-08-01"
        }
        serializer = CopySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("lent_by", serializer.errors)

    def test_missing_return_date_when_lent_true(self):
        data = {
            "book": self.book.id,
            "lent": True,
            "lent_by": "Ali"
        }
        serializer = CopySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("return_date", serializer.errors)

    def test_copy_when_lent_false_can_skip_fields(self):
        data = {
            "book": self.book.id,
            "lent": False,
            "lent_by": None,
            "return_date": None
        }
        serializer = CopySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)