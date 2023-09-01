import sys
import os
import requests
import argparse
import concurrent.futures
import random
import time
from datetime import datetime
import re
import pickle
import csv
import io

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

api_keys_dict = {'gp762nuuoqcoxypju8c569th9wz7q5': 'Bearer w5e2zmbpgpiri3c1kya6i4fo7txz3r', 'gp762nuuoqcoxypju8c569th9wz7q5': 'Bearer zuln03s672r6udltan4mrfakwss4xf', 'gp762nuuoqcoxypju8c569th9wz7q5': 'Bearer qgmwpro6dc0z5ete1clw8rvxyx5p6n'}
user_agent_list = ['Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36']

def get_response(url, params, tries=1610612741):
    for _ in range(tries):
        random_client_id = random.choice(list(api_keys_dict.keys()))
        headers = {
        'Authorization': api_keys_dict[random_client_id],
        'Client-Id': random_client_id,
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            return(response)
        except Exception as e:
            print(e)
            time.sleep(random.uniform(0.02, 0.5))

def get_user_by_name(user_name):
    time.sleep(random.uniform(0.05, 0.5))
    url = 'https://api.twitch.tv/helix/users'
    params = {
        'login': user_name,
    }
    try:
        time.sleep(random.uniform(0.05, 0.5))
        response = get_response(url, params)
        data = response.json()['data'][0]
        twitch_dictionary[user_name]['user_metadata'] = {'id': data['id'], 'display_name': data['display_name'], 'login': data['login'], 'profile_image_url': data['profile_image_url'], 'offline_image_url': data['offline_image_url'], 'created_at': data['created_at']}
        print(f"INSERTED metadata for {user_name} successfully!")
    except Exception as e:
        print(f"COULD NOT insert metadata for {user_name}!", e)

def thread_get_user(user_list, max_threads=150):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(get_user_by_name, user) for user in user_list]
        concurrent.futures.wait(futures)
    
def get_user_id(user_name):
    time.sleep(random.uniform(0.05, 0.5))
    url = 'https://api.twitch.tv/helix/users'
    params = {
        'login': user_name,
    }
    try:    
        response = get_response(url, params)
        return(response.json()['data'][0]['id'])
    except Exception as e:
        print(f"couldn't get user id for {user_name}", e)
        return(None)

def get_top_streams(game_id=None, pages=1000):
    time.sleep(random.uniform(0.05, 0.2))
    top_streamers = set()
    url = 'https://api.twitch.tv/helix/streams'
    params = {
        'first': 100,
    }
    if game_id:
        params['game_id'] = int(game_id)
    try:
        response = get_response(url, params)
    except Exception as e:
        print('line 78', e)
        return(top_streamers)
    for i in response.json()['data']:
        try:
            user_name = i['user_name'].lower()
            if user_name in twitch_dictionary:
                twitch_dictionary[user_name]['user_id'] = i['user_id']
                twitch_dictionary[user_name]['video_dict'][i['id']] = i
            else:
                twitch_dictionary[user_name] = {'user_name': user_name, 'video_dict': {}, 'user_metadata': {}}
                twitch_dictionary[user_name]['user_id'] = i['user_id']
                twitch_dictionary[user_name]['video_dict'][i['id']] = i
            print(f"added {user_name}")
        except Exception as e:
            print(f"couldn't add user-name {user_name} to top stramers", e)
    
    for i in range(pages):
        try: 
            pag = response.json()['pagination']['cursor']
        except Exception as e:
            print('line 92', e)
            return(top_streamers)
        params = {
            'first': 100,
            'after': pag,
        }
        try:
            response = get_response(url, params)
            for i in response.json()['data']:
                try:
                    user_name = i['user_name'].lower()
                    if user_name in twitch_dictionary:
                        twitch_dictionary[user_name]['user_id'] = i['user_id']
                        twitch_dictionary[user_name]['video_dict'][i['id']] = i
                    else:
                        twitch_dictionary[user_name] = {'user_name': user_name, 'video_dict': {}, 'user_metadata': {}}
                        twitch_dictionary[user_name]['user_id'] = i['user_id']
                        twitch_dictionary[user_name]['video_dict'][i['id']] = i
                    top_streamers.add(user_name)
                    print(f"added {user_name}")
                except Exception as e:
                    print(f"could not add {user_name} to top_streamers", e)
        except Exception as e:
            print('line 108', e)
    return(top_streamers)

def get_streamer_videos(user_name):
    time.sleep(random.uniform(0.05, 0.5))
    try:
        user_id = get_user_id(user_name)
        if user_id is None:
            pass
        else:
            twitch_dictionary[user_name]['user_id'] = user_id
            print(f'added user id {user_id} for {user_name}')
    except Exception as e:
        print('line 118', e)
        return
    url = 'https://api.twitch.tv/helix/videos'
    params = {
        'first' : 100,
        'user_id': user_id,
    }
    try:    
        response = get_response(url, params)
        data = response.json()
    except Exception as e:
        print(e)
        print(f"Cannot get response for get_streamer_videos({user_name})!")
    try:
        for v in data['data']:
            if v['id'] in twitch_dictionary[user_name]['video_dict']:
                return
            else:
                try:
                    twitch_dictionary[user_name]['video_dict'][v['id']] = {'id': v['id'], 'title': v['title'], 'created_at': v['created_at'], 'published_at': v['published_at'], 'duration': v['duration'], 'thumbnail_url': v['thumbnail_url'], 'view_count': v['view_count'], 'language': v['language']}                    
                    print(f"ADDED video id {v['id']} for user {user_name}")
                except Exception as e:
                    print(f"COULD NOT ADD VIDEO ID {v['id']} for user {user_name}", e)
    except Exception as e:
        print(e)
        return
    try:
        pag = data['pagination']['cursor']
    except Exception as e:
        print(e)
        return
    while True:
        url = f'https://api.twitch.tv/helix/videos?user_id={user_id}'
        params = {
            'first' : 100,
            'after': pag,
        }
        try:
            response = get_response(url, params)
            data = response.json()
        except Exception as e:
            print(e)
            return
        try:
            for v in data['data']:
                if v['id'] in twitch_dictionary[user_name]['video_dict']:
                    return
                else:
                    try:
                        twitch_dictionary[user_name]['video_dict'][v['id']] = {'id': v['id'], 'title': v['title'], 'created_at': v['created_at'], 'published_at': v['published_at'], 'duration': v['duration'], 'thumbnail_url': v['thumbnail_url'], 'view_count': v['view_count'], 'language': v['language']}                    
                        print(f"ADDED video id {v['id']} for user {user_name}")
                    except Exception as e:
                        print(e)
                        print(f"COULD NOT ADD VIDEO ID {v['id']} for user {user_name}")
        except Exception as e:
            print("error in adding videos", e)
            return
        try:
            pag = data['pagination']['cursor']
        except Exception as e:
            print(e)
            return
#1610612741
def thread_get_streamer(streamer_list, max_threads=150):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(get_streamer_videos, streamer) for streamer in streamer_list]
        concurrent.futures.wait(futures)

def is_english(string):
  pattern = re.compile(r'^[a-zA-Z]+$')
  return pattern.match(string) is not None

def get_profile_picture(streamer):
    if is_english(streamer):
        try:
            chromedriver_executable = Service('chromedriver')
            options = Options()
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--headless") 
            options.add_argument("--no-sandbox")
            options.add_argument("--incognito")
            options.add_argument("--disable-dev-shm-usage")
            #options.add_argument("--disable-blink-features=AutomationControlled") 
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-extensions")
            options.add_argument('--ignore-ssl-errors')
            options.add_argument("--disable-blink-features")
            random_user_agent = random.choice(user_agent_list)
            options.add_argument(f"user-agent={random_user_agent}")
            driver = webdriver.Chrome(service = chromedriver_executable, options = options)
            driver.set_window_size(1920, 1080*3)
            driver.get(f"https://twitch.tv/{streamer}")
            user_agent = driver.execute_script("return window.navigator.userAgent")
            is_webdriver = driver.execute_script("return window.navigator.webdriver")
            print("User Agent:", user_agent)
            print("Webdriver is", is_webdriver)
            time.sleep(random.uniform(5.5, 6.5))
            try:
                os.system(f"mkdir screenshots/{streamer} > /dev/null 2>&1")
            except:
                pass
            driver.save_screenshot(f"screenshots/{streamer}/{get_timestamp()}_{streamer}.png")
            # image = full_page_screenshot(driver)
            # image.save(f"screenshots/{streamer}/{get_timestamp()}_{streamer}.png")
            print(f"saved screenshot for {streamer} on {get_timestamp()}")
            driver.get(f"https://twitch.tv/{streamer}/about")
            time.sleep(random.uniform(5.5, 6.5))
            driver.save_screenshot(f"screenshots/{streamer}/about/{get_timestamp()}_{streamer}.png")
            print(f"saved screenshot for {streamer} about section on {get_timestamp()}")
            # image = full_page_screenshot(driver)
            # image.save(f"screenshots/{streamer}/{get_timestamp()}_{streamer}.png")
        except Exception as e:
            print(e)
            print(f"could not save screenshot for {streamer} on {get_timestamp()}")

def thread_profile_picture(streamer_list, max_threads=10):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(get_profile_picture, streamer) for streamer in streamer_list]
        concurrent.futures.wait(futures)

def get_timestamp():
    timestamp = datetime.now()
    timestr = str(timestamp).replace(' ', '_')
    timestr = timestr.replace(':', '-')
    timestr = timestr[:-7]
    return timestr

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Usage of dl_twitch.py:')
    parser.add_argument('streamers', nargs=argparse.REMAINDER, help='command line arugments for specific streamer names')
    # parser.add_argument('--games', type=str, help='get all data from specific games query; eg query casino to get all casino games including slots, blackjack, etc.')
    args = parser.parse_args()
    # games_query = args.games
    # print("Games query:", games_query)
    # game_ids_list = []
    # if games_query:
    #     get_top_games.main()
    #     with open("top_games.pickle", "rb") as f:
    #             top_games = pickle.load(f)
    #     for game in top_games:
    #         if games_query.lower() in game.lower():
    #             game_ids_list.append(top_games[game]['id'])
    # print("Game IDs List: ", game_ids_list)
    if os.path.exists("twitch_dictionary.pickle"):
        with open("twitch_dictionary.pickle", "rb") as f:
            twitch_dictionary = pickle.load(f)
    else:
        twitch_dictionary = {}

    if args.streamers:
        for streamer in args.streamers:
            if streamer != '--ONLY' and streamer != '--NOUPDATE':
                streamer_lower = streamer.lower() 
                if streamer_lower not in twitch_dictionary:
                    twitch_dictionary[streamer_lower] = {'user_name': streamer_lower, 'video_dict': {}, 'user_metadata': {}}
                    get_user_by_name(streamer_lower)
                    get_streamer_videos(streamer_lower)

    if "--ONLY" in sys.argv:
        with open("twitch_dictionary.pickle", "wb") as f:
            pickle.dump(twitch_dictionary, f)        
        sys.exit(0)

    # if len(game_ids_list) > 0:
    #     for game_id in game_ids_list:
    #         top_streamers = get_top_streams(game_id)
    #         s_list = list(top_streamers)
    #         thread_get_streamer(s_list)
    # else:
    top_streamers = get_top_streams()

    if '--NOUPDATE' in sys.argv:
        sys.exit(0)
    streamer_list = []
    for key, value in twitch_dictionary.items():
        streamer_list.append(key)

    random.shuffle(streamer_list)

    thread_get_user(streamer_list)

    with open("twitch_dictionary.pickle", "wb") as f:
        pickle.dump(twitch_dictionary, f)

    #thread_get_streamer(streamer_list)

    one_part = len(streamer_list) // 4

    one_of_four = streamer_list[:one_part]
    thread_get_streamer(one_of_four)
    with open("twitch_dictionary.pickle", "wb") as f:
        pickle.dump(twitch_dictionary, f)
    two_of_four = streamer_list[one_part:one_part*2]
    thread_get_streamer(two_of_four)
    with open("twitch_dictionary.pickle", "wb") as f:
        pickle.dump(twitch_dictionary, f)
    three_of_four = streamer_list[one_part*2: one_part*3]
    thread_get_streamer(three_of_four)
    with open("twitch_dictionary.pickle", "wb") as f:
        pickle.dump(twitch_dictionary, f)
    four_of_four = streamer_list[one_part*3:]
    thread_get_streamer(four_of_four)

    with open("twitch_dictionary.pickle", "wb") as f:
        pickle.dump(twitch_dictionary, f)