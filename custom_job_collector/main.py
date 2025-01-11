"""
Main module to run the LinkedIn job scraper.
"""

import logging
from datetime import datetime

from custom_job_collector.lib.linkedin_job_scraper import LinkedInJobScraper
from custom_job_collector.lib.email_handler import EmailHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/linkedin_job_scraper.log", mode="a")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)


def main():
    """
    Main function to run the LinkedIn job scraper.
    """
    logger.info(
        f"--------------{datetime.now().strftime('%d %b %Y')}--------------"
    )
    logger.info("Starting LinkedIn job scraper")
    scraper = LinkedInJobScraper()
    email_agent = EmailHandler()
    try:
        scraper.login()
        scraper.navigate_to_jobs_page()
        collected_jobs = scraper.extract_job_postings(target_jobs=10)
        if len(collected_jobs):
            email_agent.send_email(
                subject="LinkedIn Job Listings for {}".format(
                    datetime.now().strftime("%Y-%m-%d")
                ),
                jobs=collected_jobs,
            )
    except Exception as e:
        logger.error("An error occurred: %s", e)
    finally:
        scraper.close()
        logger.info("LinkedIn job scraper finished")


if __name__ == "__main__":
    main()
