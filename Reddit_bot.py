from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from data_base import *

info3 = {
    'api': notion_api,
    'version': '2022-06-28',
    'base_id': notion_base_id
}


URL_BASE = 'https://old.reddit.com/user/'


class RedditParse:
    def __init__(self):
        self.base_url = 'https://old.reddit.com/user/'
        self.browser = webdriver.Firefox()

    def open_profile(self, user_name):
        self.browser.get(self.base_url + str(user_name))
        self.browser.implicitly_wait(3)

    def open_page(self, ref):
        self.browser.get(ref)
        self.browser.implicitly_wait(3)

    def click_yes_button(self):
        self.browser.find_element(By.XPATH, "//button[@value='yes']").click()

    @staticmethod
    def get_users_name():
        global INFO, INFO2
        data = get_users_data(NOTION_API_KEY=info3['api'], NOTION_API_VERSION=info3['version'],
                              DATABASE_ID=info3['base_id'])
        return data

    def parse_time(self):
        elements = self.browser.find_elements(By.XPATH, "//time")
        times_list = []
        for i in elements:
            post_time = datetime.strptime(i.get_attribute('datetime'), '%Y-%m-%dT%H:%M:%S%z')
            now = datetime.now(timezone.utc)
            difference_day = (now - post_time).total_seconds() / 60 / 60
            times_list.append(difference_day)
        return times_list

    def is_next_button(self):
        try:
            self.browser.find_element(By.XPATH, "//a[@rel='nofollow next']")
            return True

        except:
            return False

    def click_next(self):
        ref = self.browser.find_element(By.XPATH, "//a[@rel='nofollow next']").get_attribute('href')
        self.open_page(ref)

    def is_baned(self):
        self.browser.find_element(By.XPATH, "//div[@class='errorpage-message']")
        return True

    def start_parse(self):
        users_data = self.get_users_name()
        print(users_data)
        for i in range(len(users_data)):
            self.open_profile(users_data[i]['username'])
            try:
                self.click_yes_button()
            except:
                pass
            post_count = 0
            try:
                if self.is_baned():
                    users_data[i]['status'] = 'ban'
                else:
                    users_data[i]['status'] = 'not_ban'
            except:
                users_data[i]['status'] = 'not_ban'
            if users_data[i]['status'] == 'not_ban':
                while True:
                    time_list = self.parse_time()
                    time_list_day = list(filter(lambda item: item < 24, time_list))
                    post_count += len(time_list_day)
                    if len(time_list_day) < len(time_list) or not self.is_next_button():
                        break
                    self.click_next()
                try:
                    if post_count > users_data[i]['max post']:
                        users_data[i]['max post'] = post_count
                except:
                    users_data[i]['max post'] = post_count
                users_data[i]['post today'] = post_count
                users_data[i]['date'] = datetime.now().strftime("%Y-%m-%d")
                write_user_data_airtable(airtable_token, base_id=air_base, table_id=air_table, new_data=users_data[i])
            else:
                write_user_data_airtable(airtable_token, base_id=air_base, table_id=air_table, new_data=users_data[i])


if __name__ == '__main__':
    reddit = RedditParse()
    reddit.start_parse()
