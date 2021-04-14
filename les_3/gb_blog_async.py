import json
import asyncio

import bs4
import aiohttp
from urllib.parse import urljoin


class GbBlogParseAsync:
    def __init__(self, start_url):
        self.start_url = start_url
        self.done_urls = set()

    def get_task(self, url, callback):
        async def task():
            soup = await self._get_soup(url)
            return await callback(url, soup)

        return task

    async def _get_response(self, url):
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    print(1)
                    await asyncio.sleep(1)

    async def _get_soup(self, url):
        response = await self._get_response(url)
        soup = bs4.BeautifulSoup(response, "lxml")
        return soup

    async def parse_post(self, url, soup):
        author_tag = soup.find("div", attrs={"itemprop": "author"})
        try:
            data = {
                "post_data": {
                    "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                    "url": url,
                    "id": soup.find("comments").attrs.get("commentable-id"),
                },
                "author_data": {
                    "url": urljoin(url, author_tag.parent.attrs.get("href")),
                    "name": author_tag.text,
                },
                "tags_data": [
                    {"name": tag.text, "url": urljoin(url, tag.attrs.get("href"))}
                    for tag in soup.find_all("a", attrs={"class": "small"})
                ],
                "comments_data": await self._get_comments(
                    soup.find("comments").attrs.get("commentable-id")
                ),
            }
        except Exception as exc:
            print(exc)
            print(1)
        print(url)
        return data

    async def _get_comments(self, post_id):
        api_path = f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc"
        response = await self._get_response(urljoin(self.start_url, api_path))
        data = json.loads(response)
        return data

    async def parse_feed(self, url, soup):
        tasks = []
        ul = soup.find("ul", attrs={"class": "gb__pagination"})
        pag_urls = set(
            urljoin(url, href.attrs.get("href"))
            for href in ul.find_all("a")
            if href.attrs.get("href")
        )
        for pag_url in pag_urls:
            if pag_url not in self.done_urls:
                task = asyncio.ensure_future(self.get_task(pag_url, self.parse_feed)())
                self.done_urls.add(pag_url)
                tasks.append(task)

        post_items = soup.find("div", attrs={"class": "post-items-wrapper"})
        posts_urls = set(
            urljoin(url, href.attrs.get("href"))
            for href in post_items.find_all("a", attrs={"class": "post-item__title"})
            if href.attrs.get("href")
        )

        for post_url in posts_urls:
            if post_url not in self.done_urls:
                task = asyncio.ensure_future(self.get_task(post_url, self.parse_post)())
                self.done_urls.add(post_url)
                tasks.append(task)
        await asyncio.wait(tasks)

    async def run(self):
        task = asyncio.create_task(self.get_task(self.start_url, self.parse_feed)())
        self.done_urls.add(self.start_url)
        await task
        # for task in self.tasks:
        #     task_result = await task()
        #     if task_result:
        #         print(1)


if __name__ == "__main__":
    parser = GbBlogParseAsync("https://geekbrains.ru/posts")
    asyncio.run(parser.run())