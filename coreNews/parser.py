import asyncio

import aiohttp
from bs4 import BeautifulSoup
from groq import Groq
from random_user_agent.user_agent import UserAgent
import environ
from ReadAndGo.settings import BASE_DIR

env = environ.Env(GROQ_API_KEY=(str))
environ.Env.read_env(BASE_DIR / '.env')
random_headers = UserAgent()
news_data = {}


async def fetch_page(url):
    header = {'User-Agent': random_headers.get_random_user_agent()}
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(url) as response:
            html_content = await response.text()
            return BeautifulSoup(html_content, 'html.parser')


def keeper(text):
    client = Groq(
        api_key=env('GROQ_API_KEY'),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": 'Summarize short texts while retaining the original language. Instructions: 1. Provide the full text of the news article in its original language as input. 2. Identify the main ideas and key points of the news article. 3. Condense the text as much as possible, keeping only the most important information. 4. Ensure the output summary is in the same language as the input news article. Example Input: "Yesterday in Kyiv, a significant protest took place, gathering over a thousand people to express their disagreement with new laws. Speakers emphasized the importance of maintaining democratic principles. The police maintained order, and no incidents were reported." Expected Output: "Yesterday in Kyiv, a protest with over a thousand participants occurred against new laws. Speakers highlighted the importance of upholding democratic principles. The police ensured order, and no incidents were reported.'
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


async def esspreso(url):
    soup = await fetch_page(url)
    important_news = soup.find_all('div', class_='news-tape-important')

    data = {}
    for news in important_news[:3]:
        urls = news.find('a').get('href')
        soup2 = await fetch_page(urls)
        title = soup2.find('h1').text
        article = soup2.find('div', class_='news-content').get_text().strip()
        clear_article = article.replace('\n', '')
        short_article = keeper(clear_article)
        link_data = {
            'title': title,
            'short_text': short_article
        }
        data[urls] = link_data
    news_data['esspreso'] = data

    return 'Esspreso Done!'


async def guardian(url):
    soup = await fetch_page(url)
    important_news = soup.find('div', class_='dcr-16c50tn').find_all('li')

    data = {}
    for news in important_news[:3]:
        get_links = news.find('a').get('href')
        urls = 'https://www.theguardian.com' + get_links
        soup2 = await fetch_page(urls)
        title = soup2.find('h1').text
        try:
            article = soup2.find('div', class_='dcr-fp1ya').get_text().strip()
        except Exception as e:
            article = soup2.find('article', class_='dcr-1os4bxs').get_text().strip()
        clear_article = article.replace('\n', '')
        short_article = keeper(clear_article)
        link_data = {
            'title': title,
            'short_text': short_article
        }
        data[urls] = link_data
    news_data['guardian'] = data

    return 'Guardian Done!'


async def ekathimerini(url):
    soup = await fetch_page(url)
    important_news = soup.find_all('div', class_='article_thumbnail_wrapper')
    data = {}
    for news in important_news[:3]:
        urls = news.find('a').get('href')
        soup2 = await fetch_page(urls)
        try:
            title = soup2.find('h1').text
            article = soup2.find('div', class_='entry-content').get_text().strip()
            clear_article = article.replace('\n', '')
            short_article = keeper(clear_article)
            link_data = {
                'title': title,
                'short_text': short_article
            }
            data[urls] = link_data
        except Exception as e:
            continue
    news_data['ekathimerini'] = data

    return 'Ekathimerini Done!'


async def south_china(url):
    try:
        soup = await fetch_page(url)
        important_news = soup.find_all('a', class_='e10huebq8')
        data = {}
        for news in important_news[:3]:
            links = news.get('href')
            soup2 = await fetch_page(links)
            try:
                title = soup2.find('h2').text
                article = soup2.find('div', class_='css-6v6tq5').get_text().strip()
                clear_article = article.replace('\n', '')
                short_article = keeper(clear_article)
                link_data = {
                    'title': title,
                    'short_text': short_article
                }
                data[links] = link_data
            except Exception as e:
                continue
        news_data['south_china'] = data
    except Exception as e:
        pass

    return 'South China Done!'


async def hindu(url):
    soup = await fetch_page(url)
    important_news = soup.find_all('div', class_='col-xl-6')
    data = {}
    for news in important_news[2:5]:
        urls = [link.get('href') for link in news.find_all('a')]
        for link in urls:
            if link is not None:
                try:
                    soup2 = await fetch_page(link)
                    title = soup2.find('h1').text
                    article = soup2.find('div', class_='articlebodycontent').get_text().strip()
                    clear_article = article.replace('\n', '')
                    short_article = keeper(clear_article)
                    link_data = {
                        'title': title,
                        'short_text': short_article
                    }
                    data[link] = link_data
                except Exception as e:
                    continue
            else:
                continue
    news_data['hindu'] = data

    return 'Hindu Done!'


async def new_yorker(url):
    try:
        soup = await fetch_page(url)
        important_news = 'https://www.newyorker.com' + soup.find('a', class_='SummaryItemHedLink-civMjp').get('href')
        data = {}
        soup2 = await fetch_page(important_news)
        title = soup2.find('h1').text
        article = soup2.find('div', class_='body__inner-container').get_text().strip()
        clear_article = article.replace('\n', '')
        short_article = keeper(clear_article)
        link_data = {
            'title': title,
            'short_text': short_article
        }
        data[important_news] = link_data

        news_data['new_yorker'] = data
    except Exception as e:
        pass

    return 'New Yorker Done!'


async def economist(url):
    soup = await fetch_page(url)
    important_news = soup.find_all('div', class_='css-17glo8i')
    data = {}
    for news in important_news[:3]:
        urls = 'https://www.economist.com' + news.find('a').get('href')
        soup2 = await fetch_page(urls)
        title = soup2.find('h1').text
        article = soup2.find('div', class_='css-1a2ik1p').get_text().strip()
        clear_article = article.replace('\n', '')
        short_article = keeper(clear_article)
        link_data = {
            'title': title,
            'short_text': short_article
        }
        data[urls] = link_data
    news_data['economist'] = data

    return 'Economist Done!'


async def ukrnet(url):
    soup = await fetch_page(url)
    important_news = soup.find_all("section", class_="im")
    data = {}
    for news in important_news[:3]:
        links = news.find('a').get('href')
        soup2 = await fetch_page(links)
        try:
            important_news2 = soup2.find("section", class_="im").find('a').get('href')
            soup3 = await fetch_page(important_news2)
            title = soup3.find('h1').text
            article = soup3.get_text()
            clear_article = article.replace('\n', '')
            short_article = keeper(clear_article)
            link_data = {
                'title': title,
                'short_text': short_article
            }
            data[important_news2] = link_data
        except Exception as e:
            continue
    news_data['ukrnet'] = data

    return 'UkrNet Done!'


async def main():
    await asyncio.gather(
        esspreso('https://espreso.tv/'),
        guardian('https://www.theguardian.com/europe'),
        ekathimerini('https://www.ekathimerini.com/'),
        south_china('https://www.scmp.com/'),
        hindu('https://www.thehindu.com/'),
        new_yorker('https://www.newyorker.com/news'),
        economist('https://www.economist.com/'),
        ukrnet('https://www.ukr.net/news/main.html')
    )

    return news_data
