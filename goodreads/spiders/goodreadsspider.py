# -*- coding: utf-8 -*-
import scrapy
import config
import sys
import csv
import proxylist
import useragent
import random, base64
import re
import os
import json
import os.path
from scrapy.http import Request, FormRequest
from goodreads.items import GoodreadsItem
from goodreads.mysql_manage import *
from goodreads.models import BookUrl, BookInformation

reload(sys)  
sys.setdefaultencoding('utf8')

class GoodreadsspiderSpider(scrapy.Spider):
    name = 'goodreadsspider'
    # allowed_domains = ['goodreads.com']
    parent_url = "https://www.goodreads.com/"
    login_url = "https://www.goodreads.com/user/sign_in?source=home"

    category_urls = [
        'https://www.goodreads.com/shelf/show/non-fiction',
        'https://www.goodreads.com/shelf/show/business',
    ]

    total_page_no = []

    error_url_csv_file_name = ""

    proxy_lists = proxylist.proxies
    useragent_lists = useragent.user_agent_list
    category_index = 0
    page_no = 0
    method = ''

    category_url = ""
    total_cnt = 0

    def set_proxies(self, url, callback, headers=None):
        if headers:
            req = Request(url=url, callback=callback,dont_filter=True, headers=headers)
        else:
            req = Request(url=url, callback=callback,dont_filter=True)

        proxy_url = random.choice(self.proxy_lists)
        user_pass=base64.encodestring('{}:{}'.format(proxylist.proxy_username, proxylist.proxy_password)).strip().decode('utf-8')
        req.meta['proxy'] = "http://" + proxy_url
        req.headers['Proxy-Authorization'] = 'Basic ' + user_pass

        user_agent = random.choice(self.useragent_lists)
        req.headers['User-Agent'] = user_agent
        return req

    def __init__(self, category =0, page_no=0, method='', *args, **kwargs):
        super(GoodreadsspiderSpider, self).__init__(*args, **kwargs)
        self.category_index = category
        self.page_no = page_no
        self.category_url = self.category_urls[int(self.category_index)]

        self.error_url_csv_file_name = "error_url_{}.csv".format(self.category_index)
        self.method = method

        for i in range(0, len(self.category_urls)):
            self.total_page_no.append(0)

        with open(self.error_url_csv_file_name, 'w') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["url", "note"])

    def start_requests(self):
        headers = {
            "Host": "www.goodreads.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "If-None-Match": 'W/"345591447a249cd038fa193c6ad05808"'
        }

        if self.method == "":
            req = self.set_proxies(self.parent_url, self.login_website, headers)
        else:
            req = self.set_proxies(self.parent_url, self.parse_book_url, headers)

        yield req

    def login_website(self, response):
        authenticated_token = response.xpath("//input[@name='authenticity_token']/@value").extract_first().encode('utf8')
        utf8 = response.xpath("//input[@name='utf8']/@value").extract_first().encode('utf8')
        n_value = response.xpath("//input[@name='n']/@value").extract_first().encode('utf8')

        payload = {
            "utf8": utf8,
            "authenticity_token": authenticated_token,
            "user[email]": config.username,
            "remember_me":"on",
            "user[password]": config.userpass,
            "n": n_value,
        }
        
        headers = {
            "Host": "www.goodreads.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Refer": 'https://www.goodreads.com/user/sign_in'
        }

        print "*********************Login*******************"
        print config.username, config.userpass
        # print headers
        # print payload
        req = FormRequest(url=self.login_url, 
            callback=self.call_root_url,
            dont_filter=True, 
            headers=headers,
            formdata = payload
            )

        yield req
    
    def call_root_url(self, response):
        print "*********************Root URL*******************"
        headers = {
            "Host": "www.goodreads.com",
            "User-Agent" : random.choice(self.useragent_lists),
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "www.goodreads.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.goodreads.com/user/sign_in?source=home",
        }

        req = Request(url=self.login_url, callback=self.call_category_url, dont_filter=True, headers=headers)
        yield req

    def call_category_url(self, response):
        login_field = response.xpath("//ul[@class='siteHeader__personal']")

        # with open("response.html", 'w') as f:
        #     f.write(response.body)
        self.page_no = self.page_no + 1

        if len(login_field) > 0:
            print "**********Log in successfully**********"
            
            headers = {
                "Host": "www.goodreads.com",
                "If-None-Match": 'W/"345591447a249cd038fa193c6ad05808"'
            }

            page_url = self.category_url
            req = self.set_proxies(page_url, self.parse_category, headers)

            yield req

    def parse_category(self, response):
        print "***********Parse Category****************", response.url, self.page_no, self.total_page_no[self.category_index]
        
        if self.page_no == 1:
            print "***********Page No************", self.page_no
            total_cnt_str = response.xpath("//span[(@class='smallText') and contains(text(), 'showing')]/text()").extract_first()
            self.total_cnt = int(re.search("of[\s]*(.*)\)", total_cnt_str, re.I|re.S|re.M).group(1).replace(",", ""))

            self.total_page_no[self.category_index] = self.total_cnt / 50
            print "Total=", self.total_cnt
            print self.total_page_no

        book_listings = response.xpath("//div[@class='elementList']")

        print "Book Len = ", len(book_listings)

        for i, book_listing in enumerate(book_listings):
            book_href_link = book_listing.xpath(".//a[@class='bookTitle']/@href").extract_first()
            book_title = book_listing.xpath(".//a[@class='bookTitle']/text()").extract_first()

            if book_href_link:
                book_url = response.urljoin(book_href_link.strip().encode("utf8"))

                book_item = db.session.query(BookUrl).filter(BookUrl.book_url == book_url).first()
                # print book_item
                if book_item == None:
                    book_url_obj = BookUrl(
                        book_url = book_url,
                        book_title = book_title.strip().encode("utf8"),
                        category_url = self.category_url,
                        )

                    try:
                        db.session.add(book_url_obj)
                        db.session.commit()
                    except Exception as e:
                        print e
                        pass

        if self.page_no <= self.total_page_no[self.category_index]:
            self.page_no = self.page_no + 1  

            headers = {
                "Host": "www.goodreads.com",
                "If-None-Match": 'W/"345591447a249cd038fa193c6ad05808"'
            }

            page_url = self.category_url + "?page=" + str(self.page_no)
            req = self.set_proxies(page_url, self.parse_category, headers)

            yield req

    def parse_book_url(self, response):
        book_info_url_list = db.session.query(BookInformation.book_url).filter(BookInformation.book_categoryurl == self.category_url)
        
        query = db.session.query(BookUrl).filter(BookUrl.category_url == self.category_url)
        book_url_list = query.filter(~BookUrl.book_url.in_(book_info_url_list)).all()
        
        headers = {
            "Host": "www.goodreads.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "If-None-Match": 'W/"345591447a249cd038fa193c6ad05808"'
        }

        # test_url = "https://www.goodreads.com/book/show/9793361-the-decision-book"
        # req = self.set_proxies(test_url, self.parse_book_detail, headers)
        # req.meta['bookUrl'] = test_url
        # yield req
        # return

        print "************************************"
        print "Remain = ", len(book_url_list)
        print "Exist = ", len(book_info_url_list.all())
        
        for i, input_item in enumerate(book_url_list):

            url = input_item.book_url
            
            req = self.set_proxies(url, self.parse_book_detail, headers)
            req.meta["bookUrl"] = url
            yield req


    def parse_book_detail(self, response):
        # print "********************Parse Detail*********************"
        print response.url
        
        book_url = response.meta["bookUrl"]

        error_item =  {
            "url" : response.url,
            "type": [],
            "priority":"low",
            "page_no": self.page_no,
            "category": self.category_url,
        }

        # try:
        item = GoodreadsItem()
        item["BookURL"] = response.url

        title_div = response.xpath("//h1[@id='bookTitle']")
        if len(title_div) > 0:
            item["Title"] =  title_div.xpath("text()").extract_first().strip().encode("utf8")
        else:
            return

        author_div =  response.xpath("//div[@id='bookAuthors']//a[@class='authorName']/span")
        if len(author_div) > 0:
            item["Author"] = author_div.xpath("text()").extract_first().strip().encode("utf8")
        else:
            error_item["type"].append( "Author")
        
        item["Cover"] = ""
        try:
            item["Cover"] = response.xpath("//img[@id='coverImage']/@src").extract_first().strip().encode("utf8")
        except:
            item["Cover"] = response.xpath("//div[@class='noCoverMediumContainer']/img/@src").extract_first().strip().encode("utf8")

        description_container =  response.xpath("//div[@id='descriptionContainer']/div[@id='description']")

        item["Subtitle"] = ""

        if len(description_container) > 0:
            sub_title_div = description_container.xpath(".//span/b")
            
            if len(sub_title_div) > 0:
                if sub_title_div[0].xpath("text()").extract_first():
                    item["Subtitle"] = sub_title_div[0].xpath("text()").extract_first().strip().encode("utf8")
            else:
                error_item["type"].append( "Subtitle")
        else:
            error_item["type"].append( "Description Container")

        more_exist = description_container.xpath(".//span[contains(@style, 'display:none')]")
        # print "*************More Desc***************", len(more_exist)
        if len(more_exist) > 0:
            description_div = more_exist.xpath(".//text()").extract()
        else:
            description_div = description_container.xpath(".//span//text()").extract()

        item["Description"] = ""

        if len(description_div) > 0:
            description_list = []
            for description_item in description_div:
                if description_item:
                    if description_item != item["Subtitle"]:

                        description_list.append(description_item.strip().encode("utf8"))

            item["Description"] = " ".join(description_list)
        else:
            error_item["type"].append( "Description")

        getacopy_div = response.xpath("//ul[contains(@class, 'buyButtonBar')]/li/a")
        
        item["GetACopy"] = []
        if len(getacopy_div) > 0:
            getacopy_list = []
            for getacopy_item in getacopy_div:
                if getacopy_item.xpath("@data-url"):
                    url_str = response.urljoin(getacopy_item.xpath("@data-url").extract_first().strip().encode("utf8"))
                    getacopy_list.append(url_str)
                elif getacopy_item.xpath("@href"):
                    url_str = response.urljoin(getacopy_item.xpath("@href").extract_first().strip().encode("utf8"))
                    getacopy_list.append(url_str)

            item["GetACopy"] = ",".join(getacopy_list)
        else:
            error_item["type"].append( "GetACopy")

        item["Format"] = ""
        format_div =  response.xpath("//div[@id='details']//span[@itemprop='bookFormat']/text()")
        if len(format_div) > 0:
            item["Format"] = format_div.extract_first().strip().encode("utf8")
        else:
            error_item["type"].append( "Format")

        item["Pages"] = ""
        pages_div = response.xpath("//div[@id='details']//span[@itemprop='numberOfPages']")
        if len(pages_div) > 0:
            item["Pages"] = pages_div.xpath("text()").extract_first().strip().encode("utf8").replace(" pages", "")
        else:
            error_item["type"].append( "Pages")

        item["AverageRating"] = ""
        average_rating_div = response.xpath("//div[@id='bookMeta']/span[@class='value rating']/span[@class='average']")
        if len(average_rating_div) > 0:
            item["AverageRating"] = average_rating_div.xpath("text()").extract_first().strip().encode("utf8")
        else:
            error_item["type"].append( "AverageRating")

        item["Ratings"] = ""
        rating_div = response.xpath("//div[@id='bookMeta']//span[@class='votes value-title']")
        if len(rating_div) > 0:
            item["Ratings"] = rating_div.xpath("text()").extract_first().strip().encode("utf8")
        else:
            error_item["type"].append( "Ratings")

        item["Reviews"] = ""
        review_div = response.xpath("//div[@id='bookMeta']//span[@class='count value-title']")
        if len(review_div) > 0:
            item["Reviews"] = review_div.xpath("text()").extract_first().strip().encode("utf8")
        else:
            error_item["type"].append( "Reviews")


        details_div = response.xpath("//div[@id='details']/div[@class='row']")
        
        item["FirstPublished"] = ""
        item["PublishDate"] = ""
        item["Publisher"] = ""

        if len(details_div) > 0:
            if len(details_div) == 1:
                detail_div_obj = details_div[0]
            else:
                detail_div_obj = details_div[1]
                
            detail_div_str = detail_div_obj.xpath("text()").extract_first().strip().encode("utf8").replace("\n", "")
            try:
                item["PublishDate"] = re.search("Published[\s]*(.*?)[\s]*by", detail_div_str, re.I|re.S|re.M).group(1)
            except:
                item["PublishDate"] = re.search("Published[\s]*(.*)", detail_div_str, re.I|re.S|re.M).group(1)
            
            try:                
                item["Publisher"] = re.search("by[\s]*(.*)", detail_div_str, re.I|re.S|re.M).group(1)
            except:
                pass

            try:
                first_published_str = detail_div_obj.xpath("nobr/text()").extract_first().strip().encode("utf8")
                item["FirstPublished"] = re.search("first[\s]*published[\s]*(.*?)\)", first_published_str, re.I|re.S|re.M).group(1)
            except:
                error_item["type"].append( "FirstPublished")
        else:
            error_item["type"].append( "Details Div")
            error_item["priority"] = "high"

        bookDataBox_div = response.xpath("//div[@id='bookDataBox']/div[@class='clearFloats']")

        if len(bookDataBox_div) > 0:

            original_title_div = None
            isbn_content_div = None
            edition_language_div = None
            award_content_div = None

            for div_item in bookDataBox_div:
                title_str = div_item.xpath("div[@class='infoBoxRowTitle']/text()").extract_first().strip().encode("utf8")
                
                if title_str == "ISBN":
                    isbn_content_div = div_item
                elif title_str == "Edition Language":
                    edition_language_div = div_item
                elif title_str == "Literary Awards":
                    award_content_div = div_item
                elif title_str == "Original Title":
                    original_title_div = div_item


            item["OriginalTitle"] = ""
            if original_title_div:
                item["OriginalTitle"] = original_title_div.xpath(".//div[@class='infoBoxRowItem']/text()").extract_first().strip().encode("utf8")

            item["ISBN"] = ""
            if isbn_content_div:
                isbn_div = isbn_content_div.xpath(".//div[@class='infoBoxRowItem']//text()").extract()

                isbn_text_list = []

                if len(isbn_div) > 0:
                    for isbn_item in isbn_div:
                        if isbn_item.strip() != "":
                            isbn_text_list.append(isbn_item.strip().encode("utf8"))
                else:
                    error_item["type"].append( "ISBN")
                
                item["ISBN"] = "".join(isbn_text_list)

            item["EditionLanguage"] = ""
            if edition_language_div:
                if edition_language_div.xpath(".//div[@class='infoBoxRowItem']/text()").extract_first():
                    item["EditionLanguage"] =edition_language_div.xpath(".//div[@class='infoBoxRowItem']/text()").extract_first().strip().encode("utf8")
            else:
                error_item["type"].append( "EditionLanguage")
            
            item["Awards"] = ""

            if award_content_div:
                award_list = []

                award_div = award_content_div.xpath(".//div[@class='infoBoxRowItem']//text()").extract()
                
                if len(award_div) > 0:
                    for award_item in award_div:
                        if award_item.strip() != "":
                            award_list.append(award_item.strip().encode("utf8"))
                else:
                    error_item["type"].append( "Awards")
                
                item["Awards"] = "".join(award_list)

            item["OtherEditions"] = ""
            other_edition_div = response.xpath("//div[@class='otherEditionCovers']/ul/li/div/a")
            if len(other_edition_div) > 0:
                other_edition_list = []
                for other_deition_item in other_edition_div:
                    other_edition_list.append(other_deition_item.xpath("@href").extract_first().strip().encode("utf8"))

                item["OtherEditions"] = ",".join(other_edition_list)
            else:
                error_item["type"].append( "OtherEditions")

            enjoyed_list = []
            for enjoy_item in response.xpath("//div[@class='rightContainer']//div[contains(@id, 'relatedWorks')]//div[@class='carouselRow']/ul/li/a"):
                enjoy_item_link = enjoy_item.xpath("@href").extract_first().strip().encode("utf8")
                enjoyed_list.append(enjoy_item_link)       
            
            item["BooksReadersEnjoyed"] = ",".join(enjoyed_list)
        else:
            error_item["type"].append( "bookDataBox Div")
            error_item["priority"] = "high"

        booksbyauthor_div = response.xpath("//div[@class='js-dataTooltip']/div/a")
        
        item["BooksByAuthor"] = ""
        if len(booksbyauthor_div) > 0:
            
            booksbyauthor_list = []
            for booksbyauthor_item in booksbyauthor_div:
                href_link = booksbyauthor_item.xpath("@href").extract_first().strip().encode("utf8")
                booksbyauthor_list.append(response.urljoin(href_link))
            
            item["BooksByAuthor"] = ",".join(booksbyauthor_list)
        else:
            error_item["type"].append( "BooksByAuthor")

        bookRightContainer = response.xpath("//div[@class='rightContainer']/div[contains(@class, ' clearFloats')]")


        if len(bookRightContainer) > 0:
            item["QuotesMoreUrl"] = ""

            more_quotes_link_div = bookRightContainer.xpath(".//a[(@class='actionLink') and contains(text(), 'More quotes')]")
            if len(more_quotes_link_div) > 0:
                more_quotes_link = response.urljoin(more_quotes_link_div.xpath("@href").extract_first().strip())
                item["QuotesMoreUrl"] = more_quotes_link
            else:
                error_item["type"].append( "More Quote Link")

            item["Quotes"] = ""
            quote_list = []
            quote_bookDataBox_Div = None


            for bookDataBox_item in bookRightContainer:
                quote_a_div = bookDataBox_item.xpath(".//h2[@class='brownBackground']/a[contains(text(), 'Quotes from')]")

                if len(quote_a_div) > 0:
                    quote_bookDataBox_Div = bookDataBox_item
                    break

            if quote_bookDataBox_Div:
                quote_divs = quote_bookDataBox_Div.xpath(".//div[contains(@class, 'bigBoxContent')]/div[@class='stacked']/span[@class='readable']")
                for quote_item in quote_divs:
                    quote_str = quote_item.xpath("text()").extract_first().strip().encode("utf8")
                    quote_list.append(quote_str)

                item["Quotes"] = ",".join(quote_list)
            else:
                error_item["type"].append( "Quotes")
        else:
            error_item["type"].append( "bookRightContainer" )
       
        item["Genres"] = ""
        genre_divs = response.xpath("//div[contains(@class, 'elementList')]/div[@class='left']")

        genre_list = []
        for genre_item in genre_divs:
            genre_str = genre_item.xpath(".//text()").extract()
            genre_str_list = []
            for genre_str_item in genre_str:
                if genre_str_item.strip() != "":
                    genre_str_list.append(genre_str_item.strip().encode("utf8"));

            if len(genre_str_list) > 0:
                genre_list.append("".join(genre_str_list))
            else:
                error_item["type"].append( "Genres" )

        item["Genres"] = ",".join(genre_list)

        author_div = response.xpath("//div[@id='aboutAuthor']/div[@class='bigBoxBody']//div[@class='readable']")
        
        item["AboutAuthor"] = ""
        if len(author_div) > 0:
            non_author_div = author_div.xpath(".//span[contains(@style, 'display:none')]")

            if len(non_author_div) > 0:
                author_str_list = []
                
                for non_author_item in non_author_div.xpath(".//text()").extract():
                    temp_str = non_author_item.strip().encode("utf8")
                    
                    author_str_list.append(temp_str)
                
                item["AboutAuthor"] = " ".join(author_str_list)
            else:
                author_temp_div = author_div.xpath(".//span")

                if len(author_temp_div) > 0:
                    if author_temp_div.xpath("text()").extract_first():
                        item["AboutAuthor"] = author_temp_div.xpath("text()").extract_first().strip().encode("utf8")
        else:
            error_item["type"].append( "AboutAuthor") 
        
        no_error = True
        if len(error_item["type"]) > 0:
            if error_item["priority"] == "high":
                no_error = False
                print error_item

        if no_error == True:
            # yield item

            book_info = BookInformation(
                book_url = book_url,
                book_title = item["Title"],
                book_author = item["Author"],
                book_cover = item["Cover"],
                book_subtitle = item["Subtitle"],
                book_desc = item["Description"],
                book_getacopy = item["GetACopy"],
                book_format = item["Format"],
                book_pages = item["Pages"],
                book_averagerating = item["AverageRating"],
                book_ratings = item["Ratings"],
                book_reviews = item["Reviews"],
                book_publishdate = item["PublishDate"],
                book_publisher = item["Publisher"],
                book_firstpublished = item["FirstPublished"],
                book_originaltitle = item["OriginalTitle"],
                book_isbn = item["ISBN"],
                book_editionlanguage = item["EditionLanguage"],
                book_awards = item["Awards"],
                book_othereditions = item["OtherEditions"],
                book_readersenjoyed = item["BooksReadersEnjoyed"],
                book_quotes = item["Quotes"],
                book_quotesmoreurl = item["QuotesMoreUrl"],
                book_byauthor = item["BooksByAuthor"],
                book_aboutauthor = item["AboutAuthor"],
                book_genres = item["Genres"],
                book_categoryurl = self.category_url,
            )

            try:
                db.session.add(book_info)
                db.session.commit()
            except Exception as e:
                print e
                pass

        else:
            with open(self.error_url_csv_file_name, 'a') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([response.url, ",".join(error_item["type"])])

        # except Exception as e:
        #     print e
        #     with open(self.error_url_csv_file_name, 'a') as csvfile:
        #         csv_writer = csv.writer(csvfile)
        #         csv_writer.writerow([response.url])
