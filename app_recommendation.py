# # Overall Behavior Expectations:
# # Must be based on user installs and ratings
#
# # User rated something higher than a 4, what is
# # Input: "Evernote" Output: "Trello, "
#
# # Figure out what data I have to work with
#
# # search terms!?
# # app categories
# # app reviews per user
# # app installs per user
#
# # phase 1:
# # based off app installs per user and categories
# # sklearn scikit surprise
#
# # possibly give recommendations based off people with similar apps
import os
import csv

from surprise import Reader, Dataset, SVD, evaluate, NormalPredictor, KNNBaseline
from sys import argv
from collections import defaultdict

def read_item_names():
    """Read the u.item file from MovieLens 100-k dataset and return two
    mappings to convert raw ids into movie names and movie names into raw ids.
    """
    file_name = 'app_item_only.csv'
    rid_to_name = {}
    name_to_rid = {}
    with open(file_name, 'rb') as f:
        reader = csv.reader(f, delimiter=',')
        for line in reader:
            rid_to_name[line[0]] = line[1]
            name_to_rid[line[1]] = line[0]

    return rid_to_name, name_to_rid

def get_data(path, line_format):
    file_path = os.path.expanduser(path)
    reader = Reader(line_format=line_format, sep='\t')
    return Dataset.load_from_file(file_path, reader=reader)

def get_categories():
    app_to_category = {}
    category_to_app = {}
    categories = []
    rows = []
    file_name = 'apps_categories.csv'
    with open(file_name, 'rb') as appCatFile:
        reader = csv.DictReader(appCatFile, delimiter=',', doublequote=True, escapechar='\\')
        for row in reader:
            categories.append(row['Solution'])
            rows.append(row)
        category_to_app = {key:[] for key in categories}
        for row in rows:
            app_to_category[row['App'].strip()] = row['Solution']
            category_to_app[row['Solution']].append(row['App'])
    return app_to_category, category_to_app, set(categories)

def get_top_n(predictions, n=10):
    '''Return the top-N recommendation for each user from a set of predictions.

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.

    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    '''

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

def get_user_recommendations() :
    data = get_data('app_clean.csv', 'user item rating timestamp')

    recommendations = []
    trainset = data.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)

    # Than predict ratings for all pairs (u, i) that are NOT in the training set.
    testset = trainset.build_anti_testset()
    predictions = algo.test(testset)

    top_n = get_top_n(predictions, n=10)

    # Return the recommended items for each user
    for uid, user_ratings in top_n.items():
        recommendations += uid, [iid for (iid, _) in user_ratings]

    return recommendations

def main() :

    data = get_data('app_clean.csv', 'user item rating timestamp')
    trainset = data.build_full_trainset()

    sim_options = {'name': 'msd','user_based': False}
    algo = KNNBaseline(sim_options=sim_options)
    algo.fit(trainset)

    # get app name and convert to
    app_input = argv[1].strip()
    rid_to_name, name_to_rid = read_item_names()
    inner_id = algo.trainset.to_inner_iid(name_to_rid[app_input])
    # get neighbours and convert to app names
    neighbors = algo.get_neighbors(inner_id, k = 5)
    neighbors = (algo.trainset.to_raw_iid(inner_ids) for inner_ids in neighbors)
    neighbors = (rid_to_name[rid] for rid in neighbors)

    print get_user_recommendations()
    # print neighbours
    print "Apps that are available in the app directory similar to",rid_to_name[algo.trainset.to_raw_iid(inner_id)]
    for app in neighbors:
        print app

    app_to_category, category_to_app, all_categories = get_categories()
    if app_input in app_to_category:
        category = app_to_category[app_input]
        print "Other apps in this category:", category
        print category_to_app[category]

if __name__ == "__main__":
    main()
