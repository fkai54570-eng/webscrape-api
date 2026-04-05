"""核心抓取服务"""
import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse
import os

from config import settings
from utils import normalize_url


SSL_VERIFY = os.getenv("SSL_VERIFY", "true").lower() != "false"


async def scrape_url(url: str, selector: Optional[str] = None, output_format: str = "json", timeout: int = 30) -> Dict[str, Any]:
    url = normalize_url(url)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, verify=SSL_VERIFY, headers={"User-Agent": settings.user_agent}) as client:
        response = await client.get(url)
        response.raise_for_status()
        html_content = response.text
        status_code = response.status_code
    soup = BeautifulSoup(html_content, "lxml")
    result = {"status_code": status_code, "url": str(response.url)}
    if selector:
        elements = soup.select(selector)
        result["data"] = parse_elements(elements, output_format)
    else:
        result["data"] = parse_full_page(soup)
        result["text"] = soup.get_text(separator="\n", strip=True)
    return result


def parse_elements(elements: List, output_format: str) -> Dict[str, Any]:
    if output_format == "text":
        return {"count": len(elements), "items": [el.get_text(strip=True) for el in elements]}
    items = []
    for i, el in enumerate(elements):
        item = {"index": i, "text": el.get_text(strip=True), "tag": el.name}
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
    data = {"title": soup.title.string if soup.title else None, "meta": {}, "links": [], "images": [], "headings": {}}
    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property", "")
        content = meta.get("content", "")
        if name and content:
            data["meta"][name] = content
    for link in soup.find_all("a", href=True)[:50]:
        data["links"].append({"text": link.get_text(strip=True), "href": link["href"]})
    for img in soup.find_all("img", src=True)[:30]:
        data["images"].append({"src": img["src"], "alt": img.get("alt", "")})
    for level in range(1, 7):
        headings = soup.find_all(f"h{level}")
        if headings:
            data["headings"][f"h{level}"] = [h.get_text(strip=True) for h in headings]
    return data


async def extract_content(url: str, extract_type: str, custom_schema: Optional[Dict[str, str]] = None, timeout: int = 30) -> Dict[str, Any]:
    url = normalize_url(url)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, verify=SSL_VERIFY, headers={"User-Agent": settings.user_agent}) as client:
        response = await client.get(url)
        response.raise_for_status()
        html_content = response.text
    soup = BeautifulSoup(html_content, "lxml")
    result = {"status_code": response.status_code, "url": str(response.url)}
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
    return result


def extract_article(soup: BeautifulSoup) -> Dict[str, Any]:
    article = {"title": None, "content": None, "author": None, "date": None, "summary": None}
    title = soup.find("h1") or soup.find("title")
    if title:
        article["title"] = title.get_text(strip=True)
    for selector in ["article", ".post-content", ".article-content", ".entry-content", ".content", "main"]:
        content_el = soup.select_one(selector)
        if content_el:
            for tag in content_el.find_all(["script", "style", "nav", "aside"]):
                tag.decompose()
            article["content"] = content_el.get_text(separator="\n", strip=True)
            break
    for selector in [".author", ".byline", ".post-author", ".article-author", "[rel='author']", ".fn", ".author-name", ".writer"]:
        author_el = soup.select_one(selector)
        if author_el:
            article["author"] = author_el.get_text(strip=True)
            break
    for selector in [".publish-date", ".post-date", ".article-date", "time", ".date", ".entry-date", "[datetime]"]:
        date_el = soup.select_one(selector)
        if date_el:
            article["date"] = date_el.get("datetime") or date_el.get("content") or date_el.get_text(strip=True)
            if article["date"]:
                break
    if article["content"]:
        text = article["content"]
        article["summary"] = text[:500] + ("..." if len(text) > 500 else "")
    return article


def extract_product(soup: BeautifulSoup) -> Dict[str, Any]:
    """提取商品信息"""
    product = {"name": None, "price": None, "description": None, "images": [], "rating": None, "reviews": None}
    title = soup.find("h1") or soup.find("title")
    if title:
        product["name"] = title.get_text(strip=True)
    for selector in [".price", ".product-price", "[data-price]", ".current-price", "#price"]:
        price_el = soup.select_one(selector)
        if price_el:
            product["price"] = price_el.get_text(strip=True)
            break
    for selector in [".description", ".product-description", "#description", ".product-details"]:
        desc_el = soup.select_one(selector)
        if desc_el:
            product["description"] = desc_el.get_text(separator="\n", strip=True)[:1000]
            break
    for selector in [".rating", ".product-rating", "[data-rating]", ".stars"]:
        rating_el = soup.select_one(selector)
        if rating_el:
            rating_text = rating_el.get_text(strip=True) or rating_el.get("data-rating", "")
            if rating_text:
                product["rating"] = rating_text
            break
    for selector in [".reviews", ".product-reviews", "#reviews-count", ".review-count"]:
        reviews_el = soup.select_one(selector)
        if reviews_el:
            product["reviews"] = reviews_el.get_text(strip=True)
            break
    for img in soup.find_all("img", src=True)[:20]:
        src = img.get("src", "")
        if src and ("product" in src.lower() or "item" in src.lower() or img.get("class") and any("product" in str(c).lower() for c in img.get("class", []))):
            product["images"].append({"src": src, "alt": img.get("alt", "")})
    return product


def extract_all_links(soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
    """提取页面所有链接"""
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(base_url, href)
        links.append({
            "text": a.get_text(strip=True),
            "href": full_url,
            "internal": urlparse(full_url).netloc == urlparse(base_url).netloc,
        })
    return {"total": len(links), "internal": len([l for l in links if l["internal"]]), "external": len([l for l in links if not l["internal"]]), "links": links}


def extract_all_images(soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
    """提取页面所有图片"""
    images = []
    for img in soup.find_all("img", src=True):
        src = img["src"]
        full_url = urljoin(base_url, src)
        images.append({
            "src": full_url,
            "alt": img.get("alt", ""),
            "width": img.get("width"),
            "height": img.get("height"),
        })
    return {"total": len(images), "images": images}


def extract_by_schema(soup: BeautifulSoup, schema: Dict[str, str]) -> Dict[str, Any]:
    """根据自定义schema提取数据"""
    result = {}
    for field_name, selector in schema.items():
        elements = soup.select(selector)
        if elements:
            if len(elements) == 1:
                result[field_name] = elements[0].get_text(strip=True)
            else:
                result[field_name] = [el.get_text(strip=True) for el in elements]
        else:
            result[field_name] = None
    return result
