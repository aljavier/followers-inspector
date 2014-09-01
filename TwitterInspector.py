#!/usr/bin/env python

import sqlite3 as lite
import datime
import sys
import traceback

# If tweepy is not installed exit
try:
    import tweepy
except:
    print(sys.exc_info())
    print("Please install tweepy to use %s." % sys.argv[0])
    print("On mostly unix-like systems the easier way to install it is: pip install tweepy.")
    sys.exit(-1)

# Some config variables
CONSUMER_KEY= = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"
USER_NAME = "n3x07" # We need it for the follow_all method, to check if someone follow you already or no

class DbConnection(object):
    """Abstract class for the persistent storage on database."""
    
    def __init__(self, DB_NAME, DB_HOST="SQLite", USER=None, PASS=None):
        """Abstract method to be implemented for the connection"""
        raise NotImplementedError("You must implement this method!")
    
    def connect():
        """The method that start the connection to the database."""
        raise NotImplementedError("You must implement this method!")

    def get_all(self,table_name):
        """Return all records from table_name."""
        raise NotImplementedError("You must implement this method!")

    def get(self, id, table_name):
        """Return an element with the id provided from table_name."""
        raise NotImplementedError("You must implement this method!")

    def update(self, id, table_name, **kwargs):
        """
        Update the element specified as parameter on the table_name and 
        return True if there were not error, False otherwise.
        """
        raise NotImplementedError("You must implement this method!")

    def delete(self, id, table_name, **kwargs):
        """
        Delete the records on table_name with the id specified and any other
        optional attributes.
        """
        raise NotImplementedError("You must implement this method!")

    def add(self, table_name, **kwargs):
        """Insert a new record on table_name with the data provided in **kwargs."""
        raise NotImplementedError("You must implement this method!")

    def seed():
        """This method create the neede tables, and could populate also,the database."""
        raise NotImplementedError("You must implement this method!")



class SQLiteConnection(DbConnection):
    """Concrete class for the data persistent on database using SQLite."""
    
    def __init__(self,DB_NAME, DB_HOST="SQLite", USER=None, PASS=None):
        """DB_NAME is the name of the sqlite database, the others arguments are not needed here."""
        self.db_name = DB_NAME
        self.conn = None

    def connect(self):     
        "This method connect to an embedded SQLite database file."
        try:
            self.conn = lite.connect(self.db_name)
            # In order to get the objects always as dictionary we set this:
            self.conn.row_factory = lite.Row
        except lite.Error:
            print("We got an error here, printing more info below.")
            print(traceback.format_exc())
            print("Quitting now...")
            sys.exit(-1)

    def get_all(self, table_name, LIMIT=None):
        """This method will return a list of dictionaries with all available records or an empty list."""
        try:
            cur = self.conn.cursor()
            sql = "SELECT * FROM " + table_name
            if LIMIT is None:
               cur.execute("SELECT * FROM %s" % table_name)
            else:
                cur.execute(sql + " LIMIT " + LIMIT) # This will not be really needed, except for get the credentials
            rows = cur.fetchall()
            return rows
        except lite.Error:
            print("We got an error here, printing more info below.")
            print(traceback.format_exc())
        finally:
            cur.close()

    def get(self, id, table_name):
        """This method return a dictionary(record) from table_name with the specified id or None."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM " + table_name + " WHERE id = ?", id)
            row = cur.fetchone()
            return row
        except lite.Error:
            print("We got an error here, printing more info below.")
            print(traceback.format_exc())
        finally:
            cur.close()

    def update(self, id, table_name, user_id, screen_name):
        """This method update the record(s) with the specified id."""
        try:
            cur = self.conn.cursor()
            if kwargs:
                # Look that we are expecting a dictionary with this keys and some values, obligatory.
                sql = "UPDATE " + table_name + " SET user_id = ?, scree_name = ?, date = ? WHERE id = ?"
                cur.execute(sql, user_id, screen_name, id, datetime.now())
                self.conn.commit()
                print("%d records have been updated!" % cur.rowcount)
        except lite.Error:
            if self.conn:
               self.conn.rollback()
            print("We got an error here, printing more info below.")
            print(traceback.format_exc())
        finally:
            cur.close()

    def delete(self, id, table_name):
        """This method remove record(s) from the database with the specified id."""
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM " + table_name + " WHERE id = ?", id)
            self.conn.commit()
        except lite.Error:
            if self.conn:
               self.conn.rollback()
            print("We got an error here, printing more info below.")
            print(traceback.format_exc())
        finally:
            cur.close()

    def raw_sql(self, sql):
        """This method will run an sql sentence passed as argument, it does not inherit from DbConnection"""
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
        except lite.Error:
            if self.conn:
                self.conn.rollback()
            print("We got an error over here, check the description below.")
            print(traceback.format_exc())

    def add(self, table_name, user_id, screen_name):
        """This method insert a new record in table_name with user_id and screen_name and return the id."""
        try:
            cur = self.conn.cursor()
            sql = "INSERT INTO " + table_name + " (user_id, screen_name, date) VALUES(?, ?, ?)"
            cur.execute(user_id, screen_name, datetime.now())
            self.conn.commit()
            return cur.lastrowid
        except lite.Error:
            if self.conn:
                self.conn.rollback()
            print("We got an error over here, more info below.")
            print(traceback.format_exc())
        finally:
            cur.close()

    def seed(self):
        """This method will create the tables needed for this app."""
        try:
            cur = self.conn.cursor()
            sql = """
                     CREATE TABLE credentials(id integer primary key autoincrement, key text, secret text);
                     CREATE TABLE followers(id integer primary key, user_id text, scree_name text, date text);
                     CREATE TABLE unfollowers(id integer primary key, user_id text, screen_name text, date text);
                  """
            cur.executescript(sql)
            self.conn.commit()
        except lite.Error:
            if self.conn:
                self.conn.rollback()
            print("We got an error here, more info below.")
            print(traceback.format_exc())
        finally:
            cur.close()

    def __str__(self):
        return "Database connection for database named %s." % self.db_name
    

class TwitterInspector(object):
    """The class that interact with the Twitter API throught tweepy library."""
   
   def __init__(self, db_name, consumer_key, consumer_secret, key=None, secret=None):
        self.__data = SQLiteConnection(db_name)
        self.followers = []
        self.unfollower = []
        self.api = None
        try:
           self.__auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        except tweepy.TweepError:
            print("We got an error with the consumer access token, more info below.")
            print(traceback.format_exc())   
            print("This is critical! Quitting now...")
            sys.exit(-1)
        # Autentificate the client
        self.__autentificate()

    def __autentificate(self):
        """This method deal with the autorization of the script with Twitter"""
        credentials = self.__data.get_all("credentials", LIMIT=1) # We just need one, right? right?!
        if credentials is None:
            print("There aren't any credential in the database!!!")
            answer = raw_input("Would do you like to add any now? >>> ")
            answer = answer.strip().lower()
            if answer == "yes" or answer == "y":
                try:
                    url = tweepy.OAuthHandler.get_authorization_url()
                    print("You can get your access token going with your web browser to this url >>> %s" % url)
                    verifier = raw_input("Please introduce the verifier code you got >>> ").strip()
                    self.__auth.get_access_token(verifier)
                    key = self.__auth.access_token.key
                    secret = self.__auth.access_token.secret
                    # Now let's store those credentials for later on
                    self.__data.raw_sql("INSERT INTO credentials(key, secret) VALUES(?, ?)", key, secret)
                except tweepy.TweepError:
                    print("An error happened trying to set the access token, see info below.")
                    print(traceback.format_exc())
                    print("This is a critical error! Quitting now...")
                    sys.exit(-1)
            else:
                print("You didn't answer yes and without access token we cannot work, so...")
                print("Good bye old friend!")
                sys.exit(-1)
        else:
            self.__auth.set_access_token(key, secret)

        try:
          # All good so far, so we get the api object
          self.api = tweepy.API(self.__auth)
        except tweepy.TweepError:
            print("Uff, we were so close and suddenly an error, see below for more info...")
            print(traceback.format_exc)
            print("It's a critical error! So we wuitting now...\nGood bye!")
            sys.exit(-1)

    # I'm not thinking in use this methd, but is usefull for some folks
    # The reason why I don't wanna use it, it's because I don't like the data
    # I have to provide to twitter to allow me do this, like my phone number.
    # Yeah, I know, i'm very paranoid, but paranoid is good...most of the time.
    # So, this method have not been tested, but should work, right? right?! :=]
    def follow_all(self):
        """This method will follow everybody that follow you, always that your permissions for the app allow it.""""
        for follower in self.followers:
            if not self.api.exists_friendship(follower.screen_name, USER_NAME):
                follower.create_friendship(follower.screen_name)
                print("[+] You're now following {0}, check his/her profile\
                        at https://twitter.com/{0}".format(follower.scree_name))
           

    def process_all(self):
        """This is the method that retry the users from database and decide who is a new follower or an unfollower."""
        db_followers = self.__data. 


class GmailSender(object):
    pass




# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
