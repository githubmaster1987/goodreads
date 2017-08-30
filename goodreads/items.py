# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GoodreadsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    BookURL = scrapy.Field()
    Title = scrapy.Field()
    Author = scrapy.Field()
    Cover = scrapy.Field()
    Subtitle = scrapy.Field()
    Description = scrapy.Field()
    GetACopy = scrapy.Field()
    Format = scrapy.Field()
    Pages = scrapy.Field()
    AverageRating = scrapy.Field()
    Ratings = scrapy.Field()
    Reviews = scrapy.Field()
    PublishDate = scrapy.Field()
    Publisher = scrapy.Field()
    FirstPublished = scrapy.Field()
    OriginalTitle = scrapy.Field()
    ISBN = scrapy.Field()
    EditionLanguage = scrapy.Field()
    Awards = scrapy.Field()
    OtherEditions = scrapy.Field()
    BooksReadersEnjoyed = scrapy.Field()
    Quotes = scrapy.Field()
    QuotesMoreUrl = scrapy.Field()
    BooksByAuthor = scrapy.Field()
    AboutAuthor = scrapy.Field()
    Genres = scrapy.Field()