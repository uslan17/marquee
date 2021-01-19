from datetime import datetime
from post import Post

import os
from settings import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from flask import render_template, current_app, abort, request, redirect, url_for, flash, session, send_from_directory
from flask_session import Session

from forms import *

from users import User
from passlib.hash import pbkdf2_sha256 as hasher
from database import Database

from helpers import *
# from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

db = Database()


def home_page():
    if request.method == "GET":
        search_form = SearchForm()
        today = datetime.today()
        day_name = today.strftime("%A")
        return render_template("home.html", day=day_name, search_form=search_form)
    else:
        return render_template("flow.html", posts=posts, form=form, search_form=search_form)

@login_required
def posts_page():
    form = AddPostForm()
    search_form = SearchForm()

    categories = db.get_categories()
    mycats = []
    for i in categories:
        mycats.append((i['category_id'],i['category_title']))
    mycats.insert(0,(0,'Select a category'))
    
    search_form.search_category.choices = [(i[0], i[1]) for i in mycats]
    form.category.choices = [(i[0], i[1]) for i in mycats]
    
    if request.method == "GET":
        posts = db.get_user_posts(True)
        for post in posts:
            post["comments"] = db.get_comments(post["post_id"])
        return render_template("posts.html", posts=posts, form=form, search_form=search_form)
    else:
        if request.form.get("reply"):
            reply = request.form.get("reply")
            id = request.form.get("post_id")
            if check_appropriateness(reply):
                db.add_comment(reply, id)
            else:
                flash("We are not going to add your stupid comment!!")

        if form.validate_on_submit():
            category_id = form.data["category"]
            content = form.data["content"]
            title = form.data["title"]
            url = form.data["url"]
            
            if check_appropriateness(content) and check_appropriateness(title):

                file = request.files['photo']
                # if user does not select file, browser also
                # submit an empty part without filename
                if file.filename == '':
                    photo = None
                elif file and allowed_file(file.filename):
                    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
                    photo = file.filename

                post = Post(category_id, content, title, session["username"], photo, url)
                post.post_id = db.add_post(post, False)
            else:
                flash("We are not going to post your stupid post!!")
            return redirect(url_for("posts_page"))
        
        if search_form.validate_on_submit():
            username = search_form.data["search_username"]
            post_title = search_form.data["post_title"]
            category = search_form.data["search_category"]
            cur_time = datetime.now()
            posts = db.search_and_get_posts(username, post_title, category, True)
            return render_template("flow.html", posts=posts, cur_time=cur_time, form=form, search_form=search_form)

        return redirect(url_for("posts_page"))

@login_required
def notes_page():
    form = AddPostForm()
    search_form = SearchForm()

    categories = db.get_categories()
    mycats = []
    for i in categories:
        mycats.append((i['category_id'],i['category_title']))
    mycats.insert(0,(0,'Select a category'))
    
    search_form.search_category.choices = [(i[0], i[1]) for i in mycats]
    form.category.choices = [(i[0], i[1]) for i in mycats]

    if request.method == "GET":
        posts = db.get_user_posts(False) # get private posts
        for post in posts:
            post["comments"] = db.get_comments(post["post_id"])
        return render_template("notes.html", notes=posts, form=form, search_form=search_form)
    else:
        if request.form.get("reply"):
            reply = request.form.get("reply")
            id = request.form.get("post_id")
            if check_appropriateness(reply):
                db.add_comment(reply, id)
            else:
                flash("We are not going to add your stupid comment!!")
            return redirect(url_for("notes_page"))

        if form.validate_on_submit():
            category_id = form.data["category"]
            content = form.data["content"]
            title = form.data["title"]
            url = form.data["url"]

            if check_appropriateness(content) and check_appropriateness(title):
                file = request.files['photo']
                if file.filename == '':
                    photo = None
                elif file and allowed_file(file.filename):
                    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
                    photo = file.filename
                post = Post(category_id, content, title, session["username"], photo, url)
                post.post_id = db.add_post(post, False) # add a private post
            else:
                flash("We are not going to post your stupid post!!")
            return redirect(url_for("notes_page"))
        
        if search_form.validate_on_submit():
            username = search_form.data["search_username"]
            post_title = search_form.data["post_title"]
            category = search_form.data["search_category"]
            cur_time = datetime.now()
            posts = db.search_and_get_posts(username, post_title, category, True)
            return render_template("flow.html", posts=posts, cur_time=cur_time, form=form, search_form=search_form)

    return redirect(url_for("notes_page"))

@login_required
def flow_page():
    add_post_form = AddPostForm()
    search_form = SearchForm()

    categories = db.get_categories()
    mycats = []
    for i in categories:
        mycats.append((i['category_id'],i['category_title']))
    mycats.insert(0,(0,'Select a category'))
    
    search_form.search_category.choices = [(i[0], i[1]) for i in mycats]
    add_post_form.category.choices = [(i[0], i[1]) for i in mycats]

    if request.method == "GET":
        posts = db.get_posts()
        for post in posts:
            post["comments"] = db.get_comments(post["post_id"])
        cur_time = datetime.now()
        return render_template("flow.html", posts=posts, cur_time=cur_time, form=add_post_form, search_form=search_form)
    else:
        if request.form.get("reply"):
            reply = request.form.get("reply")
            id = request.form.get("post_id")
            if check_appropriateness(reply):
                db.add_comment(reply, id)
            else:
                flash("We are not going to add your stupid comment!!")
        
        if add_post_form.validate_on_submit():
            category_id = add_post_form.data["category"]
            content = add_post_form.data["content"]
            title = add_post_form.data["title"]
            url = add_post_form.data["url"]

            if check_appropriateness(content) and check_appropriateness(title):
                file = request.files['photo']
                # if user does not select file, browser also
                # submit an empty part without filename
                if file.filename == '':
                    photo = None
                elif file and allowed_file(file.filename):
                    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
                    photo = file.filename

                post = Post(category_id, content, title, username=session["username"], photo=photo, video=url)
                post.post_id = db.add_post(post, True)
                return redirect(url_for("flow_page"))
            else:
                flash("We are not going to post your stupid post!!")
                return redirect(url_for("flow_page"))
        

        if search_form.validate_on_submit():
            username = search_form.data["search_username"]
            post_title = search_form.data["post_title"]
            category = search_form.data["search_category"]
            cur_time = datetime.now()
            posts = db.search_and_get_posts(username, post_title, category, True)
            return render_template("flow.html", posts=posts, cur_time=cur_time, form=add_post_form, search_form=search_form)
            
        return redirect(url_for("flow_page"))

@login_required
def profile_page():
    form = ProfileEditForm()
    search_form = SearchForm()

    user = db.get_user(session["username"])
    if user == None:
        flash("Something went wrong")
        return redirect("home_page")
    if request.method == "GET":
        return render_template("profile.html", user=user, form=form, search_form=search_form)
    else:
        form = request.form
        db.update_profile(user, form)
        session["username"] = form['username']
        return redirect("/profile")

@login_required
def post_page(post_id):
    search_form = SearchForm()

    post = db.get_post(post_id)
    if post is None:
        return apology("Post is not found !")
    return render_template("post.html", post=post, search_form=search_form)

@login_required
def post_edit_page(post_id):
    form = PostEditForm()
    search_form = SearchForm()

    if request.method == "GET":
        post = db.get_post(post_id)
        form.content.data = post["text_field"]
        return render_template("post_edit.html", form=form, post_id=post_id, search_form=search_form)
    else:
        if form.validate_on_submit():
            content = form.data["content"]
            db.update_post(post_id, content)
        return redirect(url_for("flow_page"))


def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.data["username"]
        user = db.get_user(username)
        if user is not None:
            if hasher.verify(form.data["password"], user.password):
                
                session["username"] = user.username
                session["is_admin"] = user.is_admin
                session["user_id"] = user.user_id
                session["logged_in"] = True
                flash("You have loggedd in.")
                return redirect(url_for("flow_page"))
        flash("Invalid credentials.")
    return render_template("login.html", form=form)

def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        db.add_user(form)
        flash('Thanks for registering')
        return redirect(url_for('login_page'))
    return render_template("register.html", form=form)

@login_required
def logout_page():
    session.pop('username', None) 
    session.pop('user_id', None) 
    session.pop('is_admin', None) 
    session["logged_in"] = False
    flash("You have logged out.")
    return redirect(url_for("home_page"))

def contact_page():
    form = ContactForm()
    search_form = SearchForm()

    if form.validate_on_submit():
        form = request.form
        db.add_contact(form)
        return redirect(url_for("contact_page"))
    return render_template("contact.html", form=form, search_form=search_form)

@login_required
def post_delete_page(post_id):
    db.delete_post(post_id)
    return redirect(url_for("flow_page"))

@login_required   
def settings_page():
    if session["is_admin"]:

        form = SearchForm()
        add_category_form = AddCategoryForm()
        delete_category_form = DeleteCategoryForm()
        
        categories = db.get_categories()

        mycats = []
        for i in categories:
            mycats.append((i['category_id'],i['category_title']))
        mycats.insert(0,(0,'Select a category'))
        form.search_category.choices = [(i[0], i[1]) for i in mycats]
        delete_category_form.delete_category.choices = [(i[0], i[1]) for i in mycats]
        
        users = db.get_usernames()
        contacts = db.get_contacts()
        
        
        if add_category_form.validate_on_submit():
            add_category = add_category_form.data["add_category"]
            db.add_category(add_category)
            return redirect(url_for("settings_page"))
        if delete_category_form.validate_on_submit():
            delete_category_id = delete_category_form.data["delete_category"]
            if delete_category_id == '0':
                return apology("Please select a category if you want to delete one!")
            db.delete_category(delete_category_id)
            flash("You have just deleted category!")
            return redirect(url_for("settings_page"))
        
        if request.form.get('user'):
            id = request.form.get('user')
            if id == '0':
                return apology("Plesase select a user if you want to give tha admin role to a user!")
            db.give_admin_role(id)
            flash("Warning! You have just gave the admin role to another user!")
            return redirect(url_for("settings_page"))
        return render_template("settings.html", add_form=add_category_form, delete_form=delete_category_form, search_form=form, users=users, contacts=contacts)
    else:
        return apology("You are not allowed to do this.")

@login_required
def delete_comment_page(comment_id):
    db.delete_comment(comment_id)
    return redirect(url_for('flow_page'))
    
@login_required
def delete_account_page():
    db.delete_user(session['user_id'])
    flash("You have deleted your account permenantly !")
    return redirect(url_for('logout_page'))

# some helper functions

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_appropriateness(text):
    badwords = ["abaza","abazan","ag","a\u011fz\u0131na s\u0131\u00e7ay\u0131m","ahmak","allahs\u0131z","am","amar\u0131m","ambiti","am biti","amc\u0131\u011f\u0131","amc\u0131\u011f\u0131n","amc\u0131\u011f\u0131n\u0131","amc\u0131\u011f\u0131n\u0131z\u0131","amc\u0131k","amc\u0131k ho\u015faf\u0131","amc\u0131klama","amc\u0131kland\u0131","amcik","amck","amckl","amcklama","amcklaryla","amckta","amcktan","amcuk","am\u0131k","am\u0131na","am\u0131nako","am\u0131na koy","am\u0131na koyar\u0131m","am\u0131na koyay\u0131m","am\u0131nakoyim","am\u0131na koyyim","am\u0131na s","am\u0131na sikem","am\u0131na sokam","am\u0131n feryad\u0131","am\u0131n\u0131","am\u0131n\u0131 s","am\u0131n oglu","am\u0131no\u011flu","am\u0131n o\u011flu","am\u0131s\u0131na","am\u0131s\u0131n\u0131","amina","amina g","amina k","aminako","aminakoyarim","amina koyarim","amina koyay\u0131m","amina koyayim","aminakoyim","aminda","amindan","amindayken","amini","aminiyarraaniskiim","aminoglu","amin oglu","amiyum","amk","amkafa","amk \u00e7ocu\u011fu","amlarnzn","aml\u0131","amm","ammak","ammna","amn","amna","amnda","amndaki","amngtn","amnn","amona","amq","ams\u0131z","amsiz","amsz","amteri","amugaa","amu\u011fa","amuna","ana","anaaann","anal","analarn","anam","anamla","anan","anana","anandan","anan\u0131","anan\u0131","anan\u0131n","anan\u0131n am","anan\u0131n am\u0131","anan\u0131n d\u00f6l\u00fc","anan\u0131nki","anan\u0131sikerim","anan\u0131 sikerim","anan\u0131sikeyim","anan\u0131 sikeyim","anan\u0131z\u0131n","anan\u0131z\u0131n am","anani","ananin","ananisikerim","anani sikerim","ananisikeyim","anani sikeyim","anann","ananz","anas","anas\u0131n\u0131","anas\u0131n\u0131n am","anas\u0131 orospu","anasi","anasinin","anay","anayin","angut","anneni","annenin","annesiz","anuna","aptal","aq","a.q","a.q.","aq.","ass","atkafas\u0131","atm\u0131k","att\u0131rd\u0131\u011f\u0131m","attrrm","auzlu","avrat","ayklarmalrmsikerim","azd\u0131m","azd\u0131r","azd\u0131r\u0131c\u0131","babaannesi ka\u015far","baban\u0131","baban\u0131n","babani","babas\u0131 pezevenk","baca\u011f\u0131na s\u0131\u00e7ay\u0131m","bac\u0131na","bac\u0131n\u0131","bac\u0131n\u0131n","bacini","bacn","bacndan","bacy","bastard","basur","beyinsiz","b\u0131z\u0131r","bitch","biting","bok","boka","bokbok","bok\u00e7a","bokhu","bokkkumu","boklar","boktan","boku","bokubokuna","bokum","bombok","boner","bosalmak","bo\u015falmak","cenabet","cibiliyetsiz","cibilliyetini","cibilliyetsiz","cif","cikar","cim","\u00e7\u00fck","dalaks\u0131z","dallama","daltassak","dalyarak","dalyarrak","dangalak","dassagi","diktim","dildo","dingil","dingilini","dinsiz","dkerim","domal","domalan","domald\u0131","domald\u0131n","domal\u0131k","domal\u0131yor","domalmak","domalm\u0131\u015f","domals\u0131n","domalt","domaltarak","domalt\u0131p","domalt\u0131r","domalt\u0131r\u0131m","domaltip","domaltmak","d\u00f6l\u00fc","d\u00f6nek","d\u00fcd\u00fck","eben","ebeni","ebenin","ebeninki","ebleh","ecdad\u0131n\u0131","ecdadini","embesil","emi","fahise","fahi\u015fe","feri\u015ftah","ferre","fuck","fucker","fuckin","fucking","gavad","gavat","geber","geberik","gebermek","gebermi\u015f","gebertir","ger\u0131zekal\u0131","gerizekal\u0131","gerizekali","gerzek","giberim","giberler","gibis","gibi\u015f","gibmek","gibtiler","goddamn","godo\u015f","godumun","gotelek","gotlalesi","gotlu","gotten","gotundeki","gotunden","gotune","gotunu","gotveren","goyiim","goyum","goyuyim","goyyim","g\u00f6t","g\u00f6t deli\u011fi","g\u00f6telek","g\u00f6t herif","g\u00f6tlalesi","g\u00f6tlek","g\u00f6to\u011flan\u0131","g\u00f6t o\u011flan\u0131","g\u00f6to\u015f","g\u00f6tten","g\u00f6t\u00fc","g\u00f6t\u00fcn","g\u00f6t\u00fcne","g\u00f6t\u00fcnekoyim","g\u00f6t\u00fcne koyim","g\u00f6t\u00fcn\u00fc","g\u00f6tveren","g\u00f6t veren","g\u00f6t verir","gtelek","gtn","gtnde","gtnden","gtne","gtten","gtveren","hasiktir","hassikome","hassiktir","has siktir","hassittir","haysiyetsiz","hayvan herif","ho\u015faf\u0131","h\u00f6d\u00fck","hsktr","huur","\u0131bnel\u0131k","ibina","ibine","ibinenin","ibne","ibnedir","ibneleri","ibnelik","ibnelri","ibneni","ibnenin","ibnerator","ibnesi","idiot","idiyot","imansz","ipne","iserim","i\u015ferim","ito\u011flu it","kafam girsin","kafas\u0131z","kafasiz","kahpe","kahpenin","kahpenin feryad\u0131","kaka","kaltak","kanc\u0131k","kancik","kappe","karhane","ka\u015far","kavat","kavatn","kaypak","kayyum","kerane","kerhane","kerhanelerde","kevase","keva\u015fe","kevvase","koca g\u00f6t","kodu\u011fmun","kodu\u011fmunun","kodumun","kodumunun","koduumun","koyarm","koyay\u0131m","koyiim","koyiiym","koyim","koyum","koyyim","krar","kukudaym","laciye boyad\u0131m","lavuk","libo\u015f","madafaka","mal","malafat","malak","manyak","mcik","meme","memelerini","mezveleli","minaamc\u0131k","mincikliyim","mna","monakkoluyum","motherfucker","mudik","oc","ocuu","ocuun","O\u00c7","o\u00e7","o. \u00e7ocu\u011fu","o\u011flan","o\u011flanc\u0131","o\u011flu it","orosbucocuu","orospu","orospucocugu","orospu cocugu","orospu \u00e7oc","orospu\u00e7ocu\u011fu","orospu \u00e7ocu\u011fu","orospu \u00e7ocu\u011fudur","orospu \u00e7ocuklar\u0131","orospudur","orospular","orospunun","orospunun evlad\u0131","orospuydu","orospuyuz","orostoban","orostopol","orrospu","oruspu","oruspu\u00e7ocu\u011fu","oruspu \u00e7ocu\u011fu","osbir","ossurduum","ossurmak","ossuruk","osur","osurduu","osuruk","osururum","otuzbir","\u00f6k\u00fcz","\u00f6\u015fex","patlak zar","penis","pezevek","pezeven","pezeveng","pezevengi","pezevengin evlad\u0131","pezevenk","pezo","pic","pici","picler","pi\u00e7","pi\u00e7in o\u011flu","pi\u00e7 kurusu","pi\u00e7ler","pipi","pipi\u015f","pisliktir","porno","pussy","pu\u015ft","pu\u015fttur","rahminde","revizyonist","s1kerim","s1kerm","s1krm","sakso","saksofon","salaak","salak","saxo","sekis","serefsiz","sevgi koyar\u0131m","sevi\u015felim","sexs","s\u0131\u00e7ar\u0131m","s\u0131\u00e7t\u0131\u011f\u0131m","s\u0131ecem","sicarsin","sie","sik","sikdi","sikdi\u011fim","sike","sikecem","sikem","siken","sikenin","siker","sikerim","sikerler","sikersin","sikertir","sikertmek","sikesen","sikesicenin","sikey","sikeydim","sikeyim","sikeym","siki","sikicem","sikici","sikien","sikienler","sikiiim","sikiiimmm","sikiim","sikiir","sikiirken","sikik","sikil","sikildiini","sikilesice","sikilmi","sikilmie","sikilmis","sikilmi\u015f","sikilsin","sikim","sikimde","sikimden","sikime","sikimi","sikimiin","sikimin","sikimle","sikimsonik","sikimtrak","sikin","sikinde","sikinden","sikine","sikini","sikip","sikis","sikisek","sikisen","sikish","sikismis","siki\u015f","siki\u015fen","siki\u015fme","sikitiin","sikiyim","sikiym","sikiyorum","sikkim","sikko","sikleri","sikleriii","sikli","sikm","sikmek","sikmem","sikmiler","sikmisligim","siksem","sikseydin","sikseyidin","siksin","siksinbaya","siksinler","siksiz","siksok","siksz","sikt","sikti","siktigimin","siktigiminin","sikti\u011fim","sikti\u011fimin","sikti\u011fiminin","siktii","siktiim","siktiimin","siktiiminin","siktiler","siktim","siktim","siktimin","siktiminin","siktir","siktir et","siktirgit","siktir git","siktirir","siktiririm","siktiriyor","siktir lan","siktirolgit","siktir ol git","sittimin","sittir","skcem","skecem","skem","sker","skerim","skerm","skeyim","skiim","skik","skim","skime","skmek","sksin","sksn","sksz","sktiimin","sktrr","skyim","slaleni","sokam","sokar\u0131m","sokarim","sokarm","sokarmkoduumun","sokay\u0131m","sokaym","sokiim","soktu\u011fumunun","sokuk","sokum","soku\u015f","sokuyum","soxum","sulaleni","s\u00fclaleni","s\u00fclalenizi","s\u00fcrt\u00fck","\u015ferefsiz","\u015f\u0131ll\u0131k","taaklarn","taaklarna","tarrakimin","tasak","tassak","ta\u015fak","ta\u015f\u015fak","tipini s.k","tipinizi s.keyim","tiyniyat","toplarm","topsun","toto\u015f","vajina","vajinan\u0131","veled","veledizina","veled i zina","verdiimin","weled","weledizina","whore","xikeyim","yaaraaa","yalama","yalar\u0131m","yalarun","yaraaam","yarak","yaraks\u0131z","yaraktr","yaram","yaraminbasi","yaramn","yararmorospunun","yarra","yarraaaa","yarraak","yarraam","yarraam\u0131","yarragi","yarragimi","yarragina","yarragindan","yarragm","yarra\u011f","yarra\u011f\u0131m","yarra\u011f\u0131m\u0131","yarraimin","yarrak","yarram","yarramin","yarraminba\u015f\u0131","yarramn","yarran","yarrana","yarrrak","yavak","yav\u015f","yav\u015fak","yav\u015fakt\u0131r","yavu\u015fak","y\u0131l\u0131\u015f\u0131k","yilisik","yogurtlayam","yo\u011furtlayam","yrrak","z\u0131kk\u0131m\u0131m","zibidi","zigsin","zikeyim","zikiiim","zikiim","zikik","zikim","ziksiiin","ziksiin","zulliyetini","zviyetini"]
    words = text.split()

    for word in words:
        if word in badwords:
            flash("Don't be rude man!")
            return False
    return True
    
