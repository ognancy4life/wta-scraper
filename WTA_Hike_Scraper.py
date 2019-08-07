# wta-scraper/WTA_Hike_Scraper.py
#*************************************************************************************
# Programmer: Yoshio Hasegawa
# Class Name: None
# Super Class: None
#
# Revision     Date                        Release Comment
# --------  ----------  --------------------------------------------------------------
#   1.0     5/1/2019   Initial Release
#
# File Description
# ----------------
# Procedural scripts that routes and organizes hike data from www.wta.org.
# https://www.wta.org/go-outside/hikes
#
# Methods
# -------------
#    Name                                     Description
# ----------                          ------------------------------------------------
# get_html_rows()                     Gets HTML code from website.
# get_hike_pages()                    Returns a list of URLs found on
#                                     'https://www.wta.org/go-outside/hikes'.
# get_hikes()                         Returns individual hike links found on
#                                     hike list pages on www.wta.org.
# get_hike_info()                     Returns organizes hike data hosted on
#                                     www.wta.org.
#*************************************************************************************
# Imported Packages:
from bs4 import BeautifulSoup
import requests
import urllib3
from datetime import datetime
import pandas as pd

class WTAScraper():

    #**************************************************************************************
    # Constructor: __init__(self)
    #
    # Description
    # -----------
    # This constructor, once instatiated, will initialize the current date as a class level
    # variable.
    #
    # ------------------------------- Arguments ------------------------------------------
    #        Type               Name                         Description
    # --------------------  ------------  ------------------------------------------------
    # None
    #*************************************************************************************
    def __init__(self):
        self.curr_date = datetime.now().date()

    #*************************************************************************************
    # Method: get_html_rows(self, string)
    #
    # Description
    # -----------
    # Using Requests & BeautifulSoup to request a URLs HTML code. This method returns
    # the HTML code as a list of individual lines.
    #
    # RETurn
    #  Type                            Description
    # ------  ----------------------------------------------------------------------------
    # list    HTML code as a list of individual lines.
    #
    # ------------------------------- Arguments ------------------------------------------
    #        Type               Name                         Description
    # --------------------  ------------  ------------------------------------------------
    # string                url           The URL for the desired HTML code.
    #*************************************************************************************
    def get_html_rows(self, url):
        r = requests.get(url, verify=False)
        s = BeautifulSoup(r.content, 'html5lib')
        html = s.prettify()
        return html.splitlines()

    #*************************************************************************************
    # Method: get_hike_pages(self, string, boolean)
    #
    # Description
    # -----------
    # This method will find all URLs to webpages consisting of a list of hikes and,
    # will return all URLs as a list using recursion. Note, this method does not include
    # 'https://www.wta.org/go-outside/hikes' in the returned list. So, it may be best to
    # append this URL to your final list.
    #
    # RETurn
    #  Type                            Description
    # ------  ----------------------------------------------------------------------------
    # list    A list of URLs to webpages consisting of a list of hikes.
    #
    # ------------------------------- Arguments ------------------------------------------
    #        Type               Name                         Description
    # --------------------  ------------  ------------------------------------------------
    # string                url           This URL should be
    #                                     'https://www.wta.org/go-outside/hikes'
    # boolean               last_page     This method is adjusted through the recursive
    #                                     techniques in order to exit the recursive loop.
    #*************************************************************************************
    def get_hike_pages(self, url, last_page = None):
        print('Getting all links to hike pages...')

        # Retireve HTML code as list of lines.
        rows_list = self.get_html_rows(url)

        check = False
        exit = False
        active_page = 0
        index_start = 0
        index_end = 0

        itr = -1
        # Iterate over the list of HTML lines.
        for row in rows_list:
            itr += 1

            # '"active"' will indicate the starting index point for where the links
            # for hike pages are located in the HTML code. It also allows for the
            # variable storing the link for the active page or current page to
            # be initialized.
            if '"active"' in row:
                index_start = rows_list.index(row)
                active_page = int(rows_list[itr + 2].lstrip())

            # '"last"' will indicate the ending index point for where the links
            # for hike pages are located in the HTML code. It also allows for the
            # variable storing the link for the last page to be initialized.
            # Additionally, if we locate '"last"', we have successfully retrieved
            # all of the hike page links.
            if '"last"' in row:
                index_end = rows_list.index(row)
                last_page = int(rows_list[itr + 2].lstrip())
                check = True
                break
            # check == False means "'last'" was not found.
            # If "'next'" is found we will retrieve the index range for the hike
            # page links found and break from this loop. This also sets the variable
            # 'exit' to True which will end our recursive loop.
            elif check == False and '"next"' in row:
                index_end = rows_list.index(row)
                last_page = int(rows_list[itr - 3].lstrip())
                check = True
                exit = True
                break
            elif check == False and active_page == last_page:
                return

        # Initializing the index range where hike pages are found.
        rows_range = rows_list[index_start : index_end]
        # Initializing the links as a list.
        pages_found = [item[item.find('https') : item.find('">')] for item in rows_range if 'www.wta.org' in item]
        # Initializing the next page to parse through as the first link in the 'pages_found' list.
        next_page = pages_found[0]

        # if 'exit' equals true we will exit our recursive loop. Otherwise, keep running
        # this recursive method.
        if exit == True:
            return pages_found
        else:
            return list(set().union(pages_found, self.get_hike_pages(next_page, last_page)))

    #*************************************************************************************
    # Method: get_hikes(self, list)
    #
    # Description
    # -----------
    # Using a list of URLs to webpages consisting of a list of hikes, this method will
    # find all URLs to webpages consisting of individual hikes found on each of the URLs
    # passed to this method.
    #
    # RETurn
    #  Type                            Description
    # ------  ----------------------------------------------------------------------------
    # list    A list of URLs to webpages consisting of individual hikes.
    #
    # ------------------------------- Arguments ------------------------------------------
    #      Type               Name                         Description
    # ---------------  -----------------  ------------------------------------------------
    # list             hike_page_links    This list should be a list of URLs to webpages
    #                                     consisting of a list of hikes.
    #*************************************************************************************
    def get_hikes(self, hike_page_links):
        print('Getting all links to individual hikes...')

        hike_links_list = []

        # Parse through all links...
        for link in hike_page_links:
            rows_list = self.get_html_rows(link)

            #Parse through HTML code for each link...
            for row in rows_list:

                # Append the individual hike link to a list...
                if "listitem-title" in row:
                    hike_link = row[row.find('https') : row.find('" title=')]
                    hike_links_list.append(hike_link)

        # Return the list containing all individual hike links.
        return hike_links_list

    #*************************************************************************************
    # Method: get_hike_info(self, list)
    #
    # Description
    # -----------
    # Using a list of URLs to webpages consisting of individual hikes, this method will
    # return specific information for each hike in the format of a DataFrame.
    #
    # RETurn
    #  Type                            Description
    # ----------  ------------------------------------------------------------------------
    # DataFrame   A DataFrame consisting of organized hike data.
    #
    # ------------------------------- Arguments ------------------------------------------
    #      Type               Name                         Description
    # ---------------  -----------------  ------------------------------------------------
    # list             hike_urls          This list should be a list of URLs to webpages
    #                                     consisting of individual hikes
    #*************************************************************************************
    def get_hike_info(self, hike_urls):

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
        # Parse through all individual hike links...
        for link in hike_urls:
            # Get HTML code as list of lines.
            hike_rows_list = self.get_html_rows(link)

            itr1 = -1
            # Parse through HTML code...
            for row1 in hike_rows_list:
                itr1 += 1

                # Messy/Hacky initialization of data fields based on
                # HTML code...

                # Retrieving the hike title...
                if '"documentFirstHeading"' in row1:
                    hike_title = hike_rows_list[itr1 + 1].lstrip()
                    titles.append(hike_title)

                # Retrieving the hike region...
                if '"hike-region"' in row1:
                    hike_region = hike_rows_list[itr1 + 3].lstrip()
                    regions.append(hike_region)

                # Retrieving the hike distance and distance type...
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

                # Retrieving the hike gain...
                if 'Gain:' in row1:
                    hike_gain = float(hike_rows_list[itr1 + 2].lstrip())
                    gains.append(hike_gain)

                # Retrieving the hike highest point...
                if 'Highest Point:' in row1:
                    hike_highest = float(hike_rows_list[itr1 + 2].lstrip())
                    highests.append(hike_highest)

                # Retrieving the hike rating...
                if '"current-rating"' in row1:
                    rating_string = hike_rows_list[itr1 + 1].lstrip()
                    hike_rating = float(rating_string[ : rating_string.find(' out of')])
                    ratings.append(hike_rating)

                # Retrieving the hike rating count...
                if '"rating-count"' in row1:
                    rating_count_string = hike_rows_list[itr1 + 1].lstrip()
                    rating_count = int(rating_count_string[rating_count_string.find('(') + 1 : rating_count_string.find(' vote')])
                    rating_counts.append(rating_count)

            # If any of the above data fields were not found,
            # append a None value to the corresponding list in order to
            # keep all lists of data fields in line with each other.
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


            # Retrieve the link for the corresponding trip report and,
            # get the HTML code for that link.
            report_link = link + '/@@related_tripreport_listing'
            report_rows_list = self.get_html_rows(report_link)
            report_date_list = []

            itr2 = -1
            # Parse through the HTML code for the hikes trip report link...
            for row2 in report_rows_list:
                itr2 += 1

                # More Messy/Hacky initialization of data fields based on
                # HTML code...

                # Retrieving the hike trip report counts...
                if '"count-data"' in row2:
                    report_count = int(report_rows_list[itr2 + 1].lstrip())
                    report_counts.append(report_count)

                # Retrieving the hike trip report date...
                if '"elapsed-time"' in row2:
                    report_date = datetime.strptime(row2[row2.find('title="') + 7 : row2.find('">')], '%b %d, %Y')
                    report_date_list.append(report_date)

            # If any of the above data fields were not found,
            # append a None value to the corresponding list in order to
            # keep all lists of data fields in line with each other.
            if len(report_counts) != rownum:
                report_counts.append(None)

            # Special Case: If the trip report date list is not empty,
            # append the first date to the final 'report_dates' list
            # that will be used for creating the final DataFrame.
            # We only want the most recent trip report date.
            if len(report_date_list) != 0:
                report_dates.append(report_date_list[0])
            # Else, append None value... to keep things in line.
            elif len(report_dates) != rownum:
                report_dates.append(None)

            # We want to also want to include a column of the hike links :)
            hike_links.append(link)

            # Print performance...
            print(str(rownum) + ' Hikes loaded...')
            rownum += 1

        # Print more performance stuff...
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

        # Return the final DataFrame that houses all hike data in an organize fashion!
        return pd.DataFrame({'TITLE': titles, 'REGION': regions, 'DISTANCE': distances, 'DIST_TYPE': dist_types,
                            'GAIN': gains, 'HIGHEST': highests, 'RATING': ratings, 'RATING_COUNT': rating_counts,
                            'REPORT_DATE': report_dates, 'REPORT_COUNT': report_counts, 'LINK': hike_links})

    #*************************************************************************************
    # Method: main(self)
    #
    # Description
    # -----------
    # Method main strategically operates the methods of this class for accurate operation.
    #
    # RETurn
    #  Type                            Description
    # ----------  ------------------------------------------------------------------------
    # None
    #
    # ------------------------------- Arguments ------------------------------------------
    #      Type               Name                         Description
    # ---------------  -----------------  ------------------------------------------------
    # None
    #*************************************************************************************
    def main(self):
        # Disabling insecure warnings to avoid printed warnings.
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # Get all hike page links, get all individual hike links, get all hike info and, write to a csv.
        all_hike_page_links = list(set().union(self.get_hike_pages('https://www.wta.org/go-outside/hikes'), ['https://www.wta.org/go-outside/hikes']))
        all_hike_links = self.get_hikes(all_hike_page_links)
        wta_hikes = self.get_hike_info(all_hike_links)
        wta_hikes.to_csv('YOUR_FILE_LOCATION\{0}_wta_hikes.csv'.format(self.curr_date.), index = False)


##########################################################################################
# This if statement will run method main if WTA_Hike_Scraper.py is ran directly.
if __name__ == '__main__':
    wta = WTAScraper()
    wta.main()
