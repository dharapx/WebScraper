import json
import sys
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class BrowseWebsite:
    def __init__(self, config_file_path: str):
        """
        This is a constructor. To initiate the class config file path will be required
        :param config_file_path: Configuration File
        """
        # Reading config file if it exists
        try:
            with open(config_file_path) as cf:
                self.config = json.load(cf)
        except (FileNotFoundError, IOError) as e:
            sys.exit(f"Unable to open config file: {config_file_path}, Exception: {e}")
        self.chromedriver = self.config.get("chromedriver_path")

    def configure_chrome_browser(self) -> webdriver.Chrome:
        """
        This method is responsible for doing basic configuration of chrome
        :return: chrome driver object
        """
        # Configuring chrome driver
        chrome_options = Options()
        chrome_options.add_argument("headless")
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=Service(self.chromedriver), options=chrome_options)
        driver.maximize_window()
        return driver

    def get_career_link(self, base_url: str) -> str:
        """
        This method will get us the career page link of a domain if there is any
        :param base_url: domain url
        :return: String (Career page url)
        """
        browser = self.configure_chrome_browser()
        browser.get(url=base_url)
        try:
            career = browser.find_element(By.XPATH, "//a[text()='Careers']")
        except Exception as e:
            raise Exception(f"Unable to find the Careers link for URL: {base_url}. Exception: {e}")
        else:
            career_link = career.get_attribute("href")
            browser.close()
            return career_link

    def executor(self, base_url: str) -> list:
        """
        This method is responsible for controlling execution flow.
        This will trigger a scraping method based on domain.
        If there is a new domain found then it will return an empty list
        :param base_url: domain url
        :return: list of job links
        """
        job_urls_list = []
        try:
            career_url = self.get_career_link(base_url=base_url)
        except Exception as e:
            print(f"Unable to find Career page link: {e}")
        else:
            try:
                if 'www.druva.com' in base_url:
                    job_urls_list = self.find_all_job_in_druva(career_url=career_url)
                elif 'www.talentica.com' in base_url:
                    job_urls_list = BrowseWebsite.find_all_job_in_talentica(career_url=career_url)
                elif 'www.nuance.com' in base_url:
                    job_urls_list = self.find_all_job_in_nuance(career_url=career_url)
                else:
                    print(f"No method available to scrap the site: {base_url}")
            except Exception as e:
                print(f"Exception: {e}")
        return job_urls_list

    def find_all_job_in_druva(self, career_url):
        """
        This method will scrape the domain druva.com get all the job links
        :param career_url: Careers page url
        :return: list of job URL
        """
        job_url_list = []
        browser = self.configure_chrome_browser()
        browser.get(career_url)
        time.sleep(5)
        try:
            iframe = browser.find_element(By.XPATH, '//iframe[@id="grnhse_iframe"]')
        except NoSuchElementException:
            print(f"Unable to find the job page iframe link --hence Exit--")
            return job_url_list
        else:
            job_page_link = iframe.get_attribute('src')
            browser.get(job_page_link)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            browser.close()
            try:
                a_tags = soup.findAll('a', attrs={"data-mapped": "true"})
                for tag in a_tags:
                    job_url_list.append(tag.get('href'))
            except Exception as e:
                print(f"Unable to find job link in url: {job_page_link}. Exception: {e}")
        return job_url_list

    @staticmethod
    def find_all_job_in_talentica(career_url):
        """
        This method is responsible for getting all job url from talentica.com.
        I have made this static method because scraping has been done with requests module
        :param career_url: Careers page url
        :return: list of job URL
        """
        job_url_list = []
        response = requests.get(career_url)
        if not response.ok:
            print(f"Unable to open Careers link of Talentica: {career_url}")
            return job_url_list
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            job_link = soup.find('p', attrs={'class': 'pad-y-7 no-margin text-center more-link'}).find('a').get('href')
        except Exception as e:
            print(f"Unable to find the job page link in URL: {career_url}. Exception: {e}")
        else:
            job_res = requests.get(job_link)
            if not job_res.ok:
                print(f"Unable to open Job Opening link of Talentica: {job_link}")
            else:
                soup_job = BeautifulSoup(job_res.content, 'html.parser')
                try:
                    all_div = soup_job.findAll(
                        'div',
                        attrs={"class": "height-100 is-md-flex flex-column justify-content-between is-relative"}
                    )
                except Exception as e:
                    print(f"Unable to find Job link in url: {job_link}, Exception: {e}")
                else:
                    for div in all_div:
                        job_url_list.append(div.find('a').get('href'))
        return job_url_list

    def find_all_job_in_nuance(self, career_url):
        """
        This method is responsible for getting all job url from nuance.com
        :param career_url: Careers page url
        :return: list of job URL
        """
        job_url_list = []
        browser = self.configure_chrome_browser()
        browser.get(career_url)
        try:
            job_btn = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.XPATH, '//div[@class="button-w-label mt-20"]/a')))
        except Exception as e:
            print(f"Unable to find job listing button. Exception: {e}")
        else:
            browser.get(job_btn.get_attribute('href'))
            while True:
                time.sleep(3)
                try:
                    all_a_tag = browser.find_elements(By.XPATH, '//a[@data-automation-id="jobTitle"]')
                except Exception as e:
                    print(f"Unable to find job in job board. Exception: {e}")
                    break
                else:
                    for tag in all_a_tag:
                        job_url_list.append(tag.get_attribute('href'))
                try:
                    next_button = browser.find_element(By.XPATH, '//button[@aria-label="next"]')
                except NoSuchElementException:
                    current_page = browser.find_element(By.XPATH, '//button[@aria-current="page"]').text
                    print(f"We are at page no: {current_page}. There is no next page available")
                    break
                except Exception as e:
                    print(f"Unable to find next button. Exception: {e}")
                    break
                else:
                    next_button.click()
        browser.close()
        return job_url_list


if __name__ == '__main__':
    urls = [
        'https://www.druva.com',
        'https://www.talentica.com',
        'https://www.nuance.com'
    ]
    config_file = 'config.json'
    result_dict = {}
    # start_time = datetime.datetime.now()
    # iterating url list
    for url in urls:
        print(f"Let's get jobs link for domain: {url}")
        bw = BrowseWebsite(config_file_path=config_file)
        job_urls = bw.executor(base_url=url)
        if job_urls:
            print(f"Jobs link has been collected successfully")
        else:
            print(f"Didn't find any job URL")
        result_dict[url] = job_urls

    # Writing job urls in a jso file
    try:
        file_name = "..\\Output\\job_urls.json"
        json_object = json.dumps(result_dict, indent=4)
        # Writing to Output.json
        with open(file_name, "w") as outfile:
            outfile.write(json_object)
    except Exception as ex:
        print(f"Unable to write url in a JSON file. Exception: {ex}")
        print(f"{'*'*100}\nKindly Find the job links below.\n{'='*100}\n{result_dict}")
    # end_time = datetime.datetime.now()
    # time_diff = end_time - start_time
    # print(f"{'-' * 100}\nTotal Execution time: {time_diff.total_seconds()}")
