""" Email Handler Module """

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formatdate
import logging
import os

from custom_job_collector import const
from custom_job_collector.lib import models


class EmailHandler:
    """Email handler class to send emails with attachments."""

    def __init__(self):
        """Initialize the email handler."""
        self.smtp_server = const.SMTP_SERVER
        self.smtp_port = const.SMTP_PORT
        self.smtp_user = const.SMTP_USER
        self.smtp_password = const.SMTP_PASSWORD
        self.from_email = const.FROM_EMAIL
        self.to_email = const.TO_EMAIL

    def send_email(
        self, subject, jobs: list[models.Job], attachment_path=None
    ):
        """
        Send an email with collected jobs.

        Args:
            subject (str): The email subject.
            jobs (list[models.Job]): A list of collected jobs.
            attachment_path (str): The path to the attachment file.
        """
        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = self.to_email
        msg["Date"] = formatdate(localtime=True)
        msg["Subject"] = subject

        # Create HTML body for jobs
        body = self.generate_html_body(jobs)
        msg.attach(MIMEText(body, "html"))

        if attachment_path:
            with open(attachment_path, "rb") as f:
                attachment = MIMEApplication(f.read())
                attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(attachment_path),
                )
                msg.attach(attachment)

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_email, self.to_email, msg.as_string())
            server.quit()
            logging.info("Email sent successfully")
        except Exception as e:
            logging.error("An error occurred while sending the email: %s", e)
            raise e

    def generate_html_body(self, jobs: list[models.Job]) -> str:
        """
        Generate an HTML table for the list of jobs.

        Args:
            jobs (List[Job]): A list of collected jobs.

        Returns:
            str: An HTML-formatted string.
        """
        table_rows = ""
        for job in jobs:
            posted_date = (
                job.posted_date.strftime("%Y-%m-%d")
                if job.posted_date
                else "N/A"
            )
            table_rows += f"""
            <tr>
                <td>{job.title}</td>
                <td>{job.company}</td>
                <td>{job.location}</td>
                <td><a href="{job.link}" target="_blank">View Job</a></td>
                <td>{posted_date}</td>
            </tr>
            """

        html_body = f"""
        <html>
        <head>
            <style>
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-family: Arial, sans-serif;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                }}
                th {{
                    background-color: #f2f2f2;
                    text-align: left;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                tr:hover {{
                    background-color: #ddd;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <h2>Collected Job Listings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Company</th>
                        <th>Location</th>
                        <th>Link</th>
                        <th>Posted Date</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </body>
        </html>
        """
        return html_body
