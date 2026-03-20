from bs4 import BeautifulSoup, Comment


def strip_html(html_content, selector="h3, h5", exclude_classes=None):
    """
    Extract headline text from HTML using a CSS selector.

    Args:
        html_content: Raw HTML string.
        selector: CSS selector for headline elements (e.g. "h3, h5" or "div.title-redesign").
        exclude_classes: List of CSS class names to skip.

    Returns:
        List of headline strings.
    """
    exclude_classes = exclude_classes or []

    soup = BeautifulSoup(html_content, 'html.parser')

    for element in soup(['script', 'style']):
        element.decompose()

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    extracted_elements = soup.select(selector)

    titles = []
    for tag in extracted_elements:
        # Skip excluded classes
        tag_classes = tag.get('class', [])
        if any(cls in tag_classes for cls in exclude_classes):
            continue

        # If there's a <span> inside, prefer the span text
        if tag.find('span'):
            text = tag.find('span').get_text(strip=True)
        else:
            text = tag.get_text(strip=True)

        # Skip junk headlines that are too short to be meaningful
        if len(text.split()) < 4:
            continue

        titles.append(text)

    return titles
