import asyncio
import os
import time

import django
import schedule

from coreNews.parser import main

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReadAndGo.settings')
django.setup()
from django.db import transaction

from coreNews.models import News


def data_in_database():

    info = asyncio.run(main())

    with transaction.atomic():
        News.objects.all().delete()

        news_instances = []
        for source, data in info.items():
            publisher = source
            for urls, content in data.items():
                url = urls
                article_title = content['title']
                short_text = content['short_text']
                news_instances.append(News(publisher=publisher, url=url, title=article_title, short_text=short_text))

        News.objects.bulk_create(news_instances)


if __name__ == '__main__':
    data_in_database()
    schedule.every(3600).seconds.do(data_in_database)

    while True:
        schedule.run_pending()
        time.sleep(1)
