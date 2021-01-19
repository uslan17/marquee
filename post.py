from datetime import datetime


class Post:
    def __init__(self, category_id, content, title, username, post_id=None, photo=None, video=None, create_date=datetime.now(), update_date=datetime.now()):
        self.post_id = post_id
        self.title = title
        self.username = username
        self.photo = photo
        self.video = video
        self.category_id = category_id
        self.content = content
        self.create_date = create_date
        self.update_date = update_date

        