import pickle
import sys
with open ("twitch_dictionary.pickle", 'rb') as f:
    twitch_dict = pickle.load(f)

print(f"There are {len(twitch_dict)} currently in twitch_dictionary.pickle")

print(twitch_dict[sys.argv[1]]['user_metadata'])
print(twitch_dict[sys.argv[1]]['video_dict'].keys())