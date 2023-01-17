import asyncio
import os
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.common import synthetics_logger as logger, synthetics_configuration
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import boto3

from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By


TIMEOUT = 45

cloudwatch = boto3.Session(region_name= "us-east-1").client('cloudwatch')

async def main():
    partition_url = os.environ['partition_url']
    tenant_id = os.environ['tenant_id']
    tenant_password = os.environ['tenant_password']
    browser = syn_webdriver.Chrome()


    # Set synthetics configuration
    synthetics_configuration.set_config({
       "screenshot_on_step_start" : True,
       "screenshot_on_step_success": True,
       "screenshot_on_step_failure": True
    });


    def navigate_to_page():
        browser.delete_all_cookies()
        browser.implicitly_wait(30)
        browser.get(partition_url)
    await syn_webdriver.execute_step("navigateToUrl", navigate_to_page)

    # Execute customer steps
    def customer_actions_1():
        browser.find_element_by_id('email').send_keys(tenant_id);
    await syn_webdriver.execute_step('input', customer_actions_1)

    def customer_actions_2():
        browser.find_element_by_id('pass').send_keys(tenant_password);
        browser.find_element_by_name('login').click()
        successful_run = 1
    await syn_webdriver.execute_step('input', customer_actions_2)

    def customer_actions_5():
        if successful_run == 1:
            logger.info("login successful for partition" +partition_url+ "whose tenant name is" +tenant_id)
        else:
            logger.info("login failure for partition" +partition_url+ "whose tenant name " +tenant_id)
            response = cloudwatch.put_metric_data(MetricData = [
                {
                    'MetricName': 'UITESTS',
                    'Dimensions': [
                        {
                            'Name': 'Partition_Url',
                            'Value': partition_url
                        },
                    ],
                    'Unit': 'Count',
                    'Value': successful_run
                },
            ],
            Namespace =  "example"
        )

async def handler(event, context):
    # user defined log statements using synthetics_logger
    logger.info("Selenium Python workflow canary")
    return await main()