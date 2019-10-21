import pytest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def open_url(driver, url):
    driver.get(url)


def enter_input(element, txt):
    element.send_keys(txt)
    element.send_keys(Keys.TAB)


def press_button(element):
    if element:
        element.click()


def login():
    driver = webdriver.Chrome()
    open_url(driver, "https://localhost/dashboard")

    time.sleep(15)

    enter_input(driver.find_element_by_id("Username"), "admin")
    enter_input(driver.find_element_by_id("Password"), "admin")
    press_button(driver.find_element_by_xpath('//button[text()="Log In"]'))

    time.sleep(15)

    driver.close()


if __name__ == "__main__":
    login()
