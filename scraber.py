#coding=UTF-8

import re
import urlparse
from grab import Grab
# from lxml.etree import tostring, fromstring


# I want to make scraber for site 'http://www.foxebook.net/',
# and save all data in csv.

# My aim to learn work with lmxl library. Right now I don't
# how to work with urllib or pycurl, and will use framework grab.

# I think, it will be correct to make it in next step:
    # 1. Make list of pages, who content links to details.
    # 2. Make dict of pages with details.
    # 3. Collect details to dict.
    # 3.1 Test to work download link.
    # 4. Write details to CSV.

URL = 'http://www.foxebook.net/'
REL_BOOKMARK = 'bookmark'
TEST_URL = 'http://www.foxebook.net/validated-numerics-a-short-introduction-to-rigorous-computations/'

FIND_NUMBER = re.compile(r'\d')


def page_numbers(url):
    url = urlparse.urlparse(url)
    path = url.path
    path_parts = path.split('/')
    for part in path_parts:
        if part.isdigit() is True:
            return int(part)


def make_pages(url, pagination_class):
    if type(pagination_class) is not 'str':
        pagination_class = str(pagination_class)

    g = Grab()
    content = g.go(url)

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
    g = Grab()
    content = g.go(url)
    HTML_elements = g.tree

    detail_list = HTML_elements.find_rel_links(rel)
    for detail in detail_list:
        print detail.attrib['href']

    return detail_list


def parse_detail_page(url):
    searched_data = {}
    g = Grab()
    content = g.go(url)
    HTML_elements = g.tree

    post_info_list = []
    post_info = HTML_elements.find_class('post-info')
    post_info_div = post_info[0]

    for span in post_info_div.iter('span'):
        if span.getchildren() == []:
            post_info_list.append(span.text)
        else:
            texts = (elem.text for elem in span.getchildren())
            post_info_list.append(';'.join(texts))

    xpath_rait = '//*[@id="content"]/div[2]/article/div[1]/div[2]/div[1]/span'
    raiting = HTML_elements.xpath(xpath_rait)
    for meta in raiting[0].iter('meta'):
        name, value = meta.values()
        searched_data[name] = value

    xpath_details = '//*[@id="details"]/div[2]/ul'
    details = HTML_elements.xpath(xpath_details)

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

        searched_data[name] = value

    searched_data['upload_date'] = post_info_list[0]
    searched_data['post_author'] = post_info_list[1]
    searched_data['download_count'] = post_info_list[2]

    comment_count = FIND_NUMBER.search(post_info_list[3])
    searched_data['comment_count'] = comment_count.group()

    return searched_data


def write_to_csv():
    pass


def main():
    page_list = make_pages(URL, 'archive-pagination pagination')
    # len_page_list = len(page_list)
    for index, page in enumerate(page_list):
        print "From page: '%s'." % (page)


if __name__ == '__main__':

    print parse_detail_page(TEST_URL)
