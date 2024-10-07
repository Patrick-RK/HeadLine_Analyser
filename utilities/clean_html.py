from bs4 import BeautifulSoup, Comment

def strip_html(html_content, to_remove_ids=None, to_remove_classes=None, tags_to_extract=None):
    # Default to empty lists if None are provided
    to_remove_ids = to_remove_ids or []
    to_remove_classes = to_remove_classes or []
    tags_to_extract = tags_to_extract or ['h3', 'h5']  # Default to 'h3' and 'h5'

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted tags (script, style) and comments
    for element in soup(['script', 'style']):
        element.decompose()  # Use decompose to completely remove the element
    
    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # Remove elements by IDs
    for element_id in to_remove_ids:
        elem = soup.find(id=element_id)
        if elem:
            elem.decompose()  # Use decompose for complete removal
    
    # Remove elements by classes
    for class_name in to_remove_classes:
        for elem in soup.find_all(class_=class_name):
            elem.decompose()

    # Extract only the specified tags (e.g., 'h3' and 'h5')
    extracted_elements = soup.find_all(tags_to_extract)
    
    # Extract text (titles) from the tags
    titles = []
    for tag in extracted_elements:
        # If there's a <span> inside the <h3> or <h5>, get the text from the <span>
        if tag.find('span'):
            titles.append(tag.find('span').get_text(strip=True))
        else:
            titles.append(tag.get_text(strip=True))

    return titles  # Return the list of titles
