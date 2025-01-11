""" LinkedIn job scraper module """

import time
import json
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)

from custom_job_collector import const
from custom_job_collector.lib import models


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class LinkedInJobScraper:
    """
    A LinkedIn job scraper that extracts job postings.
    """

    COOKIES_FILE = "linkedin_cookies.json"

    def __init__(self):
        """
        Initializes the LinkedInJobScraper with Chrome options and
        sets up the WebDriver.
        """
        logging.info("Initializing LinkedInJobScraper")
        try:
            self.chrome_options = Options()
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=self.chrome_options)
        except WebDriverException as e:
            logging.error("Failed to initialize WebDriver: %s", e)
            raise

    def login(self):
        """
        Logs into LinkedIn using the provided user credentials.
        If cookies are available, it loads them to skip the login step.
        """
        logging.info("Attempting to restore session using cookies")
        self.driver.get("https://www.linkedin.com")
        self.load_cookies()
        self.driver.refresh()
        time.sleep(2)

        try:
            self.driver.find_element(
                By.CSS_SELECTOR, "img.global-nav__me-photo"
            )
            logging.info("Session restored using cookies")
            self.save_cookies()
            return
        except NoSuchElementException:
            logging.info("Cookies failed. Logging in manually.")

        self.driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        try:
            self.driver.find_element(By.ID, "username").send_keys(
                const.USER_EMAIL
            )
            self.driver.find_element(By.ID, "password").send_keys(
                const.USER_PASSWORD
            )
            self.driver.find_element(
                By.XPATH, '//button[@type="submit"]'
            ).click()
            time.sleep(5)

            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, "img.global-nav__me-photo"
                )
                logging.info("Manual login successful")
                self.save_cookies()
            except NoSuchElementException:
                logging.error("Login failed. Please check your credentials.")
                raise Exception("Login failed.")
        except NoSuchElementException as e:
            logging.error("Error during manual login: %s", e)
            raise

    def save_cookies(self):
        """
        Saves the current session cookies to a file.
        """
        logging.info("Saving cookies to file")
        cookies = self.driver.get_cookies()
        with open(self.COOKIES_FILE, "w") as file:
            json.dump(cookies, file)

    def load_cookies(self):
        """
        Loads cookies from a file and adds them to the browser.
        """
        try:
            with open(self.COOKIES_FILE, "r") as file:
                cookies = json.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            logging.info("Cookies loaded successfully")
        except FileNotFoundError:
            logging.warning("No cookies file found. Manual login required.")
        except Exception as e:
            logging.error("Failed to load cookies: %s", e)

    def navigate_to_jobs_page(self):
        """
        Navigates to the LinkedIn jobs page.
        """
        logging.info("Navigating to LinkedIn jobs page")
        try:
            self.driver.get(
                "https://www.linkedin.com/jobs/collections/recommended/"
            )
            time.sleep(5)
            logging.info("Navigated to jobs page")
        except TimeoutException as e:
            logging.error("Timeout while navigating to jobs page: %s", e)
            raise

    def extract_job_postings(self, target_jobs=50) -> list[models.Job]:
        """
        Extracts job postings from the LinkedIn jobs page.

        :param target_jobs: The target number of jobs to collect.
        """
        logging.info("Extracting job postings")
        jobs_collected = 0
        seen_jobs = set()
        new_jobs = []

        while jobs_collected < target_jobs:
            try:
                jobs_container = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "#main > div > div.scaffold-layout__list-detail-inner."
                    "scaffold-layout__list-detail-inner--grow > div.scaffold-"
                    "layout__list > div",
                )
                jobs = self.driver.find_elements(
                    By.CLASS_NAME, "job-card-container"
                )

                if not jobs:
                    logging.warning("No job postings found.")
                    break

                for job in jobs:
                    try:
                        title_element = job.find_element(
                            By.CLASS_NAME, "job-card-list__title--link"
                        )
                        title = title_element.get_attribute("aria-label")
                        company = job.find_element(
                            By.CLASS_NAME, "artdeco-entity-lockup__subtitle"
                        ).text
                        location = job.find_element(
                            By.CLASS_NAME, "artdeco-entity-lockup__caption"
                        ).text
                        link = title_element.get_attribute("href")
                        job_key = f"{title}-{company}-{location}"

                        if job_key not in seen_jobs:
                            seen_jobs.add(job_key)
                            jobs_collected += 1
                            new_job = models.Job(
                                title=title,
                                company=company,
                                location=location,
                                link=link,
                                posted_date=None,
                            )
                            logging.info(
                                "Job %d: Title: %s, Company: %s, Location: %s",
                                jobs_collected,
                                title,
                                company,
                                location,
                            )
                            new_jobs.append(new_job)

                            if jobs_collected >= target_jobs:
                                break
                    except NoSuchElementException as e:
                        logging.warning(
                            "Incomplete job information found: %s", e
                        )

                last_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight;", jobs_container
                )
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight;",
                    jobs_container,
                )
                time.sleep(2)
                new_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight;", jobs_container
                )

                if new_height == last_height:
                    logging.info("Reached the end of the job listings")
                    break
            except Exception as e:
                logging.error(
                    "An error occurred while extracting job postings: %s", e
                )
                break

        logging.info("Extracted a total of %s jobs.", jobs_collected)
        return new_jobs

    def close(self):
        """
        Closes the WebDriver.
        """
        logging.info("Closing WebDriver")
        self.driver.quit()
