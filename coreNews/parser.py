import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup
from groq import Groq
from random_user_agent.user_agent import UserAgent
import environ
from ReadAndGo.settings import BASE_DIR

env = environ.Env(GROQ_API_KEY=(str))
environ.Env.read_env(BASE_DIR / '.env')
random_headers = UserAgent()
header = {'User-Agent': random_headers.get_random_user_agent()}
news_data = {}


# Asynchronous function to fetch a webpage and return a BeautifulSoup object
async def fetch_page(url, session):
    try:
        async with session.get(url) as response:
            html_content = await response.text()
            return BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        print(e)
        return None


# Function to summarize text using the Groq API
def keeper_sync(text):
    try:
        client = Groq(
            api_key='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',
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Your task is to summarize the following text, making it as concise as possible while retaining its essential meaning and key points. Please ensure that the summary is clear, coherent, and accurately reflects the original content.Number each article."
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama3-8b-8192",
        )
        result = chat_completion.choices[0].message.content
        return result
    except Exception as e:
        print(e)
        return None


# Asynchronous wrapper for the synchronous Groq API call
async def keeper(text):
    return await asyncio.to_thread(keeper_sync, text)


# Function to clean and combine article data
async def clean_article_data(text):
    cleaned_text = re.sub(r'\*\*Article \d+:? [^\*]*\*\*', '', text)
    lines = cleaned_text.split('\n')
    del lines[0]

    combined_lines = []
    temp_line = ""
    for line in lines:
        line = line.strip()
        if line.startswith('**'):
            continue
        elif line.startswith('*'):
            temp_line += " " + line[1:].strip()
        else:
            if temp_line:
                combined_lines.append(temp_line)
                temp_line = ""
            if line:
                combined_lines.append(line)
    if temp_line:
        combined_lines.append(temp_line)

    return combined_lines


# Function to process each news site
async def process_site(fetch_func, url, session):
    try:
        outcome = await fetch_func(url, session)
    except Exception as e:
        print(e)


# Functions to fetch and process news from different sources
async def esspreso(url, session):
    soup = await fetch_page(url, session)
    important_news = soup.find_all('div', class_='news-tape-important')
    article_num = 1
    data_for_llama = ''
    data = {}
    for news in important_news[:3]:
        link = news.find('a').get('href')
        soup2 = await fetch_page(link, session)
        title = soup2.find('h1').text
        article = soup2.find('div', class_='news-content').get_text().strip()
        clear_article = article.replace('\n', '')
        data_for_llama += f'## Article {article_num}\n{clear_article}\n'
        article_num += 1
        data[link] = {
            'title': title,
            'short_text': ''
        }

    llama_article = await keeper(data_for_llama)
    normal_text = await clean_article_data(llama_article)
    try:
        for i, (url, article_data) in enumerate(data.items()):
            article_data['short_text'] = normal_text[i].strip()
    except Exception as e:
        pass

    news_data['esspreso'] = data
    print('%%% Espreso Done %%%')


async def ekathimerini(url, session):
    soup = await fetch_page(url, session)
    important_news = soup.find_all('div', class_='article_thumbnail_wrapper')
    article_num = 1
    data_for_llama = ''
    data = {}
    for news in important_news[:3]:
        link = news.find('a').get('href')
        soup2 = await fetch_page(link, session)
        try:
            title = soup2.find('h1').text
            article = soup2.find('div', class_='entry-content').get_text().strip()
            clear_article = article.replace('\n', '')
            data_for_llama += f'## Article {article_num}\n{clear_article}\n'
            article_num += 1
            data[link] = {
                'title': title,
                'short_text': ''
            }
        except Exception as e:
            continue

    llama_article = await keeper(data_for_llama)
    normal_text = await clean_article_data(llama_article)
    try:
        for i, (url, article_data) in enumerate(data.items()):
            article_data['short_text'] = normal_text[i].strip()
    except Exception as e:
        pass

    news_data['ekathimerini'] = data
    print('%%% Ekathemarini Done %%%')


async def new_yorker(url, session):
    try:
        soup = await fetch_page(url, session)
        important_news = 'https://www.newyorker.com' + soup.find('a', class_='SummaryItemHedLink-civMjp').get('href')
        data = {}
        soup2 = await fetch_page(important_news, session)
        title = soup2.find('h1').text
        article = soup2.find('div', class_='body__inner-container').get_text().strip()
        clear_article = article.replace('\n', '')
        short_article = await keeper(clear_article)
        link_data = {
            'title': title,
            'short_text': short_article
        }
        data[important_news] = link_data
        news_data['new_yorker'] = data
    except Exception as e:
        pass

    print('%%% New Yorker Done %%%')


async def unian(url, session):
    soup = await fetch_page(url, session)
    counter = 0
    data_for_llama = ''
    article_num = 1
    data = {}
    for h3 in soup.select('h3 a'):
        link = h3['href'].strip()
        title = h3.get_text().strip()
        soup2 = await fetch_page(link, session)
        article = soup2.find('div', class_='article-text').get_text().strip()
        clear_article = article.replace('\n', '')
        data_for_llama += f'## Article {article_num}\n{clear_article}\n'
        article_num += 1
        data[link] = {
            'title': title,
            'short_text': ''
        }

        counter += 1
        if counter >= 3:
            break

    llama_article = await keeper(data_for_llama)
    normal_text = await clean_article_data(llama_article)
    try:
        for i, (url, article_data) in enumerate(data.items()):
            article_data['short_text'] = normal_text[i].strip()
    except Exception as e:
        pass

    news_data['unian'] = data
    print('%%% Unian Done %%%')


async def nv(url, session):
    soup = await fetch_page(url, session)
    counter = 0
    data_for_llama = ''
    article_num = 1
    data = {}
    feed_items = soup.select('div.tab.active .feed-item')
    for item in feed_items:
        link = item.select_one('a.feed-item-title')['href'].strip()
        title = item.select_one('a.feed-item-title').get_text().strip()
        soup2 = await fetch_page(link, session)
        try:
            article = soup2.find('div', class_='content_wrapper').get_text().strip()
            clear_article = article.replace('\n', '')
            data_for_llama += f'## Article {article_num}\n{clear_article}\n'
            article_num += 1
            data[link] = {
                'title': title,
                'short_text': ''
            }
        except Exception as e:
            continue

        counter += 1
        if counter >= 3:
            break

    llama_article = await keeper(data_for_llama)
    normal_text = await clean_article_data(llama_article)
    try:
        for i, (url, article_data) in enumerate(data.items()):
            article_data['short_text'] = normal_text[i].strip()
    except Exception as e:
        pass

    news_data['nv'] = data
    print('%%% NV Done %%%')


async def korespondent(url, session):
    soup = await fetch_page(url, session)
    counter = 0
    data = {}
    data_for_llama = ''
    article_num = 1
    for article in soup.select('div.article__title'):
        link = article.select_one('a')['href'].strip()
        title = article.select_one('a').get_text().strip()
        soup2 = await fetch_page(link, session)
        article = soup2.find('div', class_='post-item__text').get_text().strip()
        clear_article = article.replace('\n', '')
        data_for_llama += f'## Article {article_num}\n{clear_article}\n'
        article_num += 1
        data[link] = {
            'title': title,
            'short_text': ''
        }

        counter += 1
        if counter >= 3:
            break

    llama_article = await keeper(data_for_llama)
    try:
        normal_text = await clean_article_data(llama_article)
        for i, (url, article_data) in enumerate(data.items()):
            article_data['short_text'] = normal_text[i].strip()
    except Exception as e:
        pass

    news_data['korespondent'] = data
    print('%%% Korespondent Done %%%')


async def tsn(url, session):
    soup = await fetch_page(url, session)
    counter = 0
    data = {}
    data_for_llama = ''
    article_num = 1
    for article in soup.select('article.c-card'):
        link = article.select_one('h3.c-card__title a')['href'].strip()
        title = article.select_one('h3.c-card__title a').get_text().strip()
        soup2 = await fetch_page(link, session)
        article = soup2.find('div', class_='c-article__body').get_text().strip()
        clear_article = article.replace('\n', '')
        data_for_llama += f'## Article {article_num}\n{clear_article}\n'
        article_num += 1
        data[link] = {
            'title': title,
            'short_text': ''
        }

        counter += 1
        if counter >= 3:
            break

    llama_article = await keeper(data_for_llama)
    normal_text = await clean_article_data(llama_article)
    try:
        for i, (url, article_data) in enumerate(data.items()):
            article_data['short_text'] = normal_text[i].strip()
    except Exception as e:
        pass

    news_data['tsn'] = data
    print('%%% TSN Done %%%')


async def pravda(url, session):
    soup = await fetch_page(url, session)
    counter = 0
    data_for_llama = ''
    article_num = 1
    data = {}
    for article in soup.select('div.article_news_bold'):
        link = "https://www.pravda.com.ua" + article.select_one('a')['href'].strip()
        title = article.select_one('a').get_text().strip()
        try:
            soup2 = await fetch_page(link, session)
            if soup2:
                article_text = soup2.find('div', class_='post_text').get_text().strip()
                clear_article = article_text.replace('\n', '')
                data_for_llama += f'## Article {article_num}\n{clear_article}\n'
                article_num += 1
                data[link] = {
                    'title': title,
                    'short_text': ''
                }
            else:
                continue
        except Exception as e:
            continue

        counter += 1
        if counter >= 3:
            break

    llama_article = await keeper(data_for_llama)
    normal_text = await clean_article_data(llama_article)
    try:
        for i, (url, article_data) in enumerate(data.items()):
            article_data['short_text'] = normal_text[i].strip()
    except Exception as e:
        pass

    news_data['pravda'] = data
    print('%%% Pravda Done %%%')


async def cnn(url, session):
    soup = await fetch_page(url, session)
    counter = 0
    data_for_llama = ''
    article_num = 1
    data = {}
    for article in soup.select('div.container__item--type-media-image'):
        link = "https://edition.cnn.com" + article.select_one('a')['href'].strip()
        title = article.select_one('span').get_text().strip()
        if title == 'Live Updates':
            continue
        else:
            try:
                soup2 = await fetch_page(link, session)
                article = soup2.find('div', class_='article__content').get_text().strip()
                clear_article = article.replace('\n', '')
                data_for_llama += f'## Article {article_num}\n{clear_article}\n'
                article_num += 1
                data[link] = {
                    'title': title,
                    'short_text': ''
                }
            except Exception as e:
                continue

        counter += 1
        if counter >= 3:
            break

    llama_article = await keeper(data_for_llama)
    normal_text = await clean_article_data(llama_article)
    try:
        for i, (url, article_data) in enumerate(data.items()):
            article_data['short_text'] = normal_text[i].strip()
    except Exception as e:
        pass

    news_data['cnn'] = data
    print('%%% CNN Done %%%')


async def euronews(url, session):
    soup = await fetch_page(url, session)
    counter = 0
    data_for_llama = ''
    article_num = 1
    data = {}
    for article in soup.select('div.c-most-viewed__article'):
        link = "https://www.euronews.com" + article.select_one('a')['href'].strip()
        title = article.select_one('a').get_text().strip()
        soup2 = await fetch_page(link, session)
        article = soup2.find('div', class_='c-article-content').get_text().strip()
        clear_article = article.replace('\n', '')
        data_for_llama += f'## Article {article_num}\n{clear_article}\n'
        article_num += 1
        data[link] = {
            'title': title,
            'short_text': ''
        }

        counter += 1
        if counter >= 3:
            break

    llama_article = await keeper(data_for_llama)
    normal_text = await clean_article_data(llama_article)
    try:
        for i, (url, article_data) in enumerate(data.items()):
            article_data['short_text'] = normal_text[i].strip()
    except Exception as e:
        pass

    news_data['euronews'] = data
    print('%%% EuroNews Done %%%')


async def times(url, session):
    try:
        soup = await fetch_page(url, session)
        counter = 0
        data_for_llama = ''
        article_num = 1
        data = {}
        for article in soup.select('li.css-1iski2w'):
            link = article.select_one('a')['href'].strip()
            title = article.select_one('h1').get_text().strip()
            try:
                soup2 = await fetch_page(link, session)
                article = soup2.find('article', class_='e1lmdhsb0').get_text().strip()
                clear_article = article.replace('\n', '')
                data_for_llama += f'## Article {article_num}\n{clear_article}\n'
                article_num += 1
                data[link] = {
                    'title': title,
                    'short_text': ''
                }
            except Exception as e:
                continue

            counter += 1
            if counter >= 3:
                break

        llama_article = await keeper(data_for_llama)
        normal_text = await clean_article_data(llama_article)
        try:
            for i, (url, article_data) in enumerate(data.items()):
                article_data['short_text'] = normal_text[i].strip()
        except Exception as e:
            pass
        news_data['times'] = data
    except Exception as e:
        print(e)
    print('%%% Times Done %%%')


async def ukrnet(url, session):
    soup = await fetch_page(url, session)
    important_news = soup.find_all("section", class_="im")
    data = {}
    data_for_llama = ''
    article_num = 1
    for news in important_news[:3]:
        links = news.find('a').get('href')
        soup2 = await fetch_page(links, session)
        try:
            important_news2 = soup2.find("section", class_="im").find('a').get('href')
            soup3 = await fetch_page(important_news2, session)
            title = soup3.find('h1').text
            article = soup3.get_text()
            clear_article = article.replace('\n', '')
            data_for_llama += f'## Article {article_num}\n{clear_article}\n'
            article_num += 1
            data[important_news2] = {
                'title': title,
                'short_text': ''
            }
        except Exception as e:
            continue

    llama_article = await keeper(data_for_llama)
    try:
        normal_text = await clean_article_data(llama_article)
        for i, (url, article_data) in enumerate(data.items()):
            article_data['short_text'] = normal_text[i].strip()
    except Exception as e:
        pass

    news_data['ukrnet'] = data
    print('%%% UkrNet Done %%%')


# Main function to orchestrate the fetching and processing of all news sites
async def main():
    async with aiohttp.ClientSession(headers=header) as session:
        tasks = [
            asyncio.create_task(process_site(esspreso, 'https://espreso.tv/', session)),
            asyncio.create_task(process_site(ekathimerini, 'https://www.ekathimerini.com/', session)),
            asyncio.create_task(process_site(unian, 'https://www.unian.ua/detail/main_news', session)),
            asyncio.create_task(process_site(new_yorker, 'https://www.newyorker.com/news', session)),
            asyncio.create_task(process_site(pravda, 'https://www.pravda.com.ua/news/', session)),
            asyncio.create_task(process_site(korespondent, 'https://ua.korrespondent.net/', session)),
            asyncio.create_task(process_site(ukrnet, 'https://www.ukr.net/news/main.html', session)),
            asyncio.create_task(process_site(times, 'https://www.nytimes.com/trending/', session)),
            asyncio.create_task(process_site(euronews, 'https://www.euronews.com/', session)),
            asyncio.create_task(process_site(cnn, 'https://edition.cnn.com/world', session)),
            asyncio.create_task(process_site(tsn, 'https://tsn.ua/', session)),
            asyncio.create_task(process_site(nv, 'https://nv.ua/', session))
        ]
        await asyncio.gather(*tasks)

    return news_data
