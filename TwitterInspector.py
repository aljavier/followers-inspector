#!/usr/bin/env python

import sqlite3 as lite
import datetime
import sys
import os
import traceback

# If tweepy is not installed exit
try:
    import tweepy
except:
    print(sys.exc_info())
    print("Please install tweepy to use %s." % sys.argv[0])
    print("On mostly unix-like systems the easier way to install it is: pip install tweepy.")
    sys.exit(-1)

# The name for the SQLite database
DB_NAME = "tw_users.db"

# Can be get it registering an app at https://apps.twitter.com/
CONSUMER_KEY = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"

# Dictionary for the send_mail function, use this keys: 
# 'to' for recipient, 'from' for the gmail email use to 
# send the mail and 'passwd' for password.
# e.g. MAIL={'to' : 'admin@nsa.gob.us', 'subject' : 'Can't touch me!', 
#'from' : '0x3d@eviless.com', 'passwd' : 'highlysecure123' }
MAIL = {} 


class SQLiteConnection(object):
    """class for the data persistence on database  SQLite."""

    def __init__(self, db_name):
        """db_name is the name of the sqlite database, no others arguments needed here."""
        self.db_name = db_name
        self.conn = None
        self.__connect()

    def __connect(self):     
        "This method connect to an embedded SQLite database file."
        create_tables = False
        if not os.path.exists(self.db_name): create_tables = True
        try:
            self.conn = lite.connect(self.db_name)
            # In order to get the objects always as dictionary we set this:
            self.conn.row_factory = lite.Row
            if create_tables: self.seed()
        except lite.Error:
            print("We got an error here, printing more info below.")
            print(traceback.format_exc())
            print("Quitting now...")
            sys.exit(-1)

    def get_all(self, table_name="twitter_users", is_follower=None, LIMIT=None):
        """This method will return a list of dictionaries with all available records or an empty list."""
        cur = None
        try:
            cur = self.conn.cursor()
            sql = "SELECT * FROM " + table_name
            if is_follower is not None:
                sql = sql + " WHERE is_follower = " + str(is_follower) 
            if LIMIT is not None:
                # Rarely both filter will be use together, I guess
               sql = sql + " LIMIT " + str(LIMIT)  # In fact, LIMIT will be maybe never use here
            cur.execute(sql) 
            rows = cur.fetchall()
            return rows
        except lite.Error:
            print("We got an error here, printing more info below.")
            print(traceback.format_exc())
        finally:
            if cur: cur.close()

    def get(self, user_id=None, table_name="twitter_users"):
        """This method return a dictionary(record) from table_name with the specified user_id or None."""
        cur = None
        try:
            cur = self.conn.cursor()
            sql = "SELECT * FROM " + table_name  # It will be just like this if we quering the credentials table
            if user_id is not None:
                sql = sql + " WHERE user_id = %s" % str(user_id) 
            cur.execute(sql)
            row = cur.fetchone()
            return row
        except lite.Error:
            print("We got an error here, printing more info below.")
            print(traceback.format_exc())
        finally:
            if cur: cur.close()

    def update(self, user_id, screen_name, is_follower=None, table_name="twitter_users"):
        """This method update the record(s) with the specified user_id, just users table no credentials."""
        if is_follower is None:
            raise Exception("You must specified the value of is_follower!")
        cur = None
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
            if cur: cur.close()

    def delete(self, user_id, table_name="twitter_users"):
        """This method remove record(s) from the database with the specified user_id."""
        cur = None
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
            if cur: cur.close()

    def raw_sql(self, sql):
        """This method will run an sql sentence passed as argument, it does not inherit from DbConnection"""
        cur = None
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
            if cur: cur.close()

    def seed(self):
        """This method will create the tables needed for this app."""
        cur = None
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
    
    def __del__(self):
        if self.conn:
            self.conn.close()

# End of class SQLiteConnection            



class TwitterInspector(object):
    """The class that interact with the Twitter API throught tweepy library."""
   
    def __init__(self, db_name, consumer_key, consumer_secret, key=None, secret=None):
        self.__data = SQLiteConnection(db_name)
        self.followers = [] # Followers fetched from Twitter 
        self.db_followers = self.__data.get_all(is_follower=1) # Followers from db 
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
        credentials = self.__data.get(table_name="credentials") # We just need one, right? right?!
        if credentials is None:
            print("There aren't any credentials in the database!!!")
            answer = raw_input("Would do you like to add any now? >>> ")
            answer = answer.strip().lower()
            if answer == "yes" or answer == "y":
                try:
                    url = self.__auth.get_authorization_url()
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
         self.initialize()
         self.process_followers()
         self.process_unfollowers()

    
    def get_time_ago(self,  date):
        """This method returns *inteligently* the time ago.""" 
        # We obtain the time in seconds since this person is (un)following us according to our database
        seconds_ago = (datetime.datetime.now() - date).total_seconds()
        time_ago = None
        if seconds_ago < 60:
             time_ago = round(seconds_ago) + " seconds ago." 
        elif seconds_ago >= 60 and seconds_ago < 3600: 
             time_ago = round((seconds_ago / 60)) + " minutes ago." 
        elif seconds_ago >= 3600 and seconds_ago < (24*3600): # (24*3600) == the amount of seconds that a day has
             time_ago = round((seconds_ago / 60 / 60)) + " hours ago."
        else:
            time_ago = round((seconds_ago / 60 / 60 / 24)) + " days ago."
        return time_ago 


    def show_report(self):
        """This method will execute process_all  and show the report."""
        # Process and determine new unfollowers and followers
        self.process_all() 
        # Get new updated list of followers
        self.db_followers = self.__data.get_all(is_follower=1)
        # Get new updated list of unfollowers
        self.unfollowers = self.__data.get_all(is_follower=0)

        # Print followers
        print("=" * 80)
        print("SHOWING ALL FOLLOWERS IN OUR DATABASE RIGHT NOW - QUANTITY %d" % len(self.followers))
        print("=" * 80)
        for follower in self.db_followers:
            time_ago = self.get_time_ago(follower['date'])
            print("\t[+] {0} - https://twitter.com/{0}".format(follower['screen_name']))
        
        # Print unfollowers
        print("=" * 80)
        print("SHOWING ALL UNFOLLOWERS IN OUR DATABASE RIGHT NOW - QUANTITY %d" % len(self.unfollowers))
        print("=" * 80)
        for follower in self.db_followers:
            time_ago = self.get_time_ago(follower['date'])
            print("\t[-] {0} - https://twitter.com/{0} {1}".format(follower['screen_name'], time_ago))

# End of class TwitterInspector



# Function for send mail to a gmail account using MIME-Type
# Code snippet from http://stackoverflow.com/a/9179103
def send_mail(user, password, recipient, subject, message): 
    # Required imports, we do it here and not at the beginning because this function will be optionally
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMETEXT import MIMEText
    
    server = None

    # MIME data
    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message))
    
    # Server connection and sending email
    try:
       server = smtplib.SMTP('smtp.gmail.com', 587)
       server.ehlo() # Not really necesary but just in case
       server.starttls()
       server.ehlo()
       server.login(user, password)
       server.sendmail(user, recipient, msg.as_string())
    except:
        print("/!\ We got an error here, see the traceback below for more info!")
        print(traceback.format_exci())
    else:
        print("The message have been successfully sent to gmail adress %s!" % recipient)
    finally:
        if server: server.close()


if __name__ == '__main__':
    client = TwitterInspector(DB_NAME, CONSUMER_KEY, CONSUMER_SECRET) 
    client.show_report()
    if MAIL:
        message = "#####  " + len(client.db_followers) + " PEOPLE FOLLOW YOU RIGHT NOW  #####\n"
        for count, follower in enumerate(client.db_followers):
            time_ago = client.get_time_ago(follower['date'])
            message += "\t{0}. - https://twitter.com/{1} {2}".format(count+1, follower['screen_name'], time_ago)  
        
        message += "#####  " + len(client.db_followers) + " PEOPLE WHO UNFOLLOWED YOU IN SOME MOMENT  #####\n"
        for count, unfollower in enumerate(client.unfollowers):
            time_ago = client.get_time_ago(unfollower['date'])
            message += "\t{0}. - https://twitter.com/{1} {2}".format(count+1, unfollower['screen_name'], time_ago)

        message += "\n\n\###############     END OF REPORT     ###############"
        try:
           send_mail(MAIL['from'], MAIL['passwd'], MAIL['to'], MAIL['subject'], message)
        except:
            print("we got an error here, read below for more  info.")
            print(traceback.format_exc())
        
    
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
