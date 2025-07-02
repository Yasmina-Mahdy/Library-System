from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    """ A model to represent the different generes a book can have"""
    # using a class because too many choices to list as constants
    class Genre_Choices(models.TextChoices): 
        HORROR = 'horror', 'Horror'
        MYSTERY = 'mystery', 'Mystery'
        ROMANCE = 'romance', 'Romance'
        FANTASY = 'fantasy', 'Fantasy'
        ADVENTURE = 'adventure', 'Adventure'
        COMEDY = 'comedy', 'Comedy'
        OTHER = 'other', 'Other'

    name = models.CharField(max_length=10, choices = Genre_Choices, null=False, unique = True) # can alternatively check for uniqueness in the serializer or the view

    def __str__(self):
        return f"{self.name}"

class Author(models.Model):
    """A model to represent authors"""
    name = models.CharField(max_length = 255, null=False, unique=True)
    introduction = models.TextField(null=True, blank=True)
    place_of_origin = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class Book(models.Model):
    """A model to represent books"""
    title = models.CharField(max_length = 100, unique=True)
    blurb = models.TextField(null=False)
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)] # limiting the rating between 0.0 to 5.0
    ) # validators to restrict the values
    # authors = models.ManyToManyField(Author, through = 'BookAuthor') # no need for this
    # # the through here to allow adding extra fields to the M2M relationship
    genres = models.ManyToManyField(Genre, related_name='books')
    date_published = models.DateField()
    
    def __str__(self):
        return f"{self.title}; {self.rating} stars"
    

class BookAuthor(models.Model):
    """A model to represent a M-M relationship between books and authors with added attributes (role)"""
    book = models.ForeignKey(Book, on_delete = models.CASCADE, related_name='book_authors') # you use book_authors when you're coming from books and want to reach this model
    author = models.ForeignKey(Author, on_delete = models.RESTRICT, related_name='authored_books')
    role = models.CharField(max_length=100)

    class Meta:
        unique_together = ['book', 'author'] # to avoid repetition

    def __str__(self):
        return f"{self.author} => {self.book}"


class Copy(models.Model):
    book = models.ForeignKey(Book, on_delete = models.CASCADE, related_name = 'copies', null=True, blank=True)
    lent = models.BooleanField(default = False)
    lent_by = models.CharField(max_length = 255, default = None, null=True, blank=True) # ^^^ add the validation in the serializer where not null if lent: handle it in the serializer
    return_date = models.DateField(null=True,default = None, blank=True) # ^^^ same as lent by
