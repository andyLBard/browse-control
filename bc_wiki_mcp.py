import asyncio
import base64
import io
from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
import urllib.parse as urlparse
import yaml

import web_source

mcp = FastMCP("wikipedia_access")
WIKI_BASE = "https://en.wikipedia.org"

@mcp.tool()
async def search_wikipedia(search_query):
    page = await web_source.get_page(url = urlparse.urljoin(WIKI_BASE,"/w/index.php?search=intitle%3A{}&ns0=1").format(search_query))
    links = await web_source.get_links(url="", page=page)
    return list(set([urlparse.urljoin(WIKI_BASE,link.strip()) for link in links]))

@mcp.tool()
async def get_wikipedia_article_from_url(article_url):
    page = await web_source.get_page(url = article_url)
    contents = [ p for p in page.css("div.mw-content-ltr p")]
    return contents
    
#async def main():
#    c = await get_images_from_url("https://en.wikipedia.org/wiki/Paul_Thomas_Anderson")
#    print(c)

#asyncio.run(main())
if __name__=="__main__":
    mcp.run(transport="streamable-http")
