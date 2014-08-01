"""
Flask Module Docs:  http://flask.pocoo.org/docs/api/#flask.Module

This file is used for both the routing and logic of your
application.
"""
import datetime

from flask import Module, url_for, render_template, request, redirect
from models import Article, Note, Comment, User
from forms import ArticleForm, NoteForm, SettingsForm, CommentForm, SignupForm
from utils import requires_auth, pygments_markdown, get_aritle_by_number, \
    get_comments, get_note_by_number
from werkzeug.security import generate_password_hash

views = Module(__name__, 'views')

@views.route('/')
def index():
    """Render website's index page."""
    return render_template('index.html')

@views.route('/taiwan/')
def taiwan():
    """Render website's taiwan page."""
    return render_template('taiwan.html')

@views.route('/console/')
@requires_auth
def console():
    """Render website's console page."""
    return render_template('console.html')

@views.route('/about/')
def about():
    return render_template('about.html')

@views.route('/about/T-Wind/')
def about_T():
    return render_template('about_T-Wind.html')

@views.route('/about/Vivian/')
def about_V():
    return render_template('about_Vivian.html')

@views.route('/about/Qing/')
def about_Q():
    return render_template('about_Qing.html')

@views.route('/xiakelite/')
def xiakelite():
    return render_template('xiakexing.html')

@views.route('/blog/')
def blog():
    articles = Article.all().order('-added')
    articles = [x for x in articles if x.is_public and not x.is_excerpt]
    # if articles.count() > 0:
    #     pager_number = articles.count()/10
    return render_template('blog.html', articles=articles)

@views.route('/excerpt/')
def excerpt():
    articles = Article.all().order('-added')
    articles = [x for x in articles if x.is_public and x.is_excerpt]
    return render_template('excerpt.html', articles=articles)

@views.route('/note/')
def note():
    notes = Note.all().order('-added')
    return render_template('note.html', notes=notes)

@views.route('/noteshub/')
def noteshub():
    return render_template('noteshub.html')

@views.route('/feed.atom')
def feed():
    articles = Article.all().order('-added')
    articles = [x for x in articles if x.is_public]
    return render_template('feed.atom', articles=articles)

@views.route('/ntfeed.atom')
def ntfeed():
    notes = Note.all().order('-added')
    return render_template('ntfeed.atom', notes=notes)

@views.route(r'/ajax/markdown/', methods=["POST",])
def ajax_markdown():
    text = request.form.get('text')
    if text is None:
        return "bad request"
    return pygments_markdown(text)


@views.route(r'/a/<int:number>/', methods=["POST", "GET"])
def get_aritle(number):
# make sure this is not the latest article
    article = get_aritle_by_number(number+1)
    # while article.is_excerpt:
    #     article = get_aritle_by_number(number+1)
        
    latestmarker = 1
    if article is None or not article.is_public:
        latestmarker = 0
    
    article = get_aritle_by_number(number)
    if article is None or not article.is_public:
        return render_template('404.html'), 404
    
    form = CommentForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                month_number = int(form.checker.data)
            except ValueError:
                month_number = 0
            if month_number != datetime.date.today().month:
                form.checker.errors = ["Sorry, but please prove you are a human."]
                form.checker.data = ""
            else:
                comment = Comment(
                    article_number=number,
                    author=form.author.data,
                    email=form.email.data,
                    comment=form.comment.data,
                )
                comment.save()
                return redirect(article.get_absolute_url())

    comments = get_comments(number)
    return render_template(
        'article.html',
        article=article,
        form=form,
        comments=comments,
        latestmarker=latestmarker,
    )

@views.route(r'/note/<int:number>/', methods=["POST", "GET"])
def get_note(number):    
    note = get_note_by_number(number)
    if note is None:
        return render_template('404.html'), 404
    
    return render_template(
        'note.html',
        note=note,
    )
   
@views.route(r'/p/<number>/')
@requires_auth
def get_private_aritle(number):
    """Render website's index page."""
    article = get_aritle_by_number(number)
    if article is None:
        return render_template('404.html'), 404
    return render_template('article.html', article=article)


@views.route(r'/tag/<tag>/')
def tag_articles(tag):
    articles = Article.all().order('-added')
    articles = [x for x in articles if x.is_public]
    articles = [x for x in articles if tag in x.tags.split(' ')]
    return render_template('tag.html', articles=articles, tag=tag)


# @views.route('/settings/', methods=["POST", "GET"])
# @requires_auth
# def settings():
#     form = SettingsForm()
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             pass
#     return render_template('settings.html', form=form)


@views.route('/add/', methods=["POST", "GET"])
@requires_auth
def add_article():
    """Add a article."""
    form = ArticleForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Get the right number - the article ID
            number = 1
            articles = Article.all().order('-number')
            if articles.count() > 0:
                number = articles[0].number + 1

            article = Article(
                number=number,
                title=form.title.data,
                content=form.content.data,
                tags=form.tags.data,
                is_public=form.is_public.data,
                is_excerpt=form.is_excerpt.data,
            )
            article.save()
            return redirect(article.get_absolute_url())
    action_url = url_for('add_article')
    return render_template('add_article.html', form=form, action_url=action_url)

@views.route('/ntadd/', methods=["POST", "GET"])
@requires_auth
def add_note():
    """Add a note."""
    form = ArticleForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Get the right number - the article ID
            number = 1
            notes = Note.all().order('-number')
            if notes.count() > 0:
                number = notes[0].number + 1

            note = Note(
                number=number,
                title=form.title.data,
                content=form.content.data,
                tags=form.tags.data,
            )
            note.save()
            return redirect(note.get_absolute_url())
    action_url = url_for('add_note')
    return render_template('add_note.html', form=form, action_url=action_url)

# @views.route('/signup/', methods=["POST", "GET"])
# def signup():
#     """Add a User."""
#     form = SignupForm()
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             # Get the right number - the user ID
#             number = 1
#             users = User.all().order('-number')
#             if users.count() > 0:
#                 number = users[0].number + 1


#             userinfo = User(
#                 number=number,
#                 title=form.title.data,
#                 content=generate_password_hash(form.content.data),
#             )
#             userinfo.save()
#             return redirect('/userlist/')
#     action_url = url_for('signup')
#     return render_template('user_signup.html', form=form, action_url=action_url)


@views.route('/userlist/')
@requires_auth
def userlist():
    users = User.all().order('-number')
    return render_template('userlist.html', users=users)



@views.route('/edit/<int:number>/', methods=["POST", "GET"])
@requires_auth
def edit_article(number):
    """Add a article."""
    article = get_aritle_by_number(number)
    if article is None:
        return render_template('404.html'), 404

    form = ArticleForm(
        title=article.title,
        content=article.content,
        is_public=article.is_public,
        tags=article.tags,
    )
    if request.method == 'POST':
        if form.validate_on_submit():
            article.title = form.title.data
            article.content = form.content.data
            article.is_public = form.is_public.data
            article.tags = form.tags.data
            article.save()
            return redirect(article.get_absolute_url())
    action_url = url_for('edit_article', number=number)
    return render_template('add_article.html', form=form, action_url=action_url)

@views.route('/ntedit/<int:number>/', methods=["POST", "GET"])
@requires_auth
def edit_note(number):
    """Edit a note."""
    note = get_note_by_number(number)
    if note is None:
        return render_template('404.html'), 404

    form = NoteForm(
        title=note.title,
        content=note.content,
        tags=note.tags,
    )
    if request.method == 'POST':
        if form.validate_on_submit():
            note.title = form.title.data
            note.content = form.content.data
            note.tags = form.tags.data
            note.save()
            return redirect(note.get_absolute_url())
    action_url = url_for('edit_note', number=number)
    return render_template('add_note.html', form=form, action_url=action_url)


@views.route('/edit/')
@requires_auth
def edit_list():
    """Render website's index page."""
    articles = Article.all().order('-added')
    return render_template('edit_list.html', articles=articles)

@views.route('/ntedit/')
@requires_auth
def ntedit_list():
    """Render website's index page."""
    notes = Note.all().order('-added')
    return render_template('ntedit_list.html', notes=notes)

@views.route('/md/')
def markdown_cn():
    """CN markdown page."""
    return render_template('cn_md.html')

@views.route('/md/en/')
def markdown_en():
    """EN markdown page."""
    return render_template('en_md.html')


@views.after_request
def add_header(response):
    """Add header to force latest IE rendering engine and Chrome Frame."""
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    return response


@views.app_errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

