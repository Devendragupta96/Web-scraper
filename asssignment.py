import json
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import threading

def fetch_restaurant_details(chunk, result_list):
    # Initialize an empty list to store restaurant details
    restaurant_details = []

    for container in chunk:
        restaurant_info = {}
        
        # Restaurant Name
        name_element = container.find('p', class_='name___2epcT')
        restaurant_info['name'] = name_element.text.strip() if name_element else None
        
        # Restaurant Cuisine
        cuisine_element = container.find('div', class_='basicInfoRow___UZM8d cuisine___T2tCh')
        restaurant_info['cuisine'] = cuisine_element.text.strip() if cuisine_element else None
        
        # Restaurant Rating
        rating_element = container.find('div', class_='medium___3F_Er ratingStar infoItemIcon___23Zvv')
        restaurant_info['rating'] = float(rating_element.next_sibling.strip()) if rating_element and rating_element.next_sibling else None
        
        # Delivery time and distance
        numbers_child_elements = container.find_all('div', class_='numbersChild___2qKMV')
        if len(numbers_child_elements) >= 2:
            delivery_info_text = numbers_child_elements[1].text.strip()
            delivery_info_parts = delivery_info_text.split('•')
            if len(delivery_info_parts) >= 2:
                restaurant_info['delivery_time'] = delivery_info_parts[0].strip()
                restaurant_info['distance'] = delivery_info_parts[1].strip()
            else:
                restaurant_info['delivery_time'] = None
                restaurant_info['distance'] = None
        else:
            restaurant_info['delivery_time'] = None
            restaurant_info['distance'] = None
        
        # Promotional Offers Listed for the Restaurant
        promo_element = container.find('span', class_='discountText___GQCkj')
        restaurant_info['promo'] = promo_element.text.strip() if promo_element else None
        
        # Image Link of the Restaurant
        image_link_element = container.find('img', class_='realImage___2TyNE')
        restaurant_info['image_link'] = image_link_element['src'] if image_link_element and 'src' in image_link_element.attrs else None
        
        # Is promo available (True/False)
        restaurant_info['is_promo_available'] = True if promo_element else False
        
        # Restaurant ID
        restaurant_id = container.find('a')['href'].split('/')[-1].split('?')[0] if container.find('a') else None
        restaurant_info['restaurant_id'] = restaurant_id

        # Closing soon
        closing_soon_element = container.find('div', class_='closeSoon___1eGf8')
        restaurant_info['closing_soon'] = closing_soon_element.text.strip() if closing_soon_element else None
        
        # Append the restaurant info to the list of restaurant details
        restaurant_details.append(restaurant_info)

    # Append the result of this chunk to the result list
    result_list.append(restaurant_details)


def divide_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Configure Selenium webdriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
chrome_options.add_argument("accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8")
chrome_options.add_argument("accept-language=en-US,en;q=0.5")
chrome_options.add_argument("cache-control=max-age=0")
chrome_options.add_argument("priority=u=0, i")
chrome_options.add_argument("sec-ch-ua=\"Chromium\";v=\"124\", \"Brave\";v=\"124\", \"Not-A.Brand\";v=\"99\"")
chrome_options.add_argument("sec-ch-ua-mobile=?0")
chrome_options.add_argument("sec-ch-ua-platform=\"Windows\"")
chrome_options.add_argument("sec-fetch-dest=document")
chrome_options.add_argument("sec-fetch-mode=navigate")
chrome_options.add_argument("sec-fetch-site=same-origin")
chrome_options.add_argument("sec-fetch-user=?1")
chrome_options.add_argument("sec-gpc=1")
chrome_options.add_argument("upgrade-insecure-requests=1")
chrome_options.add_argument("cookie=_gsvid=1531315f-31bc-4954-a530-5757b707e3f2; hwuuid=dfc6b434-02e4-4115-919a-8c302e7c7265; hwuuidtime=1715331086; gfc_country=SG; gfc_session_guid=5cf98623-e09f-4f05-97de-82d3a1931c3f; next-i18next=en; _gssid=2404120928-ikrf56snhfa; location=%7B%22id%22%3A%22IT.2EPYOYVWDKGU3%22%2C%22latitude%22%3A1.396364%2C%22longitude%22%3A103.747462%2C%22address%22%3A%22Choa%20Chu%20Kang%20North%206%2C%20Singapore%2C%20689577%22%2C%22countryCode%22%3A%22SG%22%2C%22isAccurate%22%3Atrue%2C%22addressDetail%22%3A%22PT%20Singapore%20-%20Choa%20Chu%20Kang%20North%206%2C%20Singapore%2C%20689577%22%2C%22noteToDriver%22%3A%22%22%2C%22city%22%3A%22Singapore%20City%22%2C%22cityID%22%3A6%2C%22displayAddress%22%3A%22PT%20Singapore%20-%20Choa%20Chu%20Kang%20North%206%2C%20Singapore%2C%20689577%22%7D")
chrome_options.add_argument("referer=https://food.grab.com/sg/en/")
chrome_options.add_argument("referrer-policy=strict-origin-when-cross-origin")
driver = webdriver.Chrome(options=chrome_options)

# Data for PT Singapore - Choa Chu Kang North 6, Singapore, 689577
# Send a request to the webpage
url = "https://food.grab.com/sg/en/restaurants"
driver.get(url)

# Simulate scrolling to the bottom of the page to load all content
SCROLL_PAUSE_TIME = 2  # Adjust as needed
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
# Get the updated page source after scrolling
page_source = driver.page_source

# Close the browser
driver.quit()

# Fetch request based on Address PT Singapore - Choa Chu Kang North 6, Singapore, 689577
soup = BeautifulSoup(page_source, "html.parser")

title = soup.find('title').text.strip()

if title != 'ERROR: The request could not be satisfied':
    # Find all restaurant containers
    restaurant_containers = soup.find_all('div', class_="ant-col-24 RestaurantListCol___1FZ8V ant-col-md-12 ant-col-lg-6")

    chunks = list(divide_chunks(restaurant_containers, len(restaurant_containers) // 5))  # Dividing into 5 chunks

    # Create threads
    threads = []
    result_list = []
    for chunk in chunks:
        thread = threading.Thread(target=fetch_restaurant_details, args=(chunk, result_list))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Combine the results from all threads
    all_restaurant_details = []
    for result in result_list:
        all_restaurant_details.extend(result)

    # Print the restaurant details
    restaurant_details_json = json.dumps(all_restaurant_details, indent=4)
    # print(restaurant_details_json, len(all_restaurant_details)) # comment this if you don't want to see the output

    # Write JSON data to the file
    with open('restaurants_details.json', 'w') as json_file:
        json.dump(all_restaurant_details, json_file, indent=4)
else:
    print("Failed to retrieve the webpage")
