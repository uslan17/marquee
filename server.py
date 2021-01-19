from flask import Flask, session
import views

def create_app():
    
    app = Flask(__name__)
    app.config.from_object("settings")
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
    app.add_url_rule("/register", view_func=views.register_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=views.logout_page)
    app.add_url_rule("/contact", view_func=views.contact_page, methods=["GET", "POST"])
    app.add_url_rule("/posts", view_func=views.posts_page, methods=["GET", "POST"])
    app.add_url_rule("/posts/<int:post_id>/edit",view_func=views.post_edit_page,methods=["GET", "POST"])
    app.add_url_rule("/notes", view_func=views.notes_page, methods=["GET", "POST"])
    app.add_url_rule("/flow", view_func=views.flow_page, methods=["GET", "POST"])
    app.add_url_rule("/profile", view_func=views.profile_page, methods=["GET", "POST"])
    app.add_url_rule("/posts/<int:post_key>", view_func=views.post_page)
    app.add_url_rule("/posts/<int:post_id>/delete", view_func=views.post_delete_page, methods=["GET", "POST"])
    app.add_url_rule("/settings", view_func=views.settings_page, methods=["GET", "POST"])

    app.add_url_rule("/comments/<int:comment_id>/delete", view_func=views.delete_comment_page, methods=["GET", "POST"])
    app.add_url_rule("/delete_account", view_func=views.delete_account_page, methods=["GET", "POST"])

    return app


if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 5000)
    app.run(host="localhost", port=port)