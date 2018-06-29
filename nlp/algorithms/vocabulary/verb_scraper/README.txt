===============================================================================

        Instructions for scraping test data for the verb inflector

===============================================================================

1. Scrape the list of irregular verbs from Wikipedia and the 1000 most common
   English verbs from poetrysoup.com. Also correct for some inconsistencies
   between Wikipedia and Wiktionary:

       python3 ./scrape_verbs.py

   Generates two output files:

       verb_list.txt      - list of unique verbs found
       irregular_verbs.py - data structures imported by verb_inflector.py

2. Copy irregular_verbs.py to the directory that contains verb_inflector.py
   (up one level).

3. Scrape the inflection truth data from Wiktionary for all verbs in
   verb_list.txt:

       python3 ./scrape_inflection_data.py

   This code loads the verb list, constructs the Wiktionary URL for each verb
   in the list, scrapes the inflection data, and writes the output file
   'raw_inflection_data.txt'.

   Progress updates will be printed to the screen as the run progresses.

4. Process the inflection data to generate a 'truth' data file for testing
   the verb inflector:

       python3 ./process_scraped_inflection_data.py

   Generates the file 'inflection_truth_data.txt'.

5. Test the verb inflector:

       python3 ./verb_inflector.py --selftest

   No output means that all self-tests passed.

       python3 ./verb_inflector.py -f /path/to/inflection_truth_data.txt

   No output means that all inflection tests passed.
