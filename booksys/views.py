from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Value
from django.db.models.functions import Coalesce

# Create your views here.

class GenreListView(APIView):
    def get(self, request):
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = GenreSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AuthorListView(APIView):
    def get(self, request):
        role = request.query_params.get('role')
        authors = Author.objects.annotate(
                avg_rating=Avg('authored_books__book__rating')
            )
        
        if role:
            authors = authors.filter(authored_books__role__iexact=role).distinct()

        ordering = request.query_params.get('ordering')
        if ordering:
            authors = authors.order_by(ordering)
        
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AuthorSerializer(
            data=request.data,
            context={'nested_in_author': True}  
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorDetailView(APIView):

    def get(self, request, pk):
        queryset = Author.objects.annotate(
                avg_rating=Avg('authored_books__book__rating')
            )
        author = get_object_or_404(queryset, pk=pk) #pass query set instead of the model
        serializer = AuthorSerializer(author)
        return Response(serializer.data)
    
    def put(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        serializer = AuthorSerializer(
            author,
            data=request.data,
            context={'nested_in_author': True}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def patch(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        serializer = AuthorSerializer(
            author,
            data=request.data,
            partial=True,
            context={'nested_in_author': True} 
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        author.delete()
        return Response(status=204)

    


class BookListView(APIView):

    def get(self, request):

        # getting query parameters
        genre = request.query_params.get('genres')
        author_name = request.query_params.get('book_authors')

        books = Book.objects.annotate(
            num_copies=Coalesce(Count('copies'), Value(0))
        )

        if genre:
            books = books.filter(genres__name__iexact=genre).distinct()
        if author_name:
            books = books.filter(book_authors__author__name__iexact=author_name)

        ordering = request.query_params.get('ordering')
        if ordering:
            books = books.order_by(ordering)

        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BookSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class BookDetailView(APIView):

    def get(self, request, pk):
        queryset = Book.objects.annotate(
                num_copies= Coalesce(Count('copies'), Value(0))
            )
        book = get_object_or_404(queryset, pk=pk) #pass query set instead of the model
        serializer = BookSerializer(book)
        return Response(serializer.data)
    
    def put(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def patch(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        book.delete()
        return Response(status=204)


class CopyListView(APIView):

    def get(self, request):
        copies = Copy.objects.all()
        book = request.query_params.get('book')
        genre = request.query_params.get('genre')
        lent = request.query_params.get('lent')

        if book:
            copies = copies.filter(book__title__iexact=book).distinct()

        if genre:
            copies = copies.filter(book__genres__name__iexact=genre).distinct()

        if lent:
            if lent.lower() == 'true':
                copies = copies.filter(lent=True)
            elif lent.lower() == 'false':
                copies = copies.filter(lent=False)

        ordering = request.query_params.get('ordering')
        if ordering:
            books = books.order_by(ordering)


        serializer = CopySerializer(copies, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CopySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CopyDetailView(APIView):

    def get(self, request, pk):
        copy = get_object_or_404(Copy, pk=pk) #pass query set instead of the model
        serializer = CopySerializer(copy)
        return Response(serializer.data)
    
    def put(self, request, pk):
        copy = get_object_or_404(Copy, pk=pk)
        serializer = CopySerializer(copy, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def patch(self, request, pk):
        copy = get_object_or_404(Copy, pk=pk)
        serializer = CopySerializer(copy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        copy = get_object_or_404(Copy, pk=pk)
        copy.delete()
        return Response(status=204)
        