import re

def is_valid_domain(url):
    pattern = r'^(http|https):\/\/[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\/?$'
    return re.fullmatch(pattern, url) is not None

def get_valid(url):
    if not is_valid_domain(url):
        raise ValueError("Некорректный домен URL")
    return url

def main():
    test = [
        "http://example.com/",
        "https://google.com",
        "http://test-site123.org/",
        "example.com",
        "кремль.рф",
        "ftp://example.com",
        "http://example"
    ]
    for url in test:
        print(f"Проверка: {url}")
        if is_valid_domain(url):
            print("its okay")
        else:
            print("not ok")

if __name__ == "__main__":
    main()