from goodreads.spiders.mysql_manage import db
from datetime import datetime
import goodreads.spiders.config
import os
# Holds card information
class BookInformation(db.Model):
    __tablename__ = "bookinformation"

    book_id = db.Column(db.Integer(), primary_key=True)
    book_url = db.Column(db.String(500))
    book_title = db.Column(db.String(500))
    book_author = db.Column(db.String(100))
    book_cover = db.Column(db.String(500))
    book_subtitle = db.Column(db.Text())
    book_desc  = db.Column(db.Text())
    book_getacopy  = db.Column(db.Text())
    book_format = db.Column(db.String(100))
    book_pages = db.Column(db.String(10))
    book_averagerating = db.Column(db.String(10))
    book_ratings = db.Column(db.String(10))
    book_reviews = db.Column(db.String(10))
    book_publishdate = db.Column(db.String(50))
    book_publisher = db.Column(db.String(50))
    book_firstpublished = db.Column(db.String(50))
    book_originaltitle = db.Column(db.String(500))
    book_isbn = db.Column(db.String(100))
    book_editionlanguage = db.Column(db.String(100))
    book_awards  = db.Column(db.Text())
    book_othereditions  = db.Column(db.Text())
    book_readersenjoyed  = db.Column(db.Text())
    book_quotes  = db.Column(db.Text())
    book_quotesmoreurl = db.Column(db.String(500))
    book_byauthor  = db.Column(db.Text())
    book_aboutauthor  = db.Column(db.Text())
    book_genres = db.Column(db.Text())
    book_categoryurl = db.Column(db.String(500))
        
    def __init__(self, book_url, book_title, book_author, book_cover, book_subtitle, book_desc, book_getacopy, book_format, book_pages, book_averagerating, book_ratings, book_reviews, book_publishdate, book_publisher, book_firstpublished, book_originaltitle, book_isbn, book_editionlanguage, book_awards, book_othereditions, book_readersenjoyed, book_quotes, book_quotesmoreurl, book_byauthor, book_aboutauthor, book_genres, book_categoryurl):
    
        self.book_url = book_url
        self.book_title = book_title
        self.book_author = book_author
        self.book_cover = book_cover
        self.book_subtitle = book_subtitle
        self.book_desc = book_desc
        self.book_getacopy = book_getacopy
        self.book_format = book_format
        self.book_pages = book_pages
        self.book_averagerating = book_averagerating
        self.book_ratings = book_ratings
        self.book_reviews = book_reviews
        self.book_publishdate = book_publishdate
        self.book_publisher = book_publisher
        self.book_firstpublished = book_firstpublished
        self.book_originaltitle = book_originaltitle
        self.book_isbn = book_isbn
        self.book_editionlanguage = book_editionlanguage
        self.book_awards = book_awards
        self.book_othereditions = book_othereditions
        self.book_readersenjoyed = book_readersenjoyed
        self.book_quotes = book_quotes
        self.book_quotesmoreurl = book_quotesmoreurl
        self.book_byauthor = book_byauthor
        self.book_aboutauthor = book_aboutauthor
        self.book_genres = book_genres
        self.book_categoryurl = book_categoryurl


    # Return a nice JSON response
    def serialize(self):
        return {
            'book_url' : self.book_url,
            'book_title' : self.book_title,
            'book_author' : self.book_author,
            'book_cover' : self.book_cover,
            'book_subtitle' : self.book_subtitle,
            'book_desc' : self.book_desc,
            'book_getacopy' : self.book_getacopy,
            'book_format' : self.book_format,
            'book_pages' : self.book_pages,
            'book_averagerating' : self.book_averagerating,
            'book_ratings' : self.book_ratings,
            'book_reviews' : self.book_reviews,
            'book_publishdate' : self.book_publishdate,
            'book_publisher' : self.book_publisher,
            'book_firstpublished' : self.book_firstpublished,
            'book_originaltitle' : self.book_originaltitle,
            'book_isbn' : self.book_isbn,
            'book_editionlanguage' : self.book_editionlanguage,
            'book_awards' : self.book_awards,
            'book_othereditions' : self.book_othereditions,
            'book_readersenjoyed' : self.book_readersenjoyed,
            'book_quotes' : self.book_quotes,
            'book_quotesmoreurl' : self.book_quotesmoreurl,
            'book_byauthor' : self.book_byauthor,
            'book_aboutauthor' : self.book_aboutauthor,
            'book_genres' : self.book_genres,
            'book_categoryurl' : self.book_categoryurl,
        }
