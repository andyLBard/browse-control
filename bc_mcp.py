import asyncio
import base64
import io
from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
import urllib.parse as urlparse
import yaml

import web_source

ALLOWED_SOURCES = []
LOADING_WAIT_TIME = 5000
MAX_SPIDERING_DEPTH = 1
DEFAULT_AL_TERM = ":"

#Open the yaml file to pull the allowlist, read it into the global variable
#and close the file, just pass and keep the sources empty if the yaml is unreadable
with open("allowlist.yml") as f:
    try:
        tmp_sources = yaml.safe_load(f)
	#improve the protection of the allowlist.
        for source in tmp_sources:
            if source.strip()[-1] not in ["/", ":"]:
                source = source.strip() + DEFAULT_AL_TERM
        ALLOWED_SOURCES = [ s for s in tmp_sources ]
    except:
        pass

mcp = FastMCP("browser-control")

def is_url_allowed(url):
    allowed = False
    #check if url is allowed, and stop asap if it is.
    for s in ALLOWED_SOURCES:
       if url.startswith(s):
           allowed = True
           break
    return allowed

def make_response(code=0, msg="Success", results=None):
    ret = {}
    ret["code"] = code
    ret["msg"] = msg
    ret["results"] = {} if results is None else results
    return ret

#NOTHING ABOVE THIS LINE CALLS REQUESTS!
#THIS SHOULD BE ONE OF ONLY Three METHODS ACTUALLY CALLING REQUESTS!!
async def make_allowed_get(url, needs_js=False):
    allowed = is_url_allowed(url)
    if not allowed: #return with an error that's a bit big but nice to the caller
        return make_response(code=-1, msg="Allowlist violation")
    else:
        page = await web_source.get_page(url, needs_js)
        return make_response(results=page)

@mcp.tool()
async def get_image_contents(url):
    if is_url_allowed(url):
        img_data = await web_source.get_binary_file_contents(url)
        content64 = base64.b64encode(img_data["contents"]).decode('utf-8')
        return ImageContent(type="image", data=content64, mimeType=img_data["filetype"])
    else:
        return make_response(code=-1, msg="Allowlist violation")

@mcp.tool()
async def get_links(url, needs_js=False):
    links = await web_source.get_links(url=url, needs_js=needs_js)
    return make_response(results=links)

@mcp.tool()
async def get_images_from_url(url, img_selector="img"):
    images = await web_source.get_html_contents(url=url, content_selector="{}::attr(src)".format(img_selector))
    return make_response(results=images)

#@mcp.tool()
#async def get_limited_spider_contents(url, link_class=None):
#    depth = 0
#    all_links = set()
#    visited_links = set()
#    visited_links.add(url)
#    links = await get_links(url, link_class)
#    for link in links:
#        all_links.add(link)

#    while depth < MAX_SPIDERING_DEPTH:
#       for link in all_links.copy():
#          if link not in visited_links:
#              try:
#                  sub_step = await get_links(link, link_class)
#                  for ssstep in sub_step:
#                      all_links.add(ssstep)
#              except:
#                  print("{} did not work".format(link))
#              visited_links.add(link)
#       depth = depth + 1
#    return all_links

#I went the janktastic route of execing this whole file from the other servers instead of extending objects
#I should not have done that, however, if you want to run the base server without wikipedia, uncomment these two lines:
if __name__ == "__main__":
    mcp.run(transport="streamable-http")

#async def main():
#    c = await get_limited_spider_contents("http://localhost:8888/")
#    print(c)

#asyncio.run(main())
