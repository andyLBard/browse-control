#import asyncio
#from bs4 import BeautifulSoup as BS4
#from mcp.server.fastmcp import FastMCP
#from urllib.parse import urljoin
#import bc_mcp

#mcp = FastMCP("browser-control") #changed for convenience when configuring a local server with multiple sites.

#Yeah, yeah, I know.
with open("bc_mcp.py") as base_server:
    exec(base_server.read())

    WIKI_BASE = "https://en.wikipedia.org"

    @mcp.tool()
    async def search_wikipedia(search_query):
        page = await browse_site(url = urlparse.urljoin(WIKI_BASE,"/w/index.php?search=intitle%3A{}&ns0=1").format(search_query))
        doc = BS4(page["text"], "html.parser")
        links =  [ a["href"] for a in doc.find("div", class_="mw-search-results-container").find_all("a") ]
        return list(set([urlparse.urljoin(WIKI_BASE,link.strip()) for link in links]))

    @mcp.tool()
    async def get_wikipedia_article_from_url(article_url):
        page = await browse_site(url = article_url)
        doc = BS4(page["text"], "html.parser")
        return "\n".join([p.text for p in doc.find("div", class_="mw-content-ltr").find_all("p")])
    
#    async def main():
#        c = await search_wikipedia("war")
#        print(c)

#    asyncio.run(main())

    mcp.run(transport="streamable-http")
