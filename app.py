try:
    from selenium import webdriver
    import csv
    import json
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException
    import argparse
    from fake_headers import Headers
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
except Exception as ex:
    print(ex)



class Twitter:

    @staticmethod
    def init_driver(browser_name:str):
        def set_properties(browser_option):
            ua = Headers().generate()      #fake user agent
            # browser_option.add_argument('--headless')
            browser_option.add_argument('--disable-extensions')
            browser_option.add_argument('--incognito')
            browser_option.add_argument('--disable-gpu')
            browser_option.add_argument('--log-level=3')
            browser_option.add_argument(f'user-agent={ua}')
            browser_option.add_argument('--disable-notifications')
            browser_option.add_argument('--disable-popup-blocking')
            return browser_option
        try:
            browser_name = browser_name.strip().title()


            #automating and opening URL in headless browser
            if browser_name.lower() == "chrome":
                browser_option = ChromeOptions()
                browser_option = set_properties(browser_option)

                driver = webdriver.Chrome(ChromeDriverManager().install(),options=browser_option) #chromedriver's path in first argument
            elif browser_name.lower() == "firefox":
                browser_option = FirefoxOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),options=browser_option)
            else:
                driver = "Browser Not Supported!"
            return driver
        except Exception as ex:
            print(ex)

    @staticmethod
    def scrap(username,browser_name):
        try:
            #generating URL according to the username
            URL = "https://twitter.com/{}".format(username)

            driver = Twitter.init_driver(browser_name)  #initialize driver
            try:
                driver.get(URL)  #try to navigate to URL
            except AttributeError:
                #if there is attribute error it means driver is not set
                print("Driver is not set")
                exit()
            wait = WebDriverWait(driver, 30) #wait for 30
            element = wait.until(EC.title_contains("@")) #until the tab loads and contains '@' symbol
            #take title tag text from tab and split it with "(" and take 0th element from the splitted list
            full_name = driver.title.split("(")[0]


            try:
                #try to find banner image
                banner_image = driver.find_element(By.CSS_SELECTOR, "img.css-9pa8cd").get_attribute("src")
                print(banner_image)

            except NoSuchElementException:
                banner_image = ""


            try:
                #if svg with aria-label as "verified account" is present then account is verified
                driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Verified account']")
                is_verified = True
            except NoSuchElementException:
                #if svg is not found that means account is not verified
                is_verified = False
            #twitter's profile route is twitter.com/user_name_of_profile/photo
            profile_image = "https://twitter.com/{}/photo".format(username.lower())

            follow_div = driver.find_element(By.CSS_SELECTOR, "div.css-1dbjc4n.r-1mf7evn").text #how many following for given profile

            followers = driver.find_element(By.XPATH, "//a[contains(@href,'followers')]").get_attribute("text")

            try:
                #user's bio
                bio = driver.find_element(By.CSS_SELECTOR, "div[data-testid='UserDescription']").text
            except NoSuchElementException:
                bio = ""


            try:
                details = driver.find_element(By.CSS_SELECTOR, "[data-testid='UserProfileHeader_Items']")
                all_spans = details.find_element(By.TAG_NAME, "span")
                joined_date = ""


                birth_date = ""
                for item in all_spans:
                    if "born" in item.text.lower():
                        birth_date = item.text
                    elif "join" in item.text.lower():
                        joined_date = item.text

            except Exception as ex:
                print(ex)
            try:
                website = details.find_element(By.TAG_NAME, "a").text
            except NoSuchElementException:
                website = ""
            location = details.text.replace(joined_date,"").replace(website,"")

            profile_data = {
                'full_name' : full_name,
                'banner' : banner_image,
                'profile_image_link' : profile_image,
                 "account_verified" : is_verified,
                 "birth_date" : birth_date,
                 "location" : location,
                 "website" : website,
                 "bio" : bio,
                 "followers" : followers.split(" ")[0],
                 "following" : follow_div.split(" ")[0],
                 "joined_date" : joined_date

            }
            f = open('info.csv', 'w')
            headerrow= ['FullName','BannerImage','ProfileImage','AccountVerified','BirthDate','Location','Website','Bio','Followers','Following','JoinedDate']
            writer = csv.writer(f)
            writer.writerow(headerrow)
            writer.writerow([full_name,banner_image,profile_image,is_verified,birth_date,location,website,bio,followers.split(" ")[0],follow_div.split(" ")[0],joined_date])
            driver.close()
            driver.quit()
            return json.dumps(profile_data)
        except Exception as ex:
            driver.close()
            driver.quit()
            print(ex)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to search")
    parser.add_argument("--browser",help="What browser your PC have?")

    args = parser.parse_args()
    browser_name = args.browser if args.browser is not None else "chrome"
    print(Twitter.scrap(args.username,browser_name))

#last updated - 27th December,2021