# WebScraper
**Application Details:**

* The main application "web_scraper.py" is present under the "Apps" directory along with a config file.
* Class Diagram and Workflow Diagram have been placed under the "Document" folder.
* Assumption and Tech Stack details can be found in "Document/web_scraper_flowdiagram.pdf"
* All Job links will be written in a JSON file under the Output directory.

***To run this app in your system follow the steps below:***

    * Install python 3.9 or 3.9+
    * Create a  "Project" directory
    * Extract the content from the Alpha-Sense-Assignment.zip file in the Project directory 
    * Download a compatible chrome driver as per your google chrome version
    * Extract chromedriver.exe from the zip file to the Project/Apps directory.
    * Update the absolute path of the chromedriver.exe in the config.json file if you are placing the chromedriver.exe somewhere else.
    * Open your terminal/cmd
    * Go to Project/Apps directory
    * Run the command "python -m pip install -r requirements.txt"
    * Run the command python web_scraper.py
    * Once Execution is done. Check the Output directory for the job_urls.json file