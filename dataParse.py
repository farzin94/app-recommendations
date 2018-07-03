import csv
import time
import datetime

appId = []
review_appId = []
memberId = []
appTitle= []
appRatingCount= []
date = []

appName = []
appCat = []

with open("app_view.csv", 'rb') as appFile:
    reader = csv.DictReader(appFile, delimiter=',', doublequote=True, escapechar='\\')
    for row in reader:
        appId.append(row['app_id'])
        appTitle.append(row['title'])

with open("member_app_review.csv", 'rb') as appFile:
    reader = csv.DictReader(appFile, delimiter=',', doublequote=True, escapechar='\\')
    for row in reader:
        review_appId.append(row['app_id'])
        memberId.append(row['member_id'])
        appRatingCount.append(row['rating'])
        date.append(row['created_date'])

with open("apps_categories.csv", 'rb') as appCatFile:
    reader = csv.DictReader(appCatFile, delimiter=',', doublequote=True, escapechar='\\')
    for row in reader:
        appName.append(row['App'])
        appCat.append(row['Solution'])

with open('app_clean.csv', 'w') as csvfile:
    fieldnames = ['user', 'item','rating', 'timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
    for i in range(len(review_appId)):
        if review_appId[i] in appId:
            writer.writerow({'user': memberId[i].decode('utf-8').encode('ascii', 'ignore'),
                             'item': review_appId[i],
                             'rating': appRatingCount[i],
                             'timestamp': time.mktime(datetime.datetime.strptime(date[i], "%Y-%m-%d %H:%M:%S").timetuple())
                             })

with open('app_item_only.csv', 'w') as csvfile:
    fieldnames = ['app_id', 'title']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    for i in range(len(appId)):
        writer.writerow({'app_id': appId[i],
                         'title': appTitle[i]
                         })

with open('apps_categories_clean.csv', 'w') as csvfile:
    fieldnames = ['item', 'category']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    for i in range(len(appName)):
        writer.writerow({'item': appName[i],
                         'category': appCat[i]
                         })