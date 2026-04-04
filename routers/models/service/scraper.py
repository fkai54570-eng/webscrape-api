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
    
    return result


def extract_article(soup: BeautifulSoup) -> Dict[str, Any]:
    """提取文章内容"""
    article = {
        "title": None,
        "content": None,
        "author": None,
        "date": None,
        "summary": None,
    }
    
    title = soup.find("h1") or soup.find("title")
    if title:
        article["title"] = title.get_text(strip=True)
    
    content_selectors = ["article", ".post-content", ".article-content", ".entry-content", ".content", "main"]
    for selector in content_selectors:
        content_el = soup.select_one(selector)
        if content_el:
            for tag in content_el.find_all(["script", "style", "nav", "aside"]):
                tag.decompose()
            article["content"] = content_el.get_text(separator="\n", strip=True)
            break
    
    author_selectors = [".author", ".byline", "[rel=author]"]
    for selector in author_selectors:
        author_el = soup.select_one(selector)
        if author_el:
            article["author"] = author_el.get_text(strip=True)
            break
    
    date_el = soup.find("time") or soup.select_one(".date, .post-date")
    if date_el:
        article["date"] = date_el.get("datetime") or date_el.get_text(strip=True)
    
    desc = soup.find("meta", attrs={"name": "description"})
    if desc:
        article["summary"] = desc.get("content", "")
    
    return article


def extract_product(soup: BeautifulSoup) -> Dict[str, Any]:
    """提取产品信息"""
    product = {
        "name": None,
        "price": None,
        "description": None,
        "images": [],
        "availability": None,
    }
    
    name_selectors = ["h1", ".product-title", ".product-name", "[itemprop=name]"]
    for selector in name_selectors:
        name_el = soup.select_one(selector)
        if name_el:
            product["name"] = name_el.get_text(strip=True)
            break
    
    price_selectors = [".price", ".product-price", "[itemprop=price]", "[data-price]"]
    for selector in price_selectors:
        price_el = soup.select_one(selector)
        if price_el:
            product["price"] = price_el.get_text(strip=True)
            break
    
    desc_selectors = [".product-description", ".description", "[itemprop=description]"]
    for selector in desc_selectors:
        desc_el = soup.select_one(selector)
        if desc_el:
            product["description"] = desc_el.get_text(strip=True)
            break
    
    for img in soup.select(".product-image img, .product-images img")[:5]:
        if img.get("src"):
            product["images"].append(img["src"])
    
    return product


def extract_all_links(soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
    """提取所有链接"""
    links = {"internal": [], "external": []}
    base_domain = urlparse(base_url).netloc
    
    for link in soup.find_all("a", href=True):
        href = link["href"]
        full_url = urljoin(base_url, href)
        domain = urlparse(full_url).netloc
        
        link_info = {
            "text": link.get_text(strip=True),
            "url": full_url,
        }
        
        if domain == base_domain:
            links["internal"].append(link_info)
        else:
            links["external"].append(link_info)
    
    return {
        "total": len(links["intern
