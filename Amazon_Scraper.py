import requests
from glob import glob
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from price_notify import notify, shorter

def search_product_list(interval_count = 1, interval_hours = 6):

    prod_tracker = pd.read_csv('trackers/PRODUCTS.csv', sep=',')
    prod_tracker_URLS = prod_tracker.url
 
    tracker_log = pd.DataFrame()
    now = datetime.now().strftime('%Y-%m-%d %Hh%Mm')
    interval = 0 # counter reset
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.minimize_window()
    print('Initializing browser !')
    while interval < interval_count:
        for x, url in enumerate(prod_tracker_URLS):

            driver.get(url)
            
            # print("Waiting for loading data!🖤")
            content = driver.page_source
            soup = BeautifulSoup(content, features="lxml")
            
            #product title
            title = soup.find('span', attrs={'id': 'productTitle'}).text.strip()
            image = soup.find('img', attrs={'id': 'landingImage'})#.get("src")
            if image is None:
                image = soup.find('img', attrs={'id': 'a-dynamic-image image-stretch-vertical frontImage'})
            
            # to prevent script from crashing when there isn't a price for the product
            try:
                price = float(soup.find('span',attrs={'class':'a-price-whole'}).text.replace('.', '').replace('€', '').replace(',', '').strip())
            except:
                # this part gets the price in dollars from amazon.com store
                try:
                    price = float(soup.find('span', attrs={'class':'a-offscreen'}).text.replace('$', '').replace(',', '').strip())
                except:
                    price = ''

            try:
                review_score = soup.find('span', attrs={'class': 'a-icon-alt'}).text.split()[0]
                review_count = soup.find('span', attrs={'id': 'acrCustomerReviewText'}).text.split()[0].replace(',', '').strip()
                
            except:
                # sometimes review_score is in a different position... had to add this alternative with another try statement
                try:
                    review_score = soup.find('span', attrs={'class': 'a-size-medium a-color-base a-text-beside-button a-text-bold'}).text.split()[0]
                    review_count = soup.find('span', attrs={'id': 'acrCustomerReviewLink'}).text.split()[0].replace(',', '').strip()
                except:
                    review_score = ''
                    review_count = ''

            # checking if there is "Out of stock"
            try:
                soup.select('#availability .a-color-state')[0].get_text().strip()
                stock = 'Out of Stock'
            except:
                # checking if there is "Out of stock" on a second possible position
                try:
                    soup.select('#availability .a-color-price')[0].get_text().strip()
                    stock = 'Out of Stock'
                except:
                    # if there is any error in the previous try statements, it means the product is available
                    stock = 'Available'

            log = pd.DataFrame({'date': now.replace('h',':').replace('m',''),
                                'code': prod_tracker.code[x], # this code comes from the TRACKER_PRODUCTS file
                                'url': url,
                                'title': title,
                                'buy_below': prod_tracker.buy_below[x], # this price comes from the TRACKER_PRODUCTS file
                                'price': price,
                                'stock': stock,
                                'review_score': review_score,
                                'review_count': review_count}, index=[x])

            try:
                # This is where you can integrate an email alert!
                if price < prod_tracker.buy_below[x] and price != '':
                    Subject = "Buy at " + "₹" + str(round(price)) +" "+ title
                    body = [url, title, image.get("src"), str(round(price))]
                    notify(Subject,body) #Email sender
            
            except Exception as e:
                # sometimes we don't get any price, so there will be an error in the if condition above
                print(e)

            tracker_log = pd.concat([tracker_log, log])
            print('appended -> '+ prod_tracker.code[x])#+'\n' + title + '\n\n')            

        interval += 1# counter update
        
        # sleep(interval_hours*1*1)
        print('end of interval '+ str(interval))
    try:
        # after the run, checks last search history record, and appends this run results to it, saving a new file
        last_search = glob('./search_history/*.xlsx')[-1] # path to file in the folder
        search_hist = pd.read_excel(last_search)
        # pd.DataFrame(np.insert(search_hist.values, values=[" "] * len(search_hist.columns), axis=0),columns = search_hist.columns)
        final_df = pd.concat([search_hist,tracker_log], sort=False)
        final_df.to_excel('search_history/SEARCH_HISTORY_{}.xlsx'.format(now), index=False)
    except Exception as e:
        print('Unable to store result => ',e)
    print('end of search !!!')

search_product_list()
