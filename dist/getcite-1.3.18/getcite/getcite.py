#    getcite was created to save Florida Law Review member's time by automating
#    the process called "pulling sources."
#
#    Copyright (C) 2015 Samuel Alexander
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    You can reach the author at: salexander2000@gmail.com
#
#   TO DO:
#   8) Determine which firefox preferences we can do without
#   9) Add wait/timeout function to original gets, so that if pages don't load, it times out
#   11) Make "quit" available at every prompt
#   12) Huge: add state statutes.
#   13) Add a "copy" command, that allows the user to copy the last downloaded source but 
#       change the footnotes when source is saved (for footnotes w/ ids. for example)
#   15) Add more info to each "timed out" function to say what exactly was happening
#   16) In the Westlaw function, determine whether it's a statute by presence of Notes of Dec.
#           if it's a case, go straight to westlaw PDF download rather than original image
#   17) Make the "article" command work like "history" and "rename": with a colon.
#   18) See if you can use the element class function is_enabled more! Much more useful than
#       wait and click.
#
#
#   Currently supported functionality:
#     Downloading
#       cases with pdf on westlaw, default presumption
#       supreme court cases on heinonline, automatically detected by presence of " U.S. "
#       united states code on heinonline, automatically detected by presence of " U.S.C. "
#       law review articles, but this type of search must be specified by user
#     Naming
#       helping users name automatically downloaded files
#       allowing users to rename most recently downloaded file, if download must be completed
#           manually
#     Shepardizing
#       cases and statutes on westlaw;
#       uses auto-naming features;
#       automatically concatenates PDFs when multiple histories are downloaded
#           e.g. cases with both negative treatment and case history;
#     
#     History:
#       1.0.0       Original functions: cases, law review articles, sup. ct. cases, fed stats
#       1.1.0       Added statute validity from westlaw
#       1.2.0       Added case history from westlaw
#       1.3.0       Added detection/creation of history and source folders, and removal to those folders


import os
import getpass
import re
import time
from PyPDF2 import PdfFileMerger, PdfFileReader
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

if os.name == 'nt':
    DOWNLOAD_DIR = "C:"+os.environ['HOMEPATH']+"\\Downloads"
    HISTORY_DIR = "\\Shepards"
    SOURCE_DIR = "\\Sources"
else:
    DOWNLOAD_DIR = os.environ['HOME']+"/Downloads"
    HISTORY_DIR = "/Shepards/"
    SOURCE_DIR = "/Sources/"
VERSION_NUM = "1.3.18"
editor_abbreviation = None
author_abbreviation = None


def rename_source_history(citation, number_of_files_downloaded, type):
    
    print ("Downloading... \nPlease let download complete before entering the footnote number.")

    # check how many history files were downloaded. If only one, no need to merge.
    if number_of_files_downloaded < 2:

        # see if the user wants to save with a different name, like a case name, instead of a citation
        saved_name = None
        
        saved_name = input("If you'd like to save the validity or history output with a name other \
than the citation, enter it.\nOtherwise, press enter to keep the same name, \
or type \"stop\" to go back: ")
        if len(saved_name) > 0:
            citation = saved_name

        if "stop" in saved_name:
            return
                               
        footnote_number = input("Please enter a footnote number, e.g. 001 or 001(3): ")
        
        # change to the download directory
        os.chdir(DOWNLOAD_DIR)

        # make sure there is a source directory. If there's not... make it!
        if not os.path.exists(DOWNLOAD_DIR+HISTORY_DIR):
            os.makedirs(DOWNLOAD_DIR+HISTORY_DIR)


        # create a list from all the files (excluding directories) in the direcory
        files = filter(os.path.isfile, os.listdir(DOWNLOAD_DIR))

        # add directory path to the file name
        files = [os.path.join(DOWNLOAD_DIR, f) for f in files]

        # sort the list by most recently modified
        files.sort(key = lambda x: os.path.getmtime(x))

        # on a Mac, .DS_Store is updated frequently. So, if that's the most recently
        # modified file, use the next newest file.
        if ".DS_Store" in files[-1]:
            newest_file = files[-2]
        else:
            newest_file = files[-1]
        print(newest_file)

        print("Moving to history directory...")
        os.rename(newest_file, DOWNLOAD_DIR+HISTORY_DIR+author_abbreviation+" "+footnote_number+" "+citation+" "+type+" "+editor_abbreviation+".pdf")

        print("File saved as: %s" % author_abbreviation+" "+footnote_number+" "+citation+" "+type+" "+editor_abbreviation+".pdf")
    else:
        # more than one source history was downloaded. Merge them.

        # see if the user wants to save with a different name, like a case name, instead of a citation
        saved_name = None
        
        saved_name = input("If you'd like to save history output with a name other \
than the citation, enter it.\nOtherwise, press enter to keep the same name, \
or type \"stop\" to go back: ")
        if len(saved_name) > 0:
            citation = saved_name

        if "stop" in saved_name:
            return
                               
        footnote_number = input("Please enter a footnote number, e.g. 001 or 001(3): ")

        os.chdir(DOWNLOAD_DIR)

        # make sure there is a source directory. If there's not... make it!
        if not os.path.exists(DOWNLOAD_DIR+HISTORY_DIR):
            os.makedirs(DOWNLOAD_DIR+HISTORY_DIR)


        print("More than one PDF downloaded... getcite will attempt to merge the files.")

        # create a list from all the files (excluding directories) in the direcory
        files = filter(os.path.isfile, os.listdir(DOWNLOAD_DIR))

        # add directory path to the file name
        files = [os.path.join(DOWNLOAD_DIR, f) for f in files]

        # sort the list by most recently modified
        files.sort(key = lambda x: os.path.getmtime(x))

        # on a Mac, .DS_Store is updated frequently. So, if that's the most recently
        # modified file, use the next newest file.
        newest_files = []

        if ".DS_Store" in files[-1]:
            newest_files.append(files[-2])
            newest_files.append(files[-3])
        else:
            newest_files.append(files[-1])
            newest_files.append(files[-2])

        # MERGING CODE goes here

        print("Creating output file...")
        merger = PdfFileMerger()

        print("Appending most recently downloaded files to output file...")
        for filename in newest_files:
            merger.append(filename)

        print("Writing the combined file and deleting the old files...")
        merger.write(author_abbreviation+" "+footnote_number+" "+citation+" "+type+" "+editor_abbreviation+".pdf")

        for filename in newest_files:
            os.remove(filename)

        # MOVE THE MERGED FILE
        # need to check new files again, before moving
        # create a list from all the files (excluding directories) in the direcory
        print("Moving to history directory...")
        files = filter(os.path.isfile, os.listdir(DOWNLOAD_DIR))

        # add directory path to the file name
        files = [os.path.join(DOWNLOAD_DIR, f) for f in files]

        # sort the list by most recently modified
        files.sort(key = lambda x: os.path.getmtime(x))

        # on a Mac, .DS_Store is updated frequently. So, if that's the most recently
        # modified file, use the next newest file.
        newest_file_for_moving = None

        if ".DS_Store" in files[-1]:
            newest_file_for_moving = files[-2]
        else:
            newest_file_for_moving = files[-1]

        # move it to the history directory
        os.rename(newest_file_for_moving, DOWNLOAD_DIR+HISTORY_DIR+author_abbreviation+" "+footnote_number+" "+citation+" "+type+" "+editor_abbreviation+".pdf")

        print("File saved as: %s" % author_abbreviation+" "+footnote_number+" "+citation+" "+type+" "+editor_abbreviation+".pdf")
    return

def rename_most_recent_manually_downloaded_source(citation):
    # rename usage:
    # in the get citation loop, type: rename:"name or citation to use":footnote_number
    # for example: rename:"Shakur v. Smalls":007(2)
    # would save the file as "author_abbreviation 007(2) Shakur v. Smalls editor_abbreviation.pdf"

    rename_options = citation.split(":")
    if len(rename_options) != 3:
        print("Renaming is performed as follows: rename:name or citation:footnote_number\n\
For example: rename:Shakur v. Smalls:007(2)")
        return
    
    # change to the download directory
    os.chdir(DOWNLOAD_DIR)

    # create a list from all the files (excluding directories) in the direcory
    files = filter(os.path.isfile, os.listdir(DOWNLOAD_DIR))
                           
    # add directory path to the file name
    files = [os.path.join(DOWNLOAD_DIR, f) for f in files]

    # sort the list by most recently modified
    files.sort(key = lambda x: os.path.getmtime(x))

    # on a Mac, .DS_Store is updated frequently. So, if that's the most recently
    # modified file, use the next newest file.
    if ".DS_Store" in files[-1]:
        newest_file = files[-2]
    else:
        newest_file = files[-1]
    print(newest_file)
    os.rename(newest_file, author_abbreviation+" "+rename_options[2]+" "+rename_options[1]+" "+editor_abbreviation+".pdf")

    print("File saved as: %s" % author_abbreviation+" "+rename_options[2]+" "+rename_options[1]+" "+editor_abbreviation+".pdf")
    return

def rename_saved_source(citation):

    print ("Downloading... \nPlease let download complete before entering the footnote number.")

    # see if the user wants to save with a different name, like a case name, instead of a citation
    saved_name = None
    
    saved_name = input("If you'd like to save with a name other \
than the citation, enter it.\nOtherwise, press enter to keep the same name, \
or type \"stop\" to go back: ")
    if len(saved_name) > 0:
        citation = saved_name

    if "stop" in saved_name:
        return
                           
    footnote_number = input("Please enter a footnote number, e.g. 001 or 001(3): ")

    # change to the download directory
    os.chdir(DOWNLOAD_DIR)

    # make sure there is a source directory. If there's not... make it!
    if not os.path.exists(DOWNLOAD_DIR+SOURCE_DIR):
        os.makedirs(DOWNLOAD_DIR+SOURCE_DIR)

    # create a list from all the files (excluding directories) in the direcory
    files = filter(os.path.isfile, os.listdir(DOWNLOAD_DIR))

    # add directory path to the file name
    files = [os.path.join(DOWNLOAD_DIR, f) for f in files]

    # sort the list by most recently modified
    files.sort(key = lambda x: os.path.getmtime(x))

    # on a Mac, .DS_Store is updated frequently. So, if that's the most recently
    # modified file, use the next newest file.
    if ".DS_Store" in files[-1]:
        newest_file = files[-2]
    else:
        newest_file = files[-1]
    print(newest_file)

    # move to source directory
    print("Moving to source directory...")
    os.rename(newest_file, DOWNLOAD_DIR+SOURCE_DIR+author_abbreviation+" "+footnote_number+" "+citation+" "+editor_abbreviation+".pdf")

    print("File saved as: %s" % author_abbreviation+" "+footnote_number+" "+citation+" "+editor_abbreviation+".pdf")
    return

def get_westlaw_history(citation, driver, with_args):


    # if comes with arguments, split it. Otherwise, just use the previous citation.
    if with_args == True:
        argument = citation.split(":")
    else:
        argument = [None, citation] # all the later parts of this function use argument[1] as 
                                    # the citation... so need user filler
                                    # could probably insert, but don't know how yet

    number_of_files_downloaded = 0
    is_statute = False # default this to false, if getcite finds a statute, change to True and don't
                        # look for history besides validity

    # tell the user what's happening
    print("Searching WestLaw for the source history...")

    # go to westlaw
    driver.get("http://a.next.westlaw.com")

    # determine whether logged in or not. If not, log in.
    if "Signon" in driver.title:
        # for now, just use my name and password
        print("getcite has not logged into WestLaw yet...")
        username = input("Please enter your WestLaw username: ")
        password = getpass.getpass("Password: ")
        elem = driver.find_element_by_name("Username")
        elem.send_keys(username)
        elem = driver.find_element_by_name("Password")
        elem.send_keys(password)
        elem.send_keys(Keys.RETURN)
        try:
            # press the continue button
            elem = driver.find_element_by_id("co_clientIDContinueButton")
            elem.click()
        except NoSuchElementException:
            print("Unable to login.\nAre you sure your username and password are correct")
            return

    # wait for the search box to appear
    wait = WebDriverWait(driver, 10)
    print("Locating...")
    elem = wait.until(EC.presence_of_element_located((By.ID, "searchInputId")))

    # enter the citation and click "Search"
    elem.send_keys(argument[1])
    elem = driver.find_element_by_id("searchButton")
    elem.click()


    # see if there is a notes of dec. tab. If so, it's a statute. Download validity and exit function.
    try:
        wait = WebDriverWait(driver, 4)
        # use notes of decision, because it's a good 
        elem = wait.until(EC.presence_of_element_located((By.ID, "coid_relatedInfo_riNotesOfDecisions_link")))
        print("Found a statute... getting validity.")
        is_statute = True

        # found a statute, click history. Now that we know there's a statute spec. anchor, could
        # just use that instead of looking at notes of decision
        try:
            wait = WebDriverWait(driver, 6)
            elem = wait.until(EC.presence_of_element_located((By.ID, "co_StatuteHistoryNavAnchor")))
            elem.click()

            # see if validity has content
            wait = WebDriverWait(driver, 6)
            elem = wait.until(EC.presence_of_element_located((By.ID, "coid_relatedInfo_subCategory_linkkcValidity")))
            
            if elem.is_enabled():
                validity_history = 1 # there is a history
            else:
                validity_history = None # there is no history


            #print("Seeing if validity contains 0")
            # but set to None if '0' is in the Validity string, e.g. "Validity (0)"
            #if not re.match('^[A-Za-z1-9 ()]+$', elem.text):
            #    print("No validity history for this statute.")
            #    validity_history = None

            if validity_history != None:
                # click validity
                try:
                    wait = WebDriverWait(driver, 4)
                    elem = wait.until(EC.presence_of_element_located((By.ID, "coid_relatedInfo_subCategory_linkkcValidity")))

                    elem.click()

                    # now download
                    try:
                        # click the download button
                        print("Attempting to download Westlaw validity output in PDF format...")
                        wait = WebDriverWait(driver, 4)
                        elem = wait.until(EC.presence_of_element_located((By.ID, "deliveryLink1")))
                        elem.click()

                        # apparently takes some time
                        time.sleep(2)

                        # first wait until PDF shows up
                        wait = WebDriverWait(driver, 4)
                        elem = wait.until(EC.presence_of_element_located((By.ID, "co_delivery_format_fulltext")))

                        # takes time
                        time.sleep(3)

                        # only then click download button
                        elem = wait.until(EC.presence_of_element_located((By.ID, "co_deliveryDownloadButton")))
                        elem.click()

                        # click the *next* download button, also sleeping
                        time.sleep(3)
                        wait = WebDriverWait(driver, 6)
                        elem = wait.until(EC.presence_of_element_located((By.ID, "coid_deliveryWaitMessage_downloadButton")))
                        elem.click()

                        number_of_files_downloaded = number_of_files_downloaded + 1
                        rename_source_history(argument[1], number_of_files_downloaded, type="Validity")
                        return
                    except TimeoutException:
                        print("Timed out while trying to download validity.")
                        return
                    except NoSuchElementException:
                        print("Could not download validity.")
                        return
                except TimeoutException:
                    print("Timed out while trying to get statute validity. Statute may not have validity history.")
                    return
                except NoSuchElementException:
                    print("Could not get statute validity.")
                except ElementNotVisibleException:
                        print("Statute does not have a validity history.")
                        return
            else:
                print("No validity history for this statute.")
        except TimeoutException:
            print("Timed out while attempting to get statute history. May not have a validity history.")
            return
        except NoSuchElementException:
            print("Could not find statute history.")
            return
        except ElementNotVisibleException:
            print("No validity history for this statute.")
    except TimeoutException:
        # if not here, then probably a case, just allow to go on.
        pass
    except NoSuchElementException:
        pass

    # after looking for statute, because this take a while to load, make sure you
    # don't use Westlaw's download button if you're on the search page
    if "Search" in driver.title:
        print("Could not find source. Please try again.")
        return

    if is_statute == False:
        # If not a statute, try to find histories
        print("Found a case... getting history.")

        # first the negative history
        try:
            wait = WebDriverWait(driver, 4)
            elem = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Negative Treatment")))
            negative_history = 1 # this is a case

            # then see if a pinpoint, if so, return
            try:
                wait = WebDriverWait(driver, 3)
                elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co_pinpointIcon")))
                print("Pinpoint citation detected. Please enter full citation.")
                return
            except NoSuchElementException:
                pass
            except TimeoutException:
                pass

            wait = WebDriverWait(driver, 4)
            elem = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Negative Treatment")))

            # see if there are actually negative cases. If not, set the negative history to None.
            # if not re.match('^[A-zA-z1-9() ]+$',elem.text): FIND ANOTHER WAY!!!
            # This is much better: if 1-9 is detected, then there is a negative history
            if re.search('[1-9]', elem.text) == None:
                print("No negative history...")
                negative_history = None


            # if negative_history is not None, i.e. has negative history, let it load, then download.
            if negative_history != None:
                wait = WebDriverWait(driver, 4)
                elem = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Negative Treatment")))
                elem.click()


                print("Attempting to download negative treatment history in PDF format...")
                wait = WebDriverWait(driver, 6)
                elem = wait.until(EC.presence_of_element_located((By.ID, "deliveryLink1")))
                elem.click()

                # apparently takes some time
                time.sleep(2)

                # first wait until PDF shows up
                wait = WebDriverWait(driver, 6)
                elem = wait.until(EC.presence_of_element_located((By.ID, "co_delivery_format_fulltext")))

                # no see if there are more than 20 items, if so, this element should be present
                try:
                    wait = WebDriverWait(driver, 2)
                    elem = wait.until(EC.presence_of_element_located((By.ID, "coid_RecipientDeliverAsListCount")))
                    # if it's there, select all the items
                    try:
                        # try and find the "all" option
                        for option in elem.find_elements_by_tag_name("option"):
                            if "All" in option.text:
                                option.click()                
                    except TimeoutException:
                        # if timed out, just move on and press download 
                        return
                    except NoSuchElementException:
                        print("Should not be here. Contact developer.")
                        return
                except NoSuchElementException:
                    # if there are less than 20 items, just press download
                    pass
                except TimeoutException:
                    pass

                # only then click download button
                elem = wait.until(EC.presence_of_element_located((By.ID, "co_deliveryDownloadButton")))
                elem.click()

                # click the *next* download button, also sleeping
                time.sleep(3)
                wait = WebDriverWait(driver, 6)
                elem = wait.until(EC.presence_of_element_located((By.ID, "coid_deliveryWaitMessage_downloadButton")))
                elem.click()

                number_of_files_downloaded = number_of_files_downloaded + 1
            else:
                pass
        except TimeoutException:
                print("Timed out.")
                return
        except NoSuchElementException:
                pass
        
        # then all the case history
        try:
            # press the history button
            try:
                wait = WebDriverWait(driver, 10)
                elem = wait.until(EC.presence_of_element_located((By.ID, "coid_relatedInfo_kcJudicialHistory_link")))

                # see if there are actually negative cases. If not, set the negative history to None.
                # if not re.match('^[A-zA-z1-9() ]+$',elem.text): FIND ANOTHER WAY!             
                if re.search('[1-9]', elem.text) == None:
                    print("No case history...")
                    case_history = None
                else:
                    case_history = 1
                    elem.click()

            except NoSuchElementException:
                "History button not found."
                return
            except TimeoutException:
                "Timed out."
                return

            if case_history != None:
                print("Attempting to download case history in PDF format...")

                wait = WebDriverWait(driver, 6)
                elem = wait.until(EC.presence_of_element_located((By.ID, "deliveryLink1")))
                elem.click()

                # apparently takes some time
                time.sleep(3)

                # first wait until PDF shows up
                wait = WebDriverWait(driver, 4)
                elem = wait.until(EC.presence_of_element_located((By.ID, "co_delivery_format_fulltext")))

                # only then click download button
                elem = wait.until(EC.presence_of_element_located((By.ID, "co_deliveryDownloadButton")))
                elem.click()

                # click the *next* download button, also sleeping
                time.sleep(3)
                wait = WebDriverWait(driver, 6)
                elem = wait.until(EC.presence_of_element_located((By.ID, "coid_deliveryWaitMessage_downloadButton")))
                elem.click()

                number_of_files_downloaded = number_of_files_downloaded + 1
        except NoSuchElementException:
                print("No history.")
        except TimeoutException:
                print("Timed out.")
                return

    if number_of_files_downloaded > 0:
            rename_source_history(argument[1], number_of_files_downloaded, type="History")

    return

def get_law_review_article_from_hein_online(citation, driver):

    # split the arguments
    argument = citation.split(":")
    if len(argument) < 2:
        print("\"article\" takes an argument. Please type \"help\" for more information.")
        return

    # tell the user what's happening
    print("Searching HeinOnline.org for law review article...")
    
    # go to heinonline, direct to main page and skipping intro page
    driver.get("http://heinonline.org/HOL/Welcome")

    print("Locating...")

    # make sure we're searching for citations and not for text, also make sure we're logged in
    try:
        wait = WebDriverWait(driver, 4)
        elem = wait.until(EC.presence_of_element_located((By.ID, "citation_tab")))
        elem.click()
    except TimeoutException:
        print("HeinOnline search not available.\nIf you're not on the local network, make sure you're connected to the VPN.")
        return
    except NoSuchElementException:
        print ("HeinOnline search not available.\nIf you're not on the local network, make sure you're connected to the VPN.")
        return


    # enter the citation and hit enter
    # could also find magnifying glass and click it
    elem = driver.find_element_by_id("citation_terms")
    elem.send_keys(argument[1])
    elem.send_keys(Keys.RETURN)
    
    # click download pdf
    try:
        print("Attempting to download law review article...")
        wait = WebDriverWait(driver, 8)
        elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "updatediv")))
        elem.click()
    except TimeoutException:
        print("Timed out.")
        return
    except NoSuchElementException:
        print("PDF not immediately available. Please locate source manually")
        return

    # change downloaded source's name to proper format
    rename_saved_source(argument[1])

    return

def get_heinonline_usc_statute(citation, driver):
    # tell the user what's happening
    print("Searching HeinOnline.org for statute in U.S. Code...")
    
    # go to heinonline, direct to main page and skipping intro page
    driver.get("http://heinonline.org/HOL/Welcome")

    print("Locating...")

    # click on U.S. code, also make sure we're logged in
    try:
        wait = WebDriverWait(driver, 4)
        elem = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "U.S. Code")))
        elem.click()
    except TimeoutException:
        print("Timed out.")
        return
    except NoSuchElementException:
        print("HeinOnline search not available.\nIf you're not on the local network, make sure you're connected to the VPN.")
        return

    # click on United States Code
    try:
        wait = WebDriverWait(driver, 8)
        elem = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "United States Code")))
        elem.click()
    except TimeoutException:
        print("Timed out.")
        return
    except NoSuchElementException:
        print("HeinOnline search not available.\nIf you're not on the local network, make sure you're connected to the VPN.")
        
                         
    # break citation into its constituent parts
    usc_citation = citation.split()

    # input the statute title number
    elem = driver.find_element_by_id("title_num")
    elem.send_keys(usc_citation[0])

    # if citation has four parts, assume user entered a section symbol and
    # use the fourth part of the entry, otherwise use third
    if len(usc_citation) == 4:
        elem = driver.find_element_by_id("part")
        elem.send_keys(usc_citation[3])
    else:
        elem = driver.find_element_by_id("part")
        elem.send_keys(usc_citation[2])

    # press enter
    elem.send_keys(Keys.RETURN)

    # click download pdf
    try:
        print("Attempting to download...")
        wait = WebDriverWait(driver, 4)
        elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "updatediv")))
        elem.click()
        ## elem = driver.find_element_by_class_name("updatediv") //do it without waiting
    except TimeoutException:
        print("Timed out.")
        return
    except NoSuchElementException:
        print("PDF not immediately available. Please locate source manually")
        return

    # change downloaded source's name to proper format
    rename_saved_source(citation)
    
    return

def get_westlaw_citation(citation, driver):
    # tell the user what's happening
    print("Searching WestLaw for the source...")

    # go to westlaw
    driver.get("http://a.next.westlaw.com")

    # determine whether logged in or not. If not, log in.
    if "Signon" in driver.title:
        # for now, just use my name and password
        print("getcite has not logged into WestLaw yet...")
        username = input("Please enter your WestLaw username: ")
        password = getpass.getpass("Password: ")
        elem = driver.find_element_by_name("Username")
        elem.send_keys(username)
        elem = driver.find_element_by_name("Password")
        elem.send_keys(password)
        elem.send_keys(Keys.RETURN)
        try:
            # press the continue button
            elem = driver.find_element_by_id("co_clientIDContinueButton")
            elem.click()
        except NoSuchElementException:
            print("Unable to login.\nAre you sure your username and password are correct")
            return

    # wait for the search box to appear
    wait = WebDriverWait(driver, 10)
    print("Locating...")
    elem = wait.until(EC.presence_of_element_located((By.ID, "searchInputId")))

    # enter the citation and click "Search"
    elem.send_keys(citation)
    elem = driver.find_element_by_id("searchButton")
    elem.click()

    # wait for the Original PDF link to appear, then click it
    try:
        print("Attempting to download source...")
        wait = WebDriverWait(driver, 4)
        elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co_blobLink")))
        elem.click()

        # see if a pinpoint, can't download yet
        try:
            wait = WebDriverWait(driver, 3)
            elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co_pinpointIcon")))
            print("Pinpoint citation detected. Please enter full citation.")
            return
        except NoSuchElementException:
            pass
        except TimeoutException:
            pass

        # if not pinpoint, download then change downloaded source's name to proper format, and
        # exit this function
        rename_saved_source(citation)
        return
    except TimeoutException:
        ## it could be that even if there is no original source, it's still a pinpoint, in which
        # case we don't want to download. So check again, and if pinpoint, exit function. Otherwise
        # continue on to download Westlaw PDF output
        try:
            wait = WebDriverWait(driver, 3)
            elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co_pinpointIcon")))
            print("Pinpoint citation detected. Please enter full citation.")
            return
        except NoSuchElementException:
            pass
        except TimeoutException:
            pass
            print("Timed out.")

    # don't use Westlaw's download button if you're on the search page
    if "Search" in driver.title:
        print("Could not find source. Please try again.")
        return

    # if Westlaw original PDf is unavailable, get the Westlaw output in PDF
    # format by 
    try:
        # click the download button
        print("Attempting to download Westlaw output in PDF format...")
        wait = WebDriverWait(driver, 4)
        elem = wait.until(EC.presence_of_element_located((By.ID, "deliveryLink1")))
        elem.click()

        # apparently takes some time
        time.sleep(3)

        # first wait until PDF shows up
        wait = WebDriverWait(driver, 4)
        elem = wait.until(EC.presence_of_element_located((By.ID, "co_delivery_format_fulltext")))

        # only then click download button
        elem = wait.until(EC.presence_of_element_located((By.ID, "co_deliveryDownloadButton")))
        elem.click()

        # click the *next* download button, also sleeping
        time.sleep(3)
        wait = WebDriverWait(driver, 6)
        elem = wait.until(EC.presence_of_element_located((By.ID, "coid_deliveryWaitMessage_downloadButton")))
        elem.click()
        
        # change downloaded source's name...
        rename_saved_source(citation)
        return

    except TimeoutException:
        print("Could not find any PDF versions of the source.")
        return

        
def get_heinonline_sc_citation(citation, driver):
    # tell the user what's happening
    print("Searching HeinOnline.org for a Supreme Court case...")
    
    # go to heinonline, direct to main page and skipping intro page
    driver.get("http://heinonline.org/HOL/Welcome")

    print("Locating...")

    # make sure we're searching for citations and not for text, also make sure we're logged in
    try:
        wait = WebDriverWait(driver, 4)
        elem = wait.until(EC.presence_of_element_located((By.ID, "citation_tab")))
        elem.click()
    except TimeoutException:
        print("HeinOnline search not available.\nIf you're not on the local network, make sure you're connected to the VPN.")
        return
    except NoSuchElementException:
        print("HeinOnline search not available.\nIf you're not on the local network, make sure you're connected to the VPN.")
        return


    # enter the citation and hit enter
    # could also find magnifying glass and click it
    elem = driver.find_element_by_id("citation_terms")
    elem.send_keys(citation)
    elem.send_keys(Keys.RETURN)
    
    # click the heinonline pdf version
    try:
        wait = WebDriverWait(driver, 8)
        elem = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "PDF version")))
        elem.click()
    except TimeoutException:
        print("Timed out.")
        return
    
    # click download pdf
    try:
        print("Attempting to download...")
        wait = WebDriverWait(driver, 8)
        elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "updatediv")))
        elem.click()

        rename_saved_source(citation)
        return
        ## elem = driver.find_element_by_class_name("updatediv") //do it without waiting
    except TimeoutException:
        print("Timed out.")
        return
    except NoSuchElementException:
        print("PDF not immediately available.")
        return

    return

def get_driver(profile):
    # get firefox driver (start firefox)
    # using profile created in create_browser_profile()

    driver = webdriver.Firefox(firefox_profile=profile)
    return driver
 
def introduction():

    # clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # print getcite introductio
    print("getcite "+VERSION_NUM+" (c) 2015")

    # give an appropriate greeting, dependent on the time of day
    current_time = datetime.now().time()
    if current_time.hour < 12:
        print("Good morning, Reviewer!")
    elif 12 <= current_time.hour < 17:
        print("Good afternoon, Reviewer!")
    else:
        print("Working the night shift, eh?")

    return
    
    
def create_browser_profile():
    # change profile to remove download dialog box
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.useWindow', False)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', DOWNLOAD_DIR)
    profile.set_preference('browser.download.manager.focusWhenStarting', False)
    profile.set_preference('browser.helperApps.alwaysAsk.force', False)
    profile.set_preference('services.sync.prefs.sync.browser.download.manager.showWhenStarting', False)
    profile.set_preference('pdfjs.disabled', True)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')
    return profile

def main():
    introduction()
    profile = create_browser_profile()
    driver = get_driver(profile)

    # ask user for EDITOR name abbreviation
    global editor_abbreviation
    editor_abbreviation = input("Please enter your two-letter EDITOR abbreviation: ")
    if editor_abbreviation.lower() == "quit":
        driver.close()
        return

    # ask user for AUTHOR name abbreviation
    global author_abbreviation
    author_abbreviation = input("Please enter the two-letter AUTHOR abbreviation: ")
    if author_abbreviation.lower() == "quit":
        driver.close()
        return

    # ask user for citation
    citation = None
    prev_citation = None
    commands = ["article", "help", "history", "rename"]

    citation_history = []
    while True:
        # save the last citation, for history
        prev_citation = citation
        prev_citation_is_command = False

        # get input
        citation = input("Please enter your citation, a command, or \"help\": ")

        # make sure only the proper characters
        if not re.match('^[A-Za-z0-9. &§:()-]+$', citation):
            print("Unknown characters. Please try again.")
        elif "quit" == citation.lower():
            break
        elif "rename" in citation.lower():
            rename_most_recent_manually_downloaded_source(citation)
        elif "article" in citation.lower():
            get_law_review_article_from_hein_online(citation, driver)
        elif "history" in citation.lower():
            if ":" in citation.lower():
                get_westlaw_history(citation, driver, with_args=True)
            else:
                # first, check to see if there is a previous citation
                if prev_citation == None:
                    print("Last entry must be a pure citation before using \"history\" without arguments.")
                else:
                    # now, check to see if previous citation is just a command
                    for command in commands:
                        if command in prev_citation:
                            print("Last entry must be a pure citation before using \"history\" without arguments.")
                            prev_citation_is_command = True
                            break
                    # if so, exit
                    if prev_citation_is_command:
                        pass
                    # otherwise, get the history
                    else:
                        get_westlaw_history(prev_citation, driver, with_args=False)
        elif " u.s. " in citation.lower():
            get_heinonline_sc_citation(citation, driver)
        elif " u.s.c. " in citation.lower():
            get_heinonline_usc_statute(citation, driver)
        elif "license" == citation.lower():
            print("    Copyright (C) 2015 Samuel Alexander\n\n\
    This program is free software: you can redistribute it and/or modify it under\n\
    the terms of the GNU General Public License as published by the Free Software \n\
    Foundation, either version 3 of the License, or (at your option) any later\n\
    version. See LICENSE in the source folder.")
        elif "warranty" == citation.lower():
            print("    This program is distributed in the hope that it will be useful, but WITHOUT\n\
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or \n\
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for \n\
    more details.\n\n\
    You should have received a copy of the GNU General Public License along with \n\
    this program.  If not, see <http://www.gnu.org/licenses/>.")
        elif "help" == citation.lower():
            print("    quit        closes the browser and quits getcite\n\n\
    article     tells getcite that the argument entered will be a law\n\
                review article citation\n\n\
                USAGE: article:118 Harv. L. Rev. 833\n\n\
    rename      renames the most recently modified file in the download\n\
                folder. getcite assumes that the the most recently modified\n\
                file in that folder is the most recently downloaded file, so\n\
                avoid modifying (e.g. renaming) files while getcite is\n\
                operating\n\n\
                USAGE:  rename:name of case or article:footnote_number\n\n\
                For example: rename:Shakur v. Smalls:003(4)\n\n\
                Assuming EDITOR abb. is AB and AUTHOR abb. is CD,, getcite\n\
                will save the most recently downloaded file in the download\n\
                folder as:\n\n\
                CD 003(4) Shakur v. Smalls AB.pdf\n\n\
    history     finds the westlaw history of the case or statute specified.\n\n\
                USAGE: history:citation\n\n\
                By simply typing \"history,\" with no argument, the user can \n\
                impute the previously entered citation as the argument. Useful\n\
                for when the history the user wants is from the previously \n\
                downloaded case.\n\n\
    license     displays a shortened version of the getcite license.\n\n\
    warranty    displays the getcite warranty.")
        else:
            get_westlaw_citation(citation, driver)
            
    driver.close()
    return

main()



