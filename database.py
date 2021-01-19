import psycopg2 as dbapi2
from post import Post
import psycopg2.extras
from passlib.hash import pbkdf2_sha256 as hasher
from users import User
from flask import session, flash
from connect import connect
# from users import User
#  data source name (DSN)  user = ..  password = ..  host = ..  port = ..  dbname = ..
#  uniform resource identifier (URI) postgres://<username>:>password>@<host>:<port>/<dbname>

dsn = "host=localhost dbname=marquee user=postgres password=limonpostu"
connection = dbapi2.connect(dsn)

class Database:
    def __init__(self):
        pass

    def add_post(self, post, public):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("INSERT INTO posts (user_id, category_id, title, text_field, is_public, photo, video) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING post_id", (session["user_id"], post.category_id, post.title, post.content, public, post.photo, post.video,))
            id = cursor.fetchone()["post_id"]
        except:
            flash("Something went wrong ! We could not add your post.")
        finally:
            connection.commit()
        return id

    def delete_post(self, post_id):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = "DELETE FROM posts WHERE post_id = %s" % (post_id,)
            cursor.execute(query)
        except:
            flash("Something went wrong ! We could not delete your post.")
        finally:
            connection.commit()
        return

    def get_post(self, post_id):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = """SELECT posts.post_id, posts.title, posts.text_field, username, posts.update_date, category.category_title
                FROM posts LEFT JOIN category ON posts.category_id = category.category_id
				INNER JOIN users 
                ON users.user_id = posts.user_id 
                WHERE posts.post_id = %s""" % (post_id,)
            cursor.execute(query) 
            post_ = cursor.fetchone()
        except:
            flash("Something went wrong ! We could not get the post.")
        finally:
            connection.commit()
        return post_

    def update_post(self, post_id, content):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("UPDATE posts SET text_field = %s WHERE post_id = %s", (content, post_id,))
        except:
            flash("Something went wrong ! We could not update your post.")
        finally:
            connection.commit()
        return

    def get_posts(self):
        posts = {}
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = """SELECT posts.post_id, posts.title, posts.text_field, username, posts.update_date, category.category_title, posts.photo, posts.video
                FROM posts LEFT JOIN category ON posts.category_id = category.category_id
				INNER JOIN users 
                ON users.user_id = posts.user_id 
                WHERE is_public = true
                ORDER BY update_date DESC"""
            cursor.execute(query)
            posts = cursor.fetchall()
        except:
            flash("Something went wrong ! We could not get posts.")
        finally:
            connection.commit()
        return posts

    def search_and_get_posts(self, username, title, category, public):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        
        posts = {}
        where_query = ''

        user_query = "username ILIKE '%s'" % username
        title_query =  "title = '%s'" % title
        category_query = "posts.category_id = %s" % category

        if username != '':
            where_query += user_query
            if title != '':
                where_query += ' and ' + title_query
                if category:
                    where_query += ' and ' + category_query
            elif category:
                where_query += ' and ' + category_query
            where_query += " and is_public = %s" % public
        elif title != '':
            where_query += title_query
            if category:
                where_query += ' and' + category_query
            where_query += " and is_public = %s" % public
        elif category:
            where_query += category_query
            where_query += " and is_public = %s" % public
        else:
            where_query = "is_public = %s" % public

        try:
            query = """SELECT posts.post_id, posts.title, posts.text_field, username, posts.update_date, category.category_title, posts.photo, posts.video
                    FROM posts LEFT JOIN category ON posts.category_id = category.category_id
                    INNER JOIN users 
                    ON users.user_id = posts.user_id 
                    WHERE (%s)""" % (where_query,)
            cursor.execute(query)
            posts = cursor.fetchall()
        except:
            flash("Something went wrong ! We could not do the searching.")
        finally:
            connection.commit()
        return posts

    def get_comments(self, post_id):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        comments = {}
        try:
            query = """SELECT username, create_date, comment_text, comment_id
                    FROM comments
                    LEFT JOIN users
                    ON users.user_id = comments.user_id
                    WHERE post_id = %s ORDER BY create_date DESC
                    LIMIT 2""" % (post_id,)
            cursor.execute(query)
            comments = cursor.fetchall()
        except:
            flash("Something went wrong ! We could not find the comments.")
        finally:
            connection.commit()
        return comments

    def add_comment(self, comment, post_id):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = "INSERT INTO comments (user_id, post_id, comment_text) VALUES (%s,%s,'%s')" % (session["user_id"], post_id, comment,)
            cursor.execute(query)
        except:
            flash("Something went wrong ! We could not add your comment.")
        finally:
            connection.commit()
        return

    def delete_comment(self, comment_id):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = "DELETE FROM comments WHERE comment_id=%s" % comment_id
            cursor.execute(query)
        except:
            flash("Something went wrong ! We could not delete that comment.")
        finally:
            connection.commit()
        return


    def get_user_posts(self, public):
        posts = {}
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = """SELECT posts.post_id, posts.title, posts.text_field, posts.update_date, category.category_title, posts.photo, posts.video
                FROM posts left join category on posts.category_id = category.category_id
                INNER JOIN users 
                ON users.user_id = posts.user_id 
                WHERE (users.username = '%s' and is_public = '%s')
                ORDER BY update_date desc""" % (session["username"], public,)
            cursor.execute(query)
            posts = cursor.fetchall()
        except:
            flash("Something went wrong ! We could not find your posts.")
        finally:
            connection.commit()
        return posts

    def get_user(self, username):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM users WHERE username = '%s'" % username
        cursor.execute(query)    
        row = cursor.fetchone()
        user = User(row["user_id"], row["role_id"], row["username"], row["password"], row["first_name"], row["last_name"], row["phone_num"], row["email"])
        connection.commit()
        return user

    def get_usernames(self):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        users = {}
        try:
            cursor.execute("SELECT username, user_id FROM users WHERE role_id = 0")
            users = cursor.fetchall()
        except:
            flash("Something went wrong ! We could not find what the potential admin users are.")
        finally:
            connection.commit()
        return users

    def add_user(self, form):
        hash = hasher.hash(form.data["password"])
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = """INSERT INTO users (role_id, username, password, first_name, last_name, phone_num, email) 
                    VALUES (0,'%s','%s','%s','%s','%s','%s')""" % (form.data["username"], hash, form.data["first_name"], form.data["last_name"],form.data["phone_num"],form.data["email"],)
            cursor.execute(query)
        except:
            flash("Something went wrong ! Registering fialed.")
        finally:
            connection.commit()
        return
    
    def delete_user(self, user_id):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = "DELETE FROM users WHERE user_id = %s" % (user_id,)
            cursor.execute(query)
        except:
            flash("Something went wrong ! Deleting your account is failed.")
        finally:
            connection.commit()
        return

    def get_categories(self):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        categories = {}
        try:
            cursor.execute("SELECT * FROM category")
            categories = cursor.fetchall()
        except:
            flash("Something went wrong ! We could not find what the categories are.")
        finally:
            connection.commit()
        return categories
    
    def add_category(self, category):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = "INSERT INTO category (category_title) VALUES ('%s')" % (category,)
            cursor.execute(query)
        except:
            flash("Something went wrong ! We could not add the category.")
        finally:
            connection.commit()
        return
    
    def delete_category(self, id):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("DELETE FROM category WHERE category_id = %s", (id,))
        except:
            flash("Something went wrong ! We could not delete the category.")
        finally:
            connection.commit()
        return

    def update_profile(self, user, form):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = "UPDATE users SET first_name='%s', last_name='%s', username='%s', email='%s', phone_num='%s'  WHERE user_id = %s" % (form['first_name'], form['last_name'], form['username'], form['email'], form['phone_num'], user.user_id,)
            cursor.execute(query)
        except:
            flash("Something went wrong ! We could not update your profile.")
        finally:
            connection.commit()
        return

    def add_contact(self, form):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = "INSERT INTO contacts (name, subject, contact_content, email) VALUES ('%s','%s','%s','%s')" % (form['name'], form['subject'], form['message'], form['email'],)
            cursor.execute(query)
            flash("Your message is successfully sent.")
        except:
            flash("Something went wrong ! We could not send your message.")
        finally:
            connection.commit()
        return

    def give_admin_role(self, user_id):
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            query = "UPDATE users SET role_id = 1  WHERE user_id = %s" % (user_id,) 
            cursor.execute(query)
        except:
            flash("Something went wrong ! We could not give the admin role.")
        finally:
            connection.commit()
        return    
    
    def get_contacts(self):
        contacts = {}
        cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM contacts ORDER BY create_date desc")
            contacts = cursor.fetchall()
        except:
            flash("Something went wrong ! We could not fetch contacts.")
        finally:
            connection.commit()
        return contacts