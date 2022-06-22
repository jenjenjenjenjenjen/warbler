"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        '''Does __repr__ function work?'''

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(f'{User.query.get(u.id)}', f'<User #{u.id}: {u.username}, {u.email}>')

    def test_is_following(self):
        '''Does is_following detect when a user is or isn't following another user'''

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        user2 = User(
            email="test2@test.com",
            username="test2user",
            password="HASHED_PASSWORD"
        )

        db.session.add(user1)
        db.session.commit()
        db.session.add(user2)
        db.session.commit()

        self.assertFalse(user1.is_following(user2))

        follow = Follows(user_being_followed_id=user2.id, user_following_id=user1.id)
        db.session.add(follow)
        db.session.commit()
        
        self.assertTrue(user1.is_following(user2))

    def test_is_followed_by(self):
        '''Does is_followed_by detect when a user is or is not followed by another user'''

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        user2 = User(
            email="test2@test.com",
            username="test2user",
            password="HASHED_PASSWORD"
        )

        db.session.add(user1)
        db.session.commit()
        db.session.add(user2)
        db.session.commit()

        self.assertFalse(user1.is_followed_by(user2))

        follow = Follows(user_being_followed_id=user2.id, user_following_id=user1.id)
        db.session.add(follow)
        db.session.commit()
        
        self.assertTrue(user2.is_followed_by(user1))

    def test_user_create(self):
        '''Test success of whether a user is created'''

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        user2 = User(
            email="test2@test.com",
            password="HASHED_PASSWORD"
        )

        self.assertIsInstance(user1, User)
        self.assertIsNone(user2.username)

    def test_user_authenticate(self):
        '''Test if User.authenticate successfully returns a user with the correct username and password
        Test if User.authenticate fails to return a user with invalid username/password'''

        user1 = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="img.png"
        )

        db.session.commit()

        self.assertEqual(user1.authenticate(username='testuser', password='HASHED_PASSWORD'), user1)
        self.assertFalse(user1.authenticate(username='bob', password='HASHED_PASSWORD'), user1)
        self.assertFalse(user1.authenticate(username='testuser', password='wrong_password'), user1)
