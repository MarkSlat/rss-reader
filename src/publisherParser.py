from src.models.publisher import Publisher


def set_favicon_from_publisher(publisher: Publisher):
    
    url = publisher.rss_url
    
    url_parts = url.split('/')
    if len(url_parts) >= 3:
        domain = url_parts[2]
        favicon_url = f"https://{domain}/favicon.ico"
        publisher.favicon_url = favicon_url
    
    return publisher