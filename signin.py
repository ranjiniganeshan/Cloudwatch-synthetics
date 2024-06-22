import asyncio
import os
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.common import synthetics_logger as logger, synthetics_configuration
import boto3
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://www.facebook.com/"
username = "ranjiniganeshan@gmail.com"
password = "*********"

cloudwatch = boto3.Session(region_name="us-east-1").client('cloudwatch')

async def main():
    browser = syn_webdriver.Chrome()

    # Set synthetics configuration
    synthetics_configuration.set_config({
       "screenshot_on_step_start" : True,
       "screenshot_on_step_success": True,
       "screenshot_on_step_failure": True
    })

    # Navigate to the page
    def navigate_to_page():
        browser.delete_all_cookies()
        browser.implicitly_wait(30)
        browser.get(url)
    await syn_webdriver.execute_step("navigateToUrl", navigate_to_page)

    # Execute customer steps
    def customer_actions_1():
        browser.execute_script('document.getElementById("email").value = arguments[0];', username)
    await syn_webdriver.execute_step('input', customer_actions_1)

    def customer_actions_2():
        browser.execute_script('document.getElementById("pass").value = arguments[0];', password)
        browser.execute_script('document.getElementsByName("login")[0].click();')
    await syn_webdriver.execute_step('input', customer_actions_2)

    # Verify login success
    def verify_login():
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Home")]'))
            )
            logger.info("Login successful for partition " + url)
            successful_run = 1
        except:
            logger.error("Login failed for partition " + url)
            successful_run = 0
        
        cloudwatch.put_metric_data(
            MetricData=[
                {
                    'MetricName': 'UITESTS',
                    'Dimensions': [
                        {'Name': 'Url', 'Value': url},
                    ],
                    'Unit': 'Count',
                    'Value': successful_run
                },
            ],
            Namespace="example"
        )
        return successful_run

    await syn_webdriver.execute_step('verifyLogin', verify_login)

async def handler(event, context):
    # User-defined log statements using synthetics_logger
    logger.info("Selenium Python workflow canary")
    return await main()
