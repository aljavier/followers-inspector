#!/usr/bin/env python

import sqlite3 as lite
import datetime
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
CONSUMER_KEY = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"


class SQLiteConnection(object):
    """class for the data persistence on database  SQLite."""
    
    def __init__(self, db_name):
        """db_name is the name of the sqlite database, no others arguments needed here."""
        self.db_name = db_name
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

    def get_all(self, table_name="twitter_users", is_follower=None, LIMIT=None):
        """This method will return a list of dictionaries with all available records or an empty list."""
        try:
            cur = self.conn.cursor()
            sql = "SELECT * FROM " + table_name
            if is_follower is not None:
                sql = sql + " WHERE is_follower = " + is_follower 
            if LIMIT is not None:
                # Rarely both filter will be use together, I guess
               sql = sql + " LIMIT " + LIMIT  # In fact, LIMIT will be maybe never use here
            cur.execute(sql) 
            rows = cur.fetchall()
            return rows
        except lite.Error:
            print("We got an error here, printing more info below.")
            print(traceback.format_exc())
        finally:
            cur.close()

    def get(self, user_id=None, table_name="twitter_users"):
        """This method return a dictionary(record) from table_name with the specified user_id or None."""
        try:
            cur = self.conn.cursor()
            sql = "SELECT * FROM " + table_name  # It will be just like this if we quering the credentials table
            if user_id is not None:
                sql = sql + " WHERE user_id = ?" # This will be usefull for fetch  result from the twitter users table
            cur.execute( user_id)
            row = cur.fetchone()
            return row
        except lite.Error:
            print("We got an error here, printing more info below.")
            print(traceback.format_exc())
        finally:
            cur.close()

    def update(self, user_id, screen_name, is_follower=None, table_name="twitter_users"):
        """This method update the record(s) with the specified user_id, just users table no credentials."""
        if is_follower is None:
            raise Exception("You must specified the value of is_follower!")
        try:
            cur = self.conn.cursor()
            if kwargs:
                # I implied user_id never changed on twitter but that screen_name does
                sql = "UPDATE " + table_name + " SET screen_name = ?, date = ?, is_follower =? WHERE user_id = ?"
                cur.execute(sql, screen_name, datetime.now(), is_follower, user_id)
                self.conn.commit()
                print("%d records have been updated!" % cur.rowcount)
        except lite.Error:
            if self.conn:
               self.conn.rollback()
            print("We got an error here, printing more info below.")
            print(traceback.format_exc())
        finally:
            cur.close()

    def delete(self, user_id, table_name="twitter_users"):
        """This method remove record(s) from the database with the specified user_id."""
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM " + table_name + " WHERE user_id = ?", user_id)
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

    def add(self, user_id, screen_name, table_name="twitter_users"):
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
                     CREATE TABLE twitter_users(id integer primary key, user_id text, screen_name text, date text, is_follower integer);
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
        if self.conn:
            version = self.raw_sql("SELECT SQL_VERSION()")
            return "SQLite %s - using database name %s" % (version, self.db_name)
        else:
            return "SQLite object - database file name: %s" % self.db_name
    

class TwitterInspector(object):
    """The class that interact with the Twitter API throught tweepy library."""
   
    def __init__(self, db_name, consumer_key, consumer_secret, key=None, secret=None):
        self.__data = SQLiteConnection(db_name)
        self.followers = [] # Followers fetched from Twitter 
        self.db_followers = self.__data.get_all(is_followers=1) # Followers from db 
        self.unfollowers = self.__data.get_all(is_follower=0) # Unfollowers from db
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
        credentials = self.__data.get("credentials") # We just need one, right? right?!
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

    def initialize(self):
        """Method for inicialize the api and fetch the followers from twitter."""
        try:
            # All good so far, so we get the api object and fetch the followers
            self.api = tweepy.API(self.__auth)
            self.followers = tweepy.Cursor(self.api.followers).items()
        except tweepy.TweepError:
            print("Uff, we were so close and suddenly an error, see below for more info...")
            print(traceback.format_exc)
            print("/!\ It's a critical error! So we quitting now...\nGood bye!")
            sys.exit(-1)

    # I'm not thinking in use this methd, but is usefull for some folks
    # The reason why I don't wanna use it, it's because I don't like the data
    # I have to provide to twitter to allow me do this, like my phone number.
    # Yeah, I know, I'm very paranoid, but paranoid is good...most of the time.
    # So, this method have not been tested, but should work, right? right?! :=]
    def follow_all(self, user_name):
        """This method will follow everybody that follow you, always that your permissions for the app allow it."""
        for follower in self.followers:
            if not self.api.exists_friendship(follower.screen_name, user_name):
                follower.create_friendship(follower.screen_name)
                print("[+] You're now following {0}, check his/her profile\
                        at https://twitter.com/{0}".format(follower.screen_name))


    def process_followers(self):
        """This is the method that process(determine) the followers."""
        # Structural is kind of more suitable than functional in this case
        for tw in self.followers:
            for db in db_followers:
                # If tw is already a registered follower in our db we jump to check the others if any
                if tw.user_id == db['user_id']: break
            else:
                print("We have a new follower and his/her name is %s" % tw.screen_name)
                # We check if is someone who unfollowed us before and follow back again
                for un in self.unfollowers:
                    if tw.user_id == un['user_id']:
                       print("And he/she unfollowed us before but now is back!!!")
                       self.__data.update(tw.user_id, tw.screen_name, is_follower=1) # Update is_follower from False to True
                       break
                else: # It's a new follower, according to our db never has followed us
                    id_new = self.__data.add(tw.user_id, tw.screen_name)
                    if id_new: print("Follower %s has succesfully been added with id %d!" % (tw.screen_name, id_new))
        # End of this crazy *loopception*

   
    def process_unfollowers(self):
        """Method for process (determine) new unfollowers."""
        # We go structural again here as in the previous one, I don't see other way
        any_unfollower = False
        for db in self.db_followers:
            for tw in self.followers:
                # We jump to other element if any, 'cause this is not an unfollower
                if db['user_id'] == tw.user_id: break
            else: # Someone who unfollowed you here ;(
                self.__data.update(db['user_id'], db['screen_name'], is_follower=0) # That follower is now an unfollower on db
                if not any_unfollower: any_unfollower = True
                print("Vaya! Someone named %s has unfollowed you!", db['screen_name'])
                print("This is the profile of the *individual* https://twitter.com/%s" % db['user_id'])
        if any_unfollower:
            print("Awesome, nobody have unfollowed you!")
     
    def process_all(self):
         """Method for initialize and execute all (un)followers operations."""
         self

# Function for send mail to a gmail account using MIME-Type
# Code snippet from http://stackoverflow.com/a/9179103
def send_mail(user, password, recipient, subject, message): 
    # Required imports, we do it here and not at the beginning because this function will be optionally
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMETEXT import MIMEText
    
    # MIME data
    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = recipient
    msg'Subject'] = subject
    msg.attach(MIMEText(message))

    # Server connection and sending email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo() # Not really necesary but just in case
    server.starttls()
    server.ehlo()
    server.login(user, password)
    server.sendmail(user, recipient, msg.as_string())
    server.close()




# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
