try:
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException
    from fake_headers import Headers
    import csv
    import json
    import time

    print("Imported")
except ModuleNotFoundError:
    print("ModuleNotFoundError")
except Exception:
    print(Exception)


def get_driver():
    try:
        ua = Headers().generate() #fake user agent
        print("Generated")
        options = webdriver.ChromeOptions()
        # options.add_argument("--start-maximized")
        # options.add_argument('--headless')
        options.add_argument('--disable-extensions')
        options.add_argument('--incognito')
        options.add_argument('--disable-gpu')
        options.add_argument('--log-level=3')
        options.add_argument(f'user-agent={ua}')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')

        global driver
        driver = webdriver.Chrome(chrome_options=options)
        # driver.get("https://twitter.com/Alrammah_T")
        driver.get("https://twitter.com/vet_abdullah_n")
        # driver.get("https://twitter.com/katohla")
        print("Opened Profile")
    except:
        print("Something went wrong about making browser driver")

def scrap():
    try:
        wait = WebDriverWait(driver, 30) #wait for 30
        element = wait.until(EC.title_contains("@")) #until the tab loads and contains '@' symbol
        #take title tag text from tab and split it with "(" and take 0th element from the splitted list
        full_name = driver.title.split("(")[0]
        username = driver.title.split("(")[1].split()[0][1:-1]
        print(username)

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
            'full_name' : str(full_name),
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
        # driver.close()
        # driver.quit()
        return json.dumps(profile_data)
    except Exception as ex:
        driver.close()
        driver.quit()
        print(ex)

Tweets = []

def tweets():
    print("Hello")
    tweet_count = 0
    # while length of captured tweets equal 50 keep on scrollling
    while True:
        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        print(len(tweets))
        if len(tweets) < tweet_count:
            print("Less Tweets...\nTrying again")
            time.sleep(2)
            continue

        uniqueTweets = list(set(tweets))
        print(len(uniqueTweets))
        # once required 50 tweets are caught, then scrape each tweet into csv
        f = open('tweets.csv', 'w')
        headerrow= ['Tweet','Retweet','Reply','Like']
        writer = csv.writer(f)
        writer.writerow(headerrow)
        
        for article in tweets: 
            # Tweets.append(t)
            print("A tweet starts here")
            tweet = driver.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
            retweet = driver.find_element(By.XPATH, './/div[@data-testid="retweet"]').text
            reply = driver.find_element(By.XPATH, './/div[@data-testid="reply"]').text
            like = driver.find_element(By.XPATH, './/div[@data-testid="like"]').text
            print(tweet, retweet, reply, like)
            print("A tweet ends\n")
            writer.writerow([tweet, retweet, reply, like])

        tweet_count = len(tweets)
        driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(2)
        print("waiting...")

        if len(uniqueTweets) >= 7:
            break



def main():
    get_driver()
    scrap()
    tweets()


main()