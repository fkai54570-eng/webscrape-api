"""核心抓取服务"""
import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse
import os

from config import settings
from utils import normalize_url


SSL_VERIFY = os.getenv("SSL_VERIFY", "true").lower() != "false"


async def scrape_url(
    url: str,
    selector: Optional[str] = None,
    output_format: str = "json",
    timeout: int = 30,
) -> Dict[str, Any]:
    """抓取URL并提取内容"""
    url = normalize_url(url)
    
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        verify=SSL_VERIFY,
        headers={
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        html_content = response.text
        status_code = response.status_code
    
    soup = BeautifulSoup(html_content, "lxml")
    
    result = {
        "status_code": status_code,
        "url": str(response.url),
    }
    
    if selector:
        elements = soup.select(selector)
        result["data"] = parse_elements(elements, output_format)
    else:
        result["data"] = parse_full_page(soup)
        result["text"] = soup.get_text(separator="\n", strip=True)
    
    return result


def parse_elements(elements: List, output_format: str) -> Dict[str, Any]:
    """解析选中的元素"""
    if output_format == "text":
        return {
            "count": len(elements),
            "items": [el.get_text(strip=True) for el in elements],
        }
    
    items = []
    for i, el in enumerate(elements):
        item = {
            "index": i,
            "text": el.get_text(strip=True),
            "tag": el.name,
        }
        
        if el.attrs:
            item["attributes"] = dict(el.attrs)
        
        if el.name == "a" and el.get("href"):
            item["href"] = el["href"]
        
        if el.name == "img" and el.get("src"):
            item["src"] = el["src"]
            item["alt"] = el.get("alt", "")
        
        items.append(item)
    
    return {"count": len(items), "items": items}


def parse_full_page(soup: BeautifulSoup) -> Dict[str, Any]:
    """解析完整页面"""
    data = {
        "title": soup.title.string if soup.title else None,
        "meta": {},
        "links": [],
        "images": [],
        "headings": {},
    }
    
    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property", "")
        content = meta.get("content", "")
        if name and content:
            data["meta"][name] = content
    
    for link in soup.find_all("a", href=True)[:50]:
        data["links"].append({
            "text": link.get_text(strip=True),
            "href": link["href"],
        })
    
    for img in soup.find_all("img", src=True)[:30]:
        data["images"].append({
            "src": img["src"],
            "alt": img.get("alt", ""),
        })
    
    for level in range(1, 7):
        headings = soup.find_all(f"h{level}")
        if headings:
            data["headings"][f"h{level}"] = [h.get_text(strip=True) for h in headings]
    
    return data


async def extract_content(
    url: str,
    extract_type: str,
    custom_schema: Optional[Dict[str, str]] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """智能内容提取"""
    url = normalize_url(url)
    
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        verify=SSL_VERIFY,
        headers={"User-Agent": settings.user_agent},
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        html_content = response.text
    
    soup = BeautifulSoup(html_content, "lxml")
    
    result = {
        "status_code": response.status_code,
        "url": str(response.url),
    }
    
    if extract_type == "article":
        result["data"] = extract_article(soup)
    elif extract_type == "product":
        result["data"] = extract_product(soup)
    elif extract_type == "links":
        result["data"] = extract_all_links(soup, str(response.url))
    elif extract_type == "images":
        result["data"] = extract_all_images(soup, str(response.url))
    elif extract_type == "custom" and custom_schema:
        result["data"] = extract_by_schema(soup, custom_schema)
    else:
        result["data"] = parse_full_page(soup)
