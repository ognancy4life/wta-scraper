# Import relevant packages
from bs4 import BeautifulSoup
import requests
import urllib3
from datetime import datetime
import pandas as pd

# Disabling insecure warnings to avoid printed warnings.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Using Requests & BeautifulSoup...
# Pass a URL to this method and it will return the URL's HTML code as a list of lines.
def get_html_rows(url):
    r = requests.get(url, verify=False)
    s = BeautifulSoup(r.content, 'html5lib')
    html = s.prettify()
    return html.splitlines()

# this method will find all links to pages consisting of a list of hikes and, return all links as a list using recursion.
# Note, this method does not include 'https://www.wta.org/go-outside/hikes' in the returned list.
def get_hike_pages(url, last_page = None):
    print('Getting all links to hike pages...')

    rows_list = get_html_rows(url)

    check = False
    exit = False
    active_page = 0
    index_start = 0
    index_end = 0

    itr = -1
    for row in rows_list:
        itr += 1

        if '"active"' in row:
            index_start = rows_list.index(row)
            active_page = int(rows_list[itr + 2].lstrip())

        if '"last"' in row:
            index_end = rows_list.index(row)
            last_page = int(rows_list[itr + 2].lstrip())
            check = True
            break
        elif check == False and '"next"' in row:
            index_end = rows_list.index(row)
            last_page = int(rows_list[itr - 3].lstrip())
            check = True
            exit = True
            break
        elif check == False and active_page == last_page:
            return

    rows_range = rows_list[index_start : index_end]
    pages_found = [item[item.find('https') : item.find('">')] for item in rows_range if 'www.wta.org' in item]
    next_page = pages_found[0]

    if exit == True:
        return pages_found
    else:
        return list(set().union(pages_found, get_hike_pages(next_page, last_page)))

# Taking a list of links consisting of WTA's pages, that houses their lists of hikes, as a parameter,
# this method will return a list of links to all hikes found on wta.org.
def get_hikes(hike_page_links):
    print('Getting all links to individual hikes...')

    hike_links_list = []

    for link in hike_page_links:
        rows_list = get_html_rows(link)

        for row in rows_list:

            if "listitem-title" in row:
                hike_link = row[row.find('https') : row.find('" title=')]
                hike_links_list.append(hike_link)

    return hike_links_list

# Taking a list of individual hike links as a parameter,
# this method will reutrn specific information for each hike in the format of a DataFrame.
def get_hike_info(hike_urls):

    titles = []
    regions = []
    distances =[]
    dist_types =[]
    gains = []
    highests = []
    ratings = []
    rating_counts =[]
    report_counts =[]
    report_dates = []
    hike_links =[]

    rownum = 1
    for link in hike_urls:
        hike_rows_list = get_html_rows(link)

        itr1 = -1
        for row1 in hike_rows_list:
            itr1 += 1

            if '"documentFirstHeading"' in row1:
                hike_title = hike_rows_list[itr1 + 1].lstrip()
                titles.append(hike_title)

            if '"hike-region"' in row1:
                hike_region = hike_rows_list[itr1 + 3].lstrip()
                regions.append(hike_region)

            if '"distance"' in row1:
                hike_distance_string = hike_rows_list[itr1 + 2].lstrip()
                hike_distance = float(hike_distance_string[ : hike_distance_string.find(' mile')])
                if ',' in hike_distance_string:
                    hike_distance_type = hike_distance_string[hike_distance_string.find(', ') + 2 : ]
                elif 'of trails' in hike_distance_string:
                    hike_distance_type = hike_distance_string[hike_distance_string.find('of trails') + 3 : ]
                else:
                    hike_distance = 'ERROR'
                distances.append(hike_distance)
                dist_types.append(hike_distance_type)

            if 'Gain:' in row1:
                hike_gain = float(hike_rows_list[itr1 + 2].lstrip())
                gains.append(hike_gain)

            if 'Highest Point:' in row1:
                hike_highest = float(hike_rows_list[itr1 + 2].lstrip())
                highests.append(hike_highest)

            if '"current-rating"' in row1:
                rating_string = hike_rows_list[itr1 + 1].lstrip()
                hike_rating = float(rating_string[ : rating_string.find(' out of')])
                ratings.append(hike_rating)

            if '"rating-count"' in row1:
                rating_count_string = hike_rows_list[itr1 + 1].lstrip()
                rating_count = int(rating_count_string[rating_count_string.find('(') + 1 : rating_count_string.find(' vote')])
                rating_counts.append(rating_count)

        if len(titles) != rownum:
            titles.append(None)

        if len(regions) != rownum:
            regions.append(None)

        if len(distances) != rownum:
            distances.append(None)

        if len(dist_types) != rownum:
            dist_types.append(None)

        if len(gains) != rownum:
            gains.append(None)

        if len(highests) != rownum:
            highests.append(None)

        if len(ratings) != rownum:
            ratings.append(None)

        if len(rating_counts) != rownum:
            rating_counts.append(None)


        report_link = link + '/@@related_tripreport_listing'
        report_rows_list = get_html_rows(report_link)
        report_date_list = []

        itr2 = -1
        for row2 in report_rows_list:
            itr2 += 1

            if '"count-data"' in row2:
                report_count = int(report_rows_list[itr2 + 1].lstrip())
                report_counts.append(report_count)

            if '"elapsed-time"' in row2:
                report_date = datetime.strptime(row2[row2.find('title="') + 7 : row2.find('">')], '%b %d, %Y')
                report_date_list.append(report_date)

        if len(report_counts) != rownum:
            report_counts.append(None)

        if len(report_date_list) != 0:
            report_dates.append(report_date_list[0])
        elif len(report_dates) != rownum:
            report_dates.append(None)

        hike_links.append(link)

        print(str(rownum) + ' Hikes loaded...')
        rownum += 1

    print('Finished loading hikes!\n' + str(rownum - 1) + ' Hikes successfully loaded.\n')
    print('titles: ', len(titles), ' entries')
    print('regions: ', len(regions), ' entries')
    print('distances: ', len(distances), ' entries')
    print('dist_types: ', len(dist_types), ' entries')
    print('gains: ', len(gains), ' entries')
    print('highests: ', len(highests), ' entries')
    print('ratings: ', len(ratings), ' entries')
    print('rating_counts: ', len(rating_counts), ' entries')
    print('report_dates: ', len(report_dates), ' entries')
    print('report_counts: ', len(report_counts), ' entries')
    print('hike_links: ', len(hike_links), ' entries')

    return pd.DataFrame({'TITLE': titles, 'REGION': regions, 'DISTANCE': distances, 'DIST_TYPE': dist_types,
                        'GAIN': gains, 'HIGHEST': highests, 'RATING': ratings, 'RATING_COUNT': rating_counts,
                        'REPORT_DATE': report_dates, 'REPORT_COUNT': report_counts, 'LINK': hike_links})


curr_date = datetime.now().date()
# Get all hike page links, get all individual hike links, get all hike info and, write to a csv.
all_hike_page_links = list(set().union(get_hike_pages('https://www.wta.org/go-outside/hikes'), ['https://www.wta.org/go-outside/hikes']))
all_hike_links = get_hikes(all_hike_page_links)
wta_hikes = get_hike_info(all_hike_links)
wta_hikes.to_csv('YOUR_FILE_LOCATION\{0}_wta_hikes.csv'.format(curr_date), index = False)
