from rest_framework import serializers
from .models import *
from copy import deepcopy

# ask for opinoin/ what tp add
# what are querysets
# after writing the basics what can i add => think about it
# do i need to do error handling

"""Note: Apparently nesting serializers instead of flattening data is better in terms of intergration with frontend"""


class AuthorLookupField(serializers.RelatedField):
    """This allows us to look up an author by their ID, Name or Create a new author in case they do not exist.
    We need this to avoid having to input the whole author object when trying to link an author to a book"""
    def __init__(self, **kwargs):
        kwargs['queryset'] = kwargs.get('queryset', Author.objects.all())
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if isinstance(data, int):
            try:
                return Author.objects.get(pk=data)
            except Author.DoesNotExist:
                raise serializers.ValidationError("No author exists with this ID")
        elif isinstance(data, str):
            try:
                return Author.objects.get(name=data)
            except Author.DoesNotExist:
                raise serializers.ValidationError("No author exists with this name")
        elif isinstance(data, dict):
            name = data.get("name")
            if not name:
                raise serializers.ValidationError("Author name is required when creating an author")
            try:
                return Author.objects.get(name=name)
            except Author.DoesNotExist:
                serializer = AuthorSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                return serializer.save()
        else:
            raise serializers.ValidationError("Author must be an ID (int), name (str) or object (dict).")
        
class BookLookupField(serializers.RelatedField):
    """This allows us to look up a book by its ID, Name or Create a new book in case it does not exist.
    We need this to avoid having to input the whole book object when trying to link an book to an author or copy"""

    def __init__(self, **kwargs):
        kwargs['queryset'] = kwargs.get('queryset', Book.objects.all())
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if isinstance(data, int):
            try:
                return Book.objects.get(pk=data)
            except Book.DoesNotExist:
                raise serializers.ValidationError("No book exists with this ID")
        elif isinstance(data, str):
            try:
                return Book.objects.get(title=data)
            except Book.DoesNotExist:
                raise serializers.ValidationError("No Book exists with this title")
        elif isinstance(data, dict):
            title = data.get("title")
            if not title:
                raise serializers.ValidationError("Book title is required when creating an book")

            try:
                return Book.objects.get(title=title)
            except Book.DoesNotExist:
                serializer_context = self.root.context.copy() # context stuff if nesting inside author
                # serializer_context['nested_in_author'] = True     # wrong to put this here
                """We pass the context to the BookSerializer so that we do not require the authors of a book when its being created inside of 
                an author [The author is implicit in this case]."""
                serializer = BookSerializer(data=data, context=serializer_context)
                serializer.is_valid(raise_exception=True)
                return serializer.save()
        else:
            raise serializers.ValidationError("Book must be an ID (int), name (str) or object (dict).")
        
class GenreLookupField(serializers.RelatedField):

    """This allows us to look up a genre by its ID, Name or Create a new genre in case it does not exist.
    We need this to avoid having to input the whole genre object when trying to link it to a book"""

    def __init__(self, **kwargs):
        kwargs['queryset'] = kwargs.get('queryset', Genre.objects.all())
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if isinstance(data, int):
            try:
                return Genre.objects.get(pk=data)
            except Genre.DoesNotExist:
                raise serializers.ValidationError("No genre exists with this ID")
        elif isinstance(data, str):
            try:
                return Genre.objects.get(name=data)
            except Genre.DoesNotExist:
                raise serializers.ValidationError("No genre exists with this title")
        elif isinstance(data, dict):
            name = data.get("name")
            if not name:
                raise serializers.ValidationError("Genre name is required when creating an genre")

            try:
                return Genre.objects.get(name=name)
            except Genre.DoesNotExist:
                serializer = GenreSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                return serializer.save()
        else:
            raise serializers.ValidationError("Genre must be an ID (int), name (str) or object (dict).")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name'] # all will also show the ID


"""Using separate serializers for reading/writing for each of the books and authors to change the fields between lookup and display"""
# (nothing to do with circular dep since using stringrelated but for fututre reasons)
class BookAuthorBookSideReadSerializer(serializers.ModelSerializer):
    # might replace stringrelated with hyperlinks in the future
    author = serializers.StringRelatedField(read_only=True) # string related because i didn't want to show each author with their books and so on => ik i can just control the fields but meh
    class Meta:
        model = BookAuthor
        fields = ['author', 'role']

class BookAuthorBookSideWriteSerializer(serializers.ModelSerializer):
    author = AuthorLookupField() # do the init instead of passing the queryset here
    class Meta:
        model = BookAuthor
        fields = ['author', 'role']

class BookAuthorAuthSideReadSerializer(serializers.ModelSerializer):

    book = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = BookAuthor
        fields = ['book', 'role']

class BookAuthorWriteSerializer(serializers.ModelSerializer):

    book = BookLookupField() #shoulf handle ONE book not MULTIPLE
    role = serializers.CharField() 

    class Meta:
        model = BookAuthor
        fields = ['book', 'role']


class AuthorSerializer(serializers.ModelSerializer):

    """A serializer to handle authors and also call classes that handle its relationship with books"""
    # could get away without the source for books even when it's not related just because i handle creation myself so DRF does not need the models
    books = BookAuthorWriteSerializer(source='authored_books', many=True, write_only=True, required = False) # if smth is not required, only makes sense to specify that for writing not reading
    # It is redundant to specify `source='authored_books'` on field 'ListSerializer' in serializer 'AuthorSerializer', because it is the same as the field name. Remove the `source` keyword argument.
    authored_books = BookAuthorAuthSideReadSerializer(many=True, read_only=True) # the read_only means you dont need to worry abobut this field when creating an author -> good
    # this is outside of meta
    avg_rating = serializers.SerializerMethodField(read_only=True) # this is something we compute so we can only read it and method to round
    class Meta:
        model = Author
        fields = ['id','name', 'introduction', 'place_of_origin', 'books', 'authored_books', 'avg_rating'] # need to add avg_rating here

     # need to override create and update because i have a separate M2M table
    def create(self, validated_data):
        books_data = validated_data.pop('books', []) # based on the serializer each "book" has a book and an author


        # want to do if exists
        # date_published = validated_data.pop('date_published') 

        author = Author.objects.create(**validated_data) # must pop everything you need before here
        
        # this also handles creating the link when the authors of a nested book being created are missing
        for item in books_data:
            BookAuthor.objects.create(
                book=item['book'],
                author=author,
                role=item['role']
            )
        return author
    
    def update(self, instance, validated_data):
        books = validated_data.pop('books', None) # None not [] to avoid overwriting when nothing is there
       
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            instance.save()

        # Delete old relationship objects and recreate them with the new data
        if books is not None:
            BookAuthor.objects.filter(author=instance).delete()
            for item in books:
                BookAuthor.objects.create(
                book=item['book'],
                author=instance,
                role=item['role']
                )
        return instance
    
    def get_avg_rating(self, obj):
        try:
            return round(obj.avg_rating, 2)
        except Exception: # need this since i overrided the get_average while it's not a real field in the model => causes some errors when creating an object that still has no average rating
                return None


class BookMiniSerializer(serializers.ModelSerializer):
    """Using this in copies to avoid circular dependency AND limit the data"""
    genres = serializers.StringRelatedField(many=True)

    class Meta:
        model = Book
        fields = ['title', 'genres', 'rating']

class CopySerializer(serializers.ModelSerializer):
    """Handles copies and their relationship to books, along with the necessary validation"""
    book = BookLookupField(write_only=True)
    book_info = BookMiniSerializer(source = 'book', read_only=True)
    
    class Meta:
        model = Copy
        fields = ['book', 'book_info' ,'lent','lent_by','return_date']
    
    def validate(self, data):
        # Get data from the input (for POST/PUT) or instance (for PATCH)
        lent = data.get('lent', getattr(self.instance, 'lent', False)) # tries to get from input, else for patch from existing data, else false
        lent_by = data.get('lent_by', getattr(self.instance, 'lent_by', None))
        return_date = data.get('return_date', getattr(self.instance, 'return_date', None))

        # Rule: if lent is True, both lent_by and return_date must be set
        if lent:
            if not lent_by:
                raise serializers.ValidationError({"lent_by": "This field is required when the book is lent."})
            if not return_date:
                raise serializers.ValidationError({"return_date": "This field is required when the book is lent."})
        return data

# no need for validation since this is read only
class CopyMiniSerializer(serializers.ModelSerializer):
    """to limit the data shown inside books"""
    class Meta:
        model = Copy
        fields = ['lent', 'lent_by', 'return_date']
        read_only_fields = fields

class BookSerializer(serializers.ModelSerializer):
    """A serializer to handle authors and also call classes that handle its relationship with authors and genres"""
    authors = BookAuthorBookSideWriteSerializer(many=True, write_only=True)
    authors_info = BookAuthorBookSideReadSerializer(source = 'book_authors', many=True, read_only=True) # the source is the related name
    genres = GenreLookupField(many=True, write_only=True)
    genres_info = serializers.StringRelatedField(source='genres', many=True, read_only=True)
    copies = CopyMiniSerializer(many=True, read_only=True)
    num_copies = serializers.IntegerField(read_only=True) # annotated in view
    date_published = serializers.DateField() 
    coauthors = serializers.SerializerMethodField(read_only=True) # a method to see if there are multiple authors

    class Meta:
        model = Book
        fields = ['id','title', 'blurb', 'rating', 'genres', 'genres_info', 'authors', 'date_published', 'coauthors' ,'authors_info', 'copies', 'num_copies'] # must incl all firlds -> even WR only
 

    # !!! using this leades to a bug where if an author is included inside the book either way it's ignored, fixed in validate 
    """def get_fields(self):
        
        fields = super().get_fields()
        if self.context.get('nested_in_author'):
            fields.pop('authors', None)
        return fields"""

    # need to override create and update because i have a separate M2M table
    def create(self, validated_data):
        authors_data = validated_data.pop('authors', [])
        genres_data = validated_data.pop('genres', []) 
        # date_published = validated_data.pop('date_published') # have this here instead of a published date per author

        book = Book.objects.create(**validated_data) # must pop everything you need before here
        book.genres.set(genres_data)
        
        for entry in authors_data:
                BookAuthor.objects.create(
                    book=book,
                    author=entry['author'],
                    role=entry['role'],
        )

        return book
    
    def update(self, instance, validated_data):
        authors_data = validated_data.pop('authors', None) # None not [] to avoid overwriting when nothing is there
        # date_published = validated_data.pop('date_published', None)
        genres_data = validated_data.pop('genres', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            instance.save()

        if genres_data is not None:
            instance.genres.set(genres_data)

        if authors_data is not None:
            BookAuthor.objects.filter(book=instance).delete()
            for entry in authors_data:
                BookAuthor.objects.create(
                book=instance,
                author=entry['author'],
                role=entry['role'],
            )
                # date_published = date_published
                
        return instance
    
    """REMOVING THIS FOR NOW assuming that validate hansles this, but need to test this => quick test shows it works but might need more
        extensive checking"""
    """def validate_authors(self, value):
        if not value:
            raise serializers.ValidationError("At least one author must be provided.")
        return value"""

    def get_coauthors(self, obj):
        book_authors = obj.book_authors.all()
        if book_authors.count() > 1:
            return True
        return False
    # could add to representation to change the bame

    def validate(self, data):
        """
        Overriding the default function to get the context in order to not require the author iff the book is being created
        inside of an author (the author is implicit and establishing the link is handled in the author serializer in this case).
        Old function would (the one where overriding the get_fields) would always ignore the authors, instead here we just make it optional
        """
        nested = self.context.get('nested_in_author', False)
        if not nested:
            if not data.get('authors'):
                raise serializers.ValidationError({"authors": "This field is required."})
        
        return data