def set_favicon_from_url(url: str) -> str:
    
    url_parts = url.split('/')
    if len(url_parts) >= 3:
        domain = url_parts[2]
        favicon_url = f"https://{domain}/favicon.ico"
        return favicon_url

    return None