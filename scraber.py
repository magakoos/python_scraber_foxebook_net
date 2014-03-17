#coding=UTF-8

import re
import urlparse
import csv
from grab import Grab
from lxml.etree import tostring, fromstring


URL = 'http://www.foxebook.net/'
REL_BOOKMARK = 'bookmark'
TEST_URL = 'http://www.foxebook.net/validated-numerics-a-short-introduction-to-rigorous-computations/'
OUTPUT_FILE = 'result.csv'
PAGINATION_CLASS  = 'archive-pagination pagination'

FIND_NUMBER = re.compile(r'\d')

def get_Grab_response(url):
    return Grab().go(url)


def is_link_valid(url):
    """Valid URL test, return true if page code not 404."""
    code = Grab().go(url).code
    if code == 404: return False
    else: return True


def page_numbers(url):
    """Get number from URL"""
    url = urlparse.urlparse(url)
    path = url.path
    path_parts = path.split('/')
    for part in path_parts:
        if part.isdigit() is True:
            return int(part)


def make_pages(url, pagination_class):
    """Get URL name and pagination_class. Find pagination class on page

    Return:
        list from first page to last.
    """
    if type(pagination_class) is not 'str':
        pagination_class = str(pagination_class)

    g = Grab()
    g.go(url)

    pagination = g.xpath('//div[@class="'+pagination_class+'"]')
    pages = (page_numbers(a.attrib['href']) for a in pagination.iter('a'))
    last = max(list(pages))

    page_list = []
    page_list.append(url)

    # fast google give no result about range() only this way =(
    for number in range(2, last + 1):
        page_list.append(urlparse.urljoin(url, 'page/'+str(number)+'/'))

    return page_list


def make_detail_pages(url, rel):
    """Make list of detail pages from <a rel=...>

    Return:
        list of urls
    """
    g = Grab()
    g.go(url)
    HTML_elements = g.tree

    detail_list = list()
    page_list = HTML_elements.find_rel_links(rel)
    for detail in page_list:
        detail_list.append(detail.attrib['href'])

    return detail_list


def parse_detail_page(url):
    """Extract information from URL.

    Return 2 values:
        dictionary, list of dictionary keys
    """
    searched_data = {}
    searched_data['url'] = url

    g = Grab()
    context = g.go(url)
    HTML_elements = g.tree

    xpath_download_link ='//*[@id="download"]/div/table/tbody'
    xpath_details = '//*[@id="details"]/div[2]/ul'
    xpath_rait = '//*[@id="content"]/div[2]/article/div[1]/div[2]/div[1]/span'
    xpath_tags = '//*[@id="content"]/div[2]/article/div[3]'

    post_info_list = []
    post_info = HTML_elements.find_class('post-info')
    post_info_div = post_info[0]

    # Find upload_date, post_author, count_comment, count_download
    for span in post_info_div.iter('span'):
        if span.getchildren() == []:
            post_info_list.append(span.text)
        else:
            texts = (elem.text for elem in span.getchildren())
            post_info_list.append(';'.join(texts))

    #Find tags
    tags = HTML_elements.xpath(xpath_tags)
    if tags != []:
        tag_list = []
        for a in tags[0].iter('a'):
            tag_list.append(a.text)
        searched_data['tags'] = tag_list

    # Find raiting
    raiting = HTML_elements.xpath(xpath_rait)
    if raiting != []:
        for meta in raiting[0].iter('meta'):
            name, value = meta.values()

            searched_data[name] = value.strip()

    # Find book details
    details = HTML_elements.xpath(xpath_details)
    if details != []:
        for li in details[0].iter('li'):
            separator = li.text.find(': ')
            name = li.text[:separator]

            if li.getchildren() == []:
                value = li.text[separator+2:] + li.tail
            else:
                for elem in li.getchildren():
                    if elem.tag == 'span' or elem.tag == 'a':
                        value = elem.text
                    elif elem.tag == 'meta':
                        value = elem.tail

            searched_data[name] = value.strip()

    # Find download links
    upload_table = HTML_elements.xpath(xpath_download_link)
    if upload_table != []:
        uploads_links = []
        for a in upload_table[0].iter('a'):
            link = {}
            link['url'] = a.text,
            link['is_valid'] = is_link_valid(a.text)
            uploads_links.append(link)
        searched_data['downloads_links'] = uploads_links

    searched_data['upload_date'] = post_info_list[0]
    searched_data['post_author'] = post_info_list[1]

    comment_count = FIND_NUMBER.search(post_info_list[3])
    searched_data['comment_count'] = comment_count.group()
    download_count = FIND_NUMBER.search(post_info_list[2])
    searched_data['download_count'] = download_count.group()

    # Stop the pain with UNICODE
    for key in searched_data:
        value_type = type(searched_data[key])
        if value_type == unicode:
            searched_data[key] = searched_data[key].encode(
                'UTF-8',
                errors='xmlcharrefreplace'
                )

    return searched_data, searched_data.keys()


def csv_dict_writer(path, fieldnames,  data):
    """Writes a CSV file using DictWriter"""
    with open(path, 'wb') as csv_file:
        writer = csv.DictWriter(
            csv_file, 
            fieldnames = fieldnames, 
            delimiter=';'
            )
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def main():
    """Main function"""
    page_list = make_pages(URL, PAGINATION_CLASS)
    data = []
    len_page_list = len(page_list)
    fieldnames = set()

    try:
        for index, page in enumerate(page_list):
            detail_pages = make_detail_pages(page, REL_BOOKMARK)
            print "(%d in %d)From page: '%s'. extracted %d links:" % (
                index,
                len_page_list,
                page, 
                len(detail_pages)
                )

            for detail_page in detail_pages:
                print detail_page
                detail_dict, detail_fields = parse_detail_page(detail_page)

                # Add "Empty" values not in fields
                lack_of_fields = set()
                field_set = set(detail_fields)

                if len(fieldnames)!=0:
                    lack_of_fields =  field_set - fieldnames
                fieldnames = field_set | lack_of_fields

                if len(lack_of_fields)!=0:
                    for field in lack_of_fields:
                        detail_dict[field] = 'Empty'

                data.append(detail_dict)
    except:
        print "ALARM!!! Something wrong =("
    finally:
        fieldnames = list(fieldnames)
        csv_dict_writer(OUTPUT_FILE, fieldnames=fieldnames, data=data)


if __name__ == '__main__':
    main()
