CONTENTS OF THIS FILE
---------------------
   
 * Introduction
 * Requirements
 * Installation
 * Functionality
 * Instructions for Use
 * License
 * Contact

INTRODUCTION
------------

 getcite was created to save Florida Law Review member's time by automating
 the process called "pulling sources." 

REQUIREMENTS
------------

 getcite currently has the following software dependencies:

 	Python 3.5.0 or higher;
 	Selenium WebDriver 2.48.0 or higher;
	Firefox 43 or higher;
	PyPDF2 1.25.0 or higher;

 getcite has the following network dependencies:

	For sources from HeinOnline: must be on local UF network or logged in 
	to UF network through VPN;

INSTALLATION
------------

 For Mac:

 (1) Download and install Python 3.5 or above, by going to this website:
		
	https://www.python.org/downloads/

 (2) Once Python is installed, download getcite by opening terminal and 
	 typing: 
		
	python3 -m pip install getcite --download ~/Downloads

 OR

	git clone https://github.com/salexander2000/getcite

(3) Once getcite is downloaded and unzipped, go to the getcite root 
	folder (that contains setup.py) and type:

	python3 setup.py install

(4) To run, go to the ./getcite folder and type:

	python3 getcite.py


FUNCTIONALITY
-------------

 getcite can perform the following actions:

 Downloading:
	Any original PDFs, including S. Ct. opinions, on Westlaw, default 
		presumption;
	Any unpublished/recent cases available on Westlaw, via the Westlaw 
		generate/download PDF function;
	Supreme Court cases on HeinOnline, automatically detected;
	U.S.C. statutes on HeinOnline, automatically detected;
	Law review articles on HeinOnline, must be specified;

 Naming:
	Names automatically downloaded sources in the FLR source-naming 
		format; 
	Can rename most recently downloaded file, if download 
		completed manually, in FLR source-naming format;

 Shepardizing:
	Cases and statutes on westlaw;
	Uses auto-naming features;
	Automatically concatenates PDFs when multiple histories are downloaded
		e.g. cases with both negative treatment and case history;

NOTE: As of right now, getcite cannot locate the table of contents
associated with a law review article. The process is too complex and
idiosyncratic. 

Law review articles often contain enough information on the first page 
of the article to determine the accuracy of the citation. However, they 
often do not. In order to make the best of getcite's automation process 
while not dropping required elements of the source-pulling process in 
general, the following steps are recommended:

1) Download the law review article automatically.
2) After the source is automatically downloaded and named, look at
	the first page, which should be open in Firefox, to see if more
	information is necessary to verify the accuracy of the citation.
3) If the article page contains enough information, move on. 
	Otherwise, you can now quickly find the associated table of 
	contents and download it manually.
4) Once you've downloaded the table of contents, you'll need to 
	manually merge it into the properly named file using a PDF 
	editor.


INSTRUCTIONS FOR USE
--------------------

 getcite will automatically attempt to detect the citation type and location. 
 However, the user must first specify that they* intend to enter an article
 citation by using the "article" command.

 NOTE: There is really no difference between citations and commands. When a 
 string is entered, getcite will first run it through the list of available
 commands. If getcite does not detect a known command, the program treat the
 entry as a citation and attempt to automatically locate and download it.

 Abbreviation prompts:

 First, getcite will ask for the EDITOR abbreviation. Next, getcite will
 ask for the AUTHOR abbreviation. 

 This information helps getcite automatically name downloaded sources 
 only needs to be entered once every time getcite runs.

 Citation prompt and source naming: 

 The user can now start entering citations and commands. 

 Source naming:

 (1) If getcite successfully downloads a source, the program will prompt the 
 user to either type a save-name different from the citation entered or 
 simply press 'enter' to use the citation entered for the save-name. This
 functionality was added because reviewers often prefer to use a case or
 article name rather than a case or article citation when naming source 
 files.

 The user may also type 'stop' here, which will return the program to the
 citation prompt without renaming a file. This is useful when getcite grabs
 the wrong file.

 (2) Next, getcite will ask the user for the footnote number, e.g.: 037(4) 

 NOTE: Because the naming function runs immediately after the footnote is 
 entered, you need to WAIT UNTIL THE DOWNLOAD IS COMPLETE before hitting
 'return' after entering the footnote number. 

 (3) Finally, getcite will print the most recently downloaded file's name, to
 ensure accuracy, and then will rename that file to an FLR format: 

 	author_abbreviation footnote_number name/citation editor_abbreviation.pdf

 Commands:

 quit:		Closes the browser and quits getcite

 article: 	Tells getcite that the next command entered will be a law 
			review article citation

 rename:	Renames the most recently modified file in the download 
			folder. getcite assumes that the the most recently modified 
			file in that folder is the most recently downloaded file, so 
			avoid modifying (e.g. renaming) files while getcite is 
			operating

	USAGE: 		rename:name of case or article:footnote_number
	For example: 	rename:Shakur v. Smalls:003(4) 

	Assuming EDITOR abb. is AB and AUTHOR abb. is CD,, getcite 
	will save the most recently downloaded file in the download 
	folder as: 

		CD 003(4) Shakur v. Smalls AB.pdf
			
 This command is helpful when: 

 (a) the user has reached a point where getcite cannot download 
 the source, but the user can finish the download manually.
 After the manual download is completed, getcite's "rename"
 function is still faster than using the operating system. 

 (b) the user has not used getcite for the most recent download, 
 but has manually downloaded a source into the download folder 
 and wishes to use the rename function rather than renaming
 through the operating system;

 (c) the user has made a mistake in the naming of the most
 recently automatically-downloaded file, and wishes to name it
 again. For example, user enters 012 for footnote, but wants to
 change it to 012(1) without using the operating system;

 history:    Finds the westlaw history of the case or statute specified.
            	
	USAGE:      history:citation

    By simply typing "history," with no argument, the user can
    impute the previously entered citation as the argument. Useful
    for when the history the user wants is from the previously
    downloaded case.
	
license     Displays a shortened version of the getcite license.
    
warranty    Displays the getcite warranty.


LICENSE
-------
   
 Copyright (C) 2015

 This program is free software: you can redistribute it and/or modify it under 
 the terms of the GNU General Public License as published by the Free Software 
 Foundation, either version 3 of the License, or (at your option) any later 
 version.

 This program is distributed in the hope that it will be useful, but WITHOUT 
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
 FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for 
 more details.

 You should have received a copy of the GNU General Public License along with 
 this program.  If not, see <http://www.gnu.org/licenses/>.

CONTACT
-------

 You can contact the author at: salexander2000@gmail.com
 
