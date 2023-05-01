import re
import requests


def get_city_review(city):
    search_url = f"https://www.google.com/search?q={city}+review"
    response = requests.get(search_url)
    html_content = response.text

    # first review
    review_regex = r'<div class="g"><span class="st">(.*?)</span></div>'
    review_match = re.search(review_regex, html_content, re.DOTALL)
    review_text = review_match.group(1).strip() if review_match else None

    # find rating
    rating_regex = r'<div class="BNeawe s3v9rd AP7Wnd">(.*?)</div>'
    rating_match = re.search(rating_regex, html_content)
    rating_text = rating_match.group(1).strip() if rating_match else None

    # find website
    website_regex = r'<div class="g"><cite>(.*?)</cite></div>'
    website_match = re.search(website_regex, html_content, re.DOTALL)
    website_text = website_match.group(1).strip() if website_match else None

    # return the review, rating, and website as a dictionary
    return {
        "review": review_text,
        "rating": rating_text,
        "website": website_text
    }

# example input: Miami
# {
#     "review": "Miami is a vibrant and exciting city with beautiful beaches and a diverse culture. There's always something to do and see in Miami, from the art galleries and museums to the lively nightlife scene.",
#     "rating": "4.2",
#     "website": "www.tripadvisor.com"
# }
