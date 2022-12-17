import requests
import json
import pickle
import time
import numpy as np
import pandas as pd

#for login cookie chrome > settings > privacy and security > cookies and other site data > see all cookies and site data > search steamcommunity.com > find “steamLoginSecure” > and copy the “Content” string.
login_cookie = input('Enter Steam login credential cookie: /n'
cookie = {'steamLoginSecure': login_cookie}
game_code = input ('Enter Steam Game Code: \n')


def total_item_number(game_code):
    response = requests.get('https://steamcommunity.com/market/search/render/?appid=' + str(game_code) + '&norender=1&count=5000', cookies=cookie)
    print(response)
    # print(response.content)
    response_json = json.loads(response.content)
    # print (response_json)
    return (response_json['total_count'])
total_item_no = total_item_number(game_code)
print (f'Total number of skins = {total_item_no}')


item_names_list = []
for current_position in range(0, total_item_no,100):
    response = requests.get('https://steamcommunity.com/market/search/render/?start=' + str(current_position) + '&count=100&appid=' + str(game_code) + '&norender=1&count=5000', cookies=cookie)
    time.sleep(4)
    print (f'{current_position} of {total_item_no}')
    response_json = json.loads(response.content)
    total_item = response_json['results']
    for i in total_item:
        item_names_list.append(i['hash_name'])
print (item_names_list)
item_names_list_count = len(item_names_list)
print (f'Total number of skin in list {item_names_list_count}')
item_names_set = set(item_names_list)
item_names_set_count = len(item_names_set)
print(f'Total number of skins in set = {item_names_set_count}')


item_names_list = list(item_names_set)

with open('skin_name.txt' , 'wb') as file:
    pickle.dump(item_names_list, file)
    print('Done writing list into a binary file')

with open('skin_name.txt', 'rb') as file:
    item_names_list = pickle.load(file)
# print (item_names_list)

allItemsPD = pd.DataFrame(data=None, index=None, columns = ['itemName', 'priceAvg', 'maxPrice', 'minPrice', 'totalVol'])
currentNumber = 1

for i in item_names_list:
    itemHTTP = i.replace(" ", '%20')
    itemHTTP = i.replace("&", '%26')
    # print(itemHTTP)
    response = requests.get('https://steamcommunity.com/market/pricehistory/?appid='+game_code+'&market_hash_name='+itemHTTP, cookies=cookie)
    print(response)
    print (f'{currentNumber} out of {len(item_names_list)} code: {response.status_code}')
    currentNumber += 1
    response = response.content
    # print (response)
    response_json = json.loads(response)
    # print (response_json)

    if response_json:
        itemPriceData = response_json['prices']
        if itemPriceData is False:
            continue
        else:

            price = []
            volume = []
            date = []
            for currPrice in itemPriceData:
                price.append(currPrice[1])
                volume.append(currPrice[2])
                date.append(time.strptime(currPrice[0][0:11], '%b %d %Y'))

            price = list(map(float, price))
            volume = list(map(int, volume))


            avgPrice = np.mean(price)
            maxPrice = max(price, default=0)
            minPrice = min(price, default=0)
            totalVol = sum(volume)

            item_data_dictionary = {'itemName': i, 'priceAvg': avgPrice, 'maxPrice': maxPrice, 'minPrice': minPrice, 'totalVol': totalVol}
            alldata = pd.DataFrame(item_data_dictionary, index=[0])
            # print(alldata)
            # alldataPD = alldataPD.append(alldata)

            allItemsPD = pd.concat([allItemsPD,alldata])

    else:
        continue
print(allItemsPD)
# print(alldata)

allItemsPD.to_pickle('PriceData.pkl')



