class User():
    def __init__(self, user_id, role_id, username, password, first_name=None, last_name=None, phone_num=None, email=None):
        self.user_id = user_id
        self.is_admin = (role_id == 1)
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.phone_num = phone_num
        self.email = email
    
