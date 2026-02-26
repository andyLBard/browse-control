import asyncio
from scrapling import Fetcher, AsyncFetcher, StealthyFetcher, Selector
from scrapling.spiders import Spider, Response

class SourceSpider(Spider):
    
    def __init__(self, starting_url, link_selector="a"):
        self.starting_url = starting_url
        self.name = "sourceSpider"
        self.link_selector = link_selector
    
    async def parse(self, response: Response):
        for link in response.css("{}::attr(href)").get():
            yield response.follow(link, callback=self.parse)

async def get_page(url, needs_js=False):
    if needs_js:
        page = await StealthyFetcher.async_fetch(url=url, impersonate="chrome", real_chrome=False, disable_resources=True, network_idle=True)
    else:
        page = Fetcher.get(url, impersonate="chrome")
    return page

async def get_links(url, page=None, needs_js=False):
    if page is None:
        page = await get_page(url=url, needs_js=needs_js)
    links = [a for a in page.css("a::attr(href)").getall()]
    return links

async def get_images(url, page=None, needs_js=False):
    if page is None:
        page = await get_page(url=url, needs_js=needs_js)
    imgs = [img for img in page.css("img::attr(src)").getall()]
    return imgs

async def get_html_contents(url, content_selector="html", needs_js=False, page=None):
    if page is None:
        page = await get_page(url=url, needs_js=needs_js)
    html_content = page.css(content_selector).getall()
    return html_content

async def get_binary_file_contents(url):
    ret = { "filetype":"text/plain", "contents":None }
    page = await get_page(url)
    ret["contents"] = page.body
    ret["filetype"] = page.headers["content-type"]
    return ret


##Testing
#async def main():
#    l = await get_binary_file_contents(url="https://cdn.hswstatic.com/gif/water-update.jpg")
#    print(l["filetype"])

#asyncio.run(main())
