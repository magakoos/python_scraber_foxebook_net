python_scraber_foxebook_net
===========================

My first scraber =))) it is study work.

I want to make scraber for site 'http://www.foxebook.net/',
 and save all data in csv.

 My aim to learn work with lmxl library. Right now I don't know
 how to work with urllib or pycurl, and will use framework grab.

 I think, it will be correct to make it in next step:
    1. Make list of pages, who content links to details.
    2. Make dict of pages with details.
    3. Collect details to dict.
    3.1 Test to work download link.
    3.2 Collect tag from page.
    4. Write details to CSV.

Problems:
    UnicodeEncodeError: 'ascii' codec can't encode character u'\xed' in position 3: ordinal not in range(128)

For valid link test we need find all link to filestorages and get page from every URL:
    http://www.embedupload.com/
    xpath to table with links to filestorages
    /html/body/table[2]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/table/tbody

    xpath to block with url from page with link to file
    /html/body/table[2]/tbody/tr/td[2]/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/span/b/a
    /html/body/table[2]/tbody/tr/td[2]/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/span/b/a
