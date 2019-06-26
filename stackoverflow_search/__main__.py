import requests
import urllib.parse as p
import bs4

CLEAR = "\033[0m"
QUESTION = "\033[95m"
CODE = "\033[42m\033[30m"
LINK = "\033[94m"
BOLD = "\033[1m"
CYAN = "\033[46m\033[30m"


def code_to_string(soup):
    l = []
    for tag in soup:
        s = [c for c in str(tag.string)]
        if len(s) > 1:
            for i, c in enumerate(s[:-1]):
                if s[i + 1] == c and c == "\n":
                    s.pop(i)
        string = "".join(s)
        l.append(string)

    s = "".join(l)
    if "\n" in s:
        # multiline comment
        s = s.rstrip()
        v = s.split("\n")
        l = []
        for x in v:
            l.append(CODE + x.rstrip() + CLEAR)
        s = "\n".join(l)
    else:
        s = CODE + s + CLEAR
    s.replace("\n", "    \n")
    return s


def parse_p(tag):
    l = []
    contents = tag.contents
    for x in contents:
        if type(x) == str:
            l.append(x)
        else:
            if x.name == "a":
                l.append(x.text + LINK + "[%s]" % x["href"] + CLEAR)
            elif x.name == "b":
                l.append(BOLD + x.text + CLEAR)
            elif x.name == "code":
                l.append(CODE + x.text + CLEAR)
            elif x.name == "strike":
                pass
            else:
                l.append(str(x.string))

    return "".join(l)


def parse_so_text(block):
    l = []
    for tag in block:
        if tag.name == "p":
            # normal text
            l.append(parse_p(tag))
        elif tag.name == "pre":
            # code
            l.append(code_to_string(tag.find("code")))
    return "\n".join(l)


def main(search_string):

    query_string = p.quote_plus(search_string)
    search_r = requests.get("https://stackoverflow.com/search?q=%s" % query_string)
    search_soup = bs4.BeautifulSoup(search_r.text, "html.parser")
    surrounding_div = search_soup.find_all("div", "question-summary search-result")[0]
    votes = search_soup.find("span", "vote-count-post ").find("strong").text
    try:
        answers = (
            search_soup.find("div", "status answered-accepted").find("strong").text
        )
    except AttributeError:
        answers = None
    tag = search_soup.find_all("a", "question-hyperlink")[0]
    print(QUESTION + "QUESTION: " + CLEAR + tag["title"])

    question_url = p.urljoin(
        "https://stackoverflow.com/search?q=%s" % query_string, tag["href"]
    )
    print(LINK + "(%s)" % question_url + CLEAR)
    answer_r = requests.get(question_url)
    answer_soup = bs4.BeautifulSoup(answer_r.text, "html.parser")
    if not answers:
        answers = answer_soup.find("div", "subheader answers-subheader").find("h2")[
            "data-answercount"
        ]

    print("(%s Answers, %s Votes)\n" % (answers, votes))

    question_block = answer_soup.find("div", "question").find("div", "post-text")
    question_text = parse_so_text(question_block)

    answer_block = answer_soup.find_all("div", "answer accepted-answer")[0]
    answer_votes = answer_block.find("div", {"itemprop": "upvoteCount"})["data-value"]
    answer_text = parse_so_text(answer_block.find("div", "post-text"))

    print()
    print(question_text)
    print()
    print(CYAN + "ANSWER: %s UPVOTES" % answer_votes + CLEAR)
    print()
    print(answer_text)


if __name__ == "__main__":
    import sys

    string = sys.argv[1]
    main(string)

