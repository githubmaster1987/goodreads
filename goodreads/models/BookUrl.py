from goodreads.spiders.mysql_manage import db
from datetime import datetime
import goodreads.spiders.config
import os
# Holds card information
class BookUrl(db.Model):
    __tablename__ = "bookurls"

    book_url = db.Column(db.String(500))
    book_title = db.Column(db.String(500))
    category_url = db.Column(db.String(500))
    book_id = db.Column(db.Integer(), primary_key=True)
    
    def __init__(self, book_url, book_title, category_url):
        self.book_url = book_url
        self.category_url = category_url
        self.book_title =  book_title

    # Return a nice JSON response
    def serialize(self):
        return {
            'book_id': self.book_id,
            'book_url': self.book_url,
            'book_title': self.book_title,
            'category_url': self.category_url,
        }
