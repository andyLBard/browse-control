import asyncio
import base64
from bs4 import BeautifulSoup as BS4
import io
from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
from playwright.async_api import async_playwright
import requests, requests_cache
import urllib.parse as urlparse
import yaml

ALLOWED_SOURCES = []
LOADING_WAIT_TIME = 5000
MAX_SPIDERING_DEPTH = 1

#Open the yaml file to pull the allowlist, read it into the global variable
#and close the file, just pass and keep the sources empty if the yaml is unreadable
with open("allowlist.yml") as f:
    try:
        tmp_sources = yaml.safe_load(f)
        ALLOWED_SOURCES = [s.strip() for s in tmp_sources]
    except:
        pass

mcp = FastMCP("browser-control")

#setup requests caching
session = requests_cache.CachedSession("bcmcp_cache", expire_after=3600) #cached for one hour

def is_url_allowed(url):
    allowed = False
    #check if url is allowed, and stop asap if it is.
    for s in ALLOWED_SOURCES:
       if url.startswith(s):
           allowed = True
           break
    return allowed

#NOTHING ABOVE THIS LINE CALLS REQUESTS!
#THIS SHOULD BE ONE OF ONLY TWO METHODS ACTUALLY CALLING REQUESTS!!
async def make_allowed_get(**kwargs):
    req = {}
    req["url"] = kwargs.get("url", "NULL")
    req["headers"] = kwargs.get("headers", [])
    allowed = is_url_allowed(req["url"])
    if not allowed: #return with an error that's a bit big but nice to the caller
        return {"code": -1, "msg": "Violates whitelist", "results": {} }
    else:
        r = ""
        async with async_playwright() as pw:
            browser = await pw.webkit.launch()
            page = await browser.new_page()
            await page.goto(req["url"])
            await page.wait_for_timeout(LOADING_WAIT_TIME)
            r = await page.evaluate("() => document.documentElement.outerHTML")
        #r = session.get(req["url"], headers=req["headers"])
        return {"code": 0, "msg": "Success", "results": r }


#THIS SHOULD BE ONE OF ONLY TWO METHODS ACTUALLY CALLING REQUESTS!!
def make_allowed_post(**kwargs):
    req = {}
    req["url"] = kwargs.get("url", "NULL")
    req["headers"] = kwargs.get("headers", [])
    req["body"] = kwargs.get("body", {})

    allowed = is_url_allowed()
    if not allowed: #return with an error that's a bit big but nice to the caller
        return {"code": -1, "msg": "Violates whitelist", "results": {} }
    else:
        r = session.post(req["url"], headers=req["headers"], data=req["body"])
        return r
##NOTHING BELOW THIS LINE CALLS REQUESTS!

async def browse_site(**kwargs):
    tmp_url = kwargs.get("url")
    initial_resp = await make_allowed_get(url=tmp_url, headers=kwargs.get("headers"))
    if initial_resp["code"] == -1:
        return initial_resp #url is blocked, just bubble the error up.
    resp = initial_resp["results"]
    results = {"links": [], "images":[], "text":""}
    body = BS4(resp, "html.parser")
    results["links"] = [urlparse.urljoin(tmp_url , a.get("href","")) for a in body.find_all("a", class_=kwargs.get("link_class", True))]
    results["images"] = [urlparse.urljoin(tmp_url, img.get("href","")) for img in body.find_all("img", class_=kwargs.get("img_class", True))]
    results["text"] = resp

    #check for selector
    sel = kwargs.get("selector", "NULL")
    if sel != "NULL":
        results["selection"] = [el.outerHTML for el in body.select(sel)]

    return results

@mcp.tool()
async def get_links(url, link_class=None, link_attr=None):
    browse = await browse_site(url=url, link_class=link_class)
    return browse["links"]

@mcp.tool()
async def get_images_from_url(url, img_class=None):
    browse = await browse_site(url=url, img_class=img_class)
    return browse["images"]

@mcp.tool()
def get_image_contents(url):
    if is_url_allowed(url):
        img_data = session.get(url)
        content64 = base64.b64encode(img_data.content).decode('utf-8')
        return ImageContent(type="image", data=content64, mimeType=img_data.headers["content-type"])
    else:
        return ""

@mcp.tool()
async def get_limited_spider_contents(url, link_class=None):
    depth = 0
    all_links = set()
    visited_links = set()
    visited_links.add(url)
    links = await get_links(url)
    links = links
    for link in links:
        all_links.add(link)

    while depth < MAX_SPIDERING_DEPTH:
       for link in all_links.copy():
          if link not in visited_links:
              try:
                  sub_step = await get_links(link)
                  for ssstep in sub_step:
                      all_links.add(ssstep)
              except:
                  print("{} did not work".format(link))
              visited_links.add(link)
       depth = depth + 1
    return all_links

#this one doesn't work yet, no idea why bs4.select is returning nothing no matter what selector i send it.
#@mcp.tool()
async def get_elements_by_selector(url, selector, headers=[]):
    req = {}
    req["url"] = url
    req["headers"] = headers
    req["selector"] = selector
    b = await browse_site(**req)
    print(b)
    return b["selection"]

mcp.run(transport="streamable-http")

#async def main():
#    c = await get_limited_spider_contents("http://localhost:8888/")
#    print(c)

#asyncio.run(main())
