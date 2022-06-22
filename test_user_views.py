"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        db.session.commit()

    def test_list_users(self):
        '''Test show list of users'''

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        with self.client as c:

            resp = c.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)

    def test_list_users_search(self):
        '''Test search param when listing users'''

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        with self.client as c:

            resp = c.get('/users?q=testuser')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)

    def test_show_user_profile(self):
        '''Test show user profile'''

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        with self.client as c:

            resp = c.get(f'/users/{u.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)

    def test_show_following(self):
        '''Test if logged in user can see the list another user is following'''

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            resp = c.get(f'/users/{testuser.id}/following')

            self.assertEqual(resp.status_code, 200)

    def test_show_following_logged_out(self):
        '''Test if user has access to following list while logged out'''

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        with self.client as c:

            resp = c.get(f'/users/{testuser.id}/following')

            self.assertEqual(resp.status_code, 302)

    def test_show_followers(self):
        '''Test if logged in user can see the list another user followers'''

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            resp = c.get(f'/users/{testuser.id}/followers')

            self.assertEqual(resp.status_code, 200)

    def test_show_followers_logged_out(self):
        '''Test if user has access to followers list while logged out'''

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        with self.client as c:

            resp = c.get(f'/users/{testuser.id}/followers')

            self.assertEqual(resp.status_code, 302)

    def test_add_follow(self):
        '''Test add follow'''

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

            db.session.commit()

            resp = c.post(f'/users/follow/{testuser2.id}')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'http://localhost/users/{testuser.id}/following')

    def test_add_follow_logged_out(self):
        '''Test add follow when user is logged out'''

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        with self.client as c:

            resp = c.post(f'/users/follow/{testuser.id}')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'http://localhost/')

    def test_stop_following(self):
        '''Test stop following'''

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

            db.session.commit()

            c.post(f'/users/follow/{testuser2.id}')

            resp = c.post(f'/users/stop-following/{testuser2.id}')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'http://localhost/users/{testuser.id}/following')

    def test_edit_user(self):
        '''Test user edit form'''

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            resp = c.post('/users/profile', data={"username": "testuser2",
                                            "email": "test@test.com",
                                            "password": "testuser",
                                            "image_url": None})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'http://localhost/users/{testuser.id}')

            resp2 = c.post('/users/profile', data={"username": "testuser2",
                                            "email": "test@test.com",
                                            "password": "test",
                                            "image_url": None})

            self.assertEqual(resp2.status_code, 302)
            self.assertEqual(resp2.location, 'http://localhost/')

            resp3 = c.get('/users/profile')
            html = resp3.get_data(as_text=True)

            self.assertEqual(resp3.status_code, 200)
            self.assertIn('<p>To confirm changes, enter your password:</p>', html)

    def test_delete_user(self):
        '''Test delete user'''

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            resp = c.post('/users/delete')

            u = User.query.all()

            self.assertEqual(resp.status_code, 302)
            self.assertNotIn(testuser, u)

    def test_list_likes(self):
        '''Test show list of users likes'''

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            resp = c.get(f'/users/{testuser.id}/likes')

            self.assertEqual(resp.status_code, 200)
