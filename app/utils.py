from cgi import escape
from datetime import timedelta
import markdown
import settings

from flask import Response, request
from functools import wraps
from libs.BeautifulSoup import BeautifulSoup
from models import Article, Comment, User
from pygments import lexers, formatters, highlight
from werkzeug.security import check_password_hash

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    # return False
    #  method 1 #
    userlist = User.all().order('-number')    
    for x in range(0, userlist.count()):
        if username == userlist[x].title and check_password_hash(userlist[x].content, password):
            return True

    # if username == settings.USER and password == settings.PASSWORD:
    #     return True
        
    return False
    #  method 2 #
    # for x in userlist
    #     if username == x.title and check_password_hash(x.content, password):
    #         flag = 1

    # if flag == 1
    #     return True
    # return False


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def pygments_markdown(content):
    _lexer_names = reduce(lambda a,b: a + b[2], lexers.LEXERS.itervalues(), ())
    _formatter = formatters.HtmlFormatter(cssclass='highlight')

    html = markdown.markdown(content)
    # Using html.parser to prevent bs4 adding <html> tag
    soup = BeautifulSoup(html)
    for tag in ("script", "html", "head", "title", "div", "hr", "article", "header", "footer"):
        if soup.findAll(tag):
            return escape(content)
    for pre in soup.findAll('pre'):
        if pre.code:
            txt = unicode(pre.code.text)
            lexer_name = "text"
            if txt.startswith(':::'):
                lexer_name, txt = txt.split('\n', 1)
                lexer_name = lexer_name.split(':::')[1]

            if lexer_name not in _lexer_names:
                lexer_name = "text"
            lexer = lexers.get_lexer_by_name(lexer_name, stripnl=True, encoding='UTF-8')
            if txt.find("&lt;") != -1 or txt.find("&gt;") != -1:
                txt = txt.replace("&lt;", "<").replace("&gt;", ">")
            if txt.find("&amp;") != -1:
                txt = txt.replace("&amp;", "&")
            highlighted = highlight(txt, lexer, _formatter)
            div_code = BeautifulSoup(highlighted).div
            if not div_code:
                return content
            pre.replaceWith(div_code)
    return unicode(soup)


def get_aritle_by_number(number):
    articles = Article.all()
    articles = articles.filter('number ==', int(number))
    if articles.count() == 0:
        return None
    return articles[0]


def get_comments(number):
    comments = Comment.all()
    comments = comments.filter('article_number ==', int(number))
    return comments


def get_comment_count(number):
    n = len([x for x in get_comments(number)])
    return "" if n == 0 else "(%d)" % n


def link_tags(tags):
    result = ""
    for tag in tags.split(" "):
        result += '<a href="/tag/%s/">%s</a> ' % (tag, tag)
    return result


def format_date(date):
    # convert to Beijing timezone
    date = date + timedelta(hours=8)
    return date.strftime("%Y-%m-%d %H:%M UTC+8")
