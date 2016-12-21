#!/usr/bin/env python                

# -*- encoding: utf-8 -*-                                                 
                                                                         

###########################################################################
#                                                                         #
# Coded by A. J. - stackncode[at]gmail[dot]com                            #
#               GPL v2 License                                            #
#                                                                         #
########################### REQUIREMENTS ##################################
#                                                                         #
#   * Python 2.x                                                          #
#   * tweepy - Install with pip: pip install tweepy                       #
#                                                                         #
#   Feedback is appreciated.                                              #
#                                                                         #
########################### DESCRIPTION ###################################
#                                                                         #
#    Script for keep a SQLite database with followers from a twitter      #
#    account and registered all those who unfollowed you. Optionally      #
#    send that information by email using a gmail account. Another        #
#    usefull feature is follow back everybody who follow you(no tested),  #
#    just if you specified this as an argument by commandline and have    #
#    read-write level permissions for your registered app on Twitter.     #
#                                                                         #
###########################################################################


import sqlite3 as lite
import datetime
import sys
import os
import traceback 
import smtplib

# import tweepy
try:
    import tweepy
except:
    print(sys.exc_info())
    print("Please install tweepy to use %s." % sys.argv[0])
    print("On mostly unix-like systems the easier way to install it is: pip install tweepy.")
    sys.exit(-1)

try: 
    # Python 2.x.x
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
except: 
    # Python 3.x.x
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

# Settings for the database location and name
DB_NAME = "tw_users.db" # Database name
DIR = "follpector_db" # Directory where store the db

try:
    DIR = os.path.join(os.path.expanduser("~"), DIR) # e.g. DIR = /home/user/.follpector/
except:
    print(traceback.format_exc())
    sys.exit(-1)

# Can be get it registering an app at https://apps.twitter.com/
# If any of these is wrong you'wll get an HTTP Error 401: Unathorized
CONSUMER_KEY = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMR_SECRET"

# Dictionary for the send_mail function, use this keys: 
# 'to' for recipient, 'from' for the gmail email use to 
# send the mail and 'passwd' for password.
# e.g. MAIL={'to' : 'admin@nsa.gob.us', 'subject' : 'Can't touch me!', 
#'from' : '0x3d@eviless.com', 'passwd' : 'highlysecure123' }
MAIL = {}

def get_user_input(message):
    """Method to get user input, valid for python 2.x and 3.x"""
    answer=''
    try: 
        answer = raw_input(message)
    except:
        answer = input(message)
    return answer
        

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

    def update(self, user_id, screen_name, is_follower, table_name="twitter_users"):
        """This method update the record(s) with the specified user_id, just users table no credentials."""
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if is_follower is None:
            raise Exception("You must specified the value of is_follower!")
        cur = None
        try:
            cur = self.conn.cursor()
            # I implied user_id never changed on twitter but that screen_name does
            sql = "UPDATE " + table_name + " SET screen_name = ?, date = ?, is_follower =? WHERE user_id = ?"
            cur.execute(sql, (screen_name, current_date, is_follower, user_id))
            self.conn.commit()
            print("%d record(s) have been updated!" % cur.rowcount)
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
        """This method will run an sql sentence passed as argument."""
        cur = None
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
        except lite.Error:
            if self.conn:
                self.conn.rollback()
            if cur: cur.close()
            print("We got an error over here, check the description below.")
            print(traceback.format_exc())

    def add(self, user_id, screen_name, is_follower, table_name="twitter_users"):
        """This method insert a new record in table_name with user_id and screen_name and return the id."""
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur = self.conn.cursor()
            sql = "INSERT INTO " + table_name + " ('user_id', 'screen_name', 'date','is_follower') VALUES(?, ?, ?, ?)"
            cur.execute(sql, (user_id, screen_name, current_date, is_follower))
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
   
    def __init__(self, db_name, consumer_key, consumer_secret):
        self.__data = SQLiteConnection(db_name)
        self.new_followers = [] 
        self.new_unfollowers = [] 
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
            key = secret = None
            print("There aren't any credentials in the database!!!")
            answer = get_user_input("Would do you like to add any now? >>> ")
            answer = answer.strip().lower()
            if answer == "yes" or answer == "y":
                answer = get_user_input("Do you have already your access token? >>> ")
                answer = answer.strip().lower()
                if answer == "yes" or answer == "y":
                    key = get_user_input("Please enter the access token key >>> ")
                    secret = get_user_input("Ok. Now please, enter the access token secret >>> ")
                    try:
                        self.__auth.set_access_token(key, secret)
                        self.__data.raw_sql("INSERT INTO credentials('key', 'secret') VALUES('%s', '%s')" % (key, secret))
                    except tweepy.TweepError:
                        print("Error trying to set access_token, see below for more info")
                        print(traceback.format_exc())
                        print("/!\ Critical error! Quitting now! /!\\")
                        sys.exit(-1)
                else: 
                    url = self.__auth.get_authorization_url()
                    print("Ok. Authorize the application in the following url and copy the code\n>>> %s" % url)
                    verifier = get_user_input("Please introduce the verifier code you got >>> ").strip()
                    try:
                       self.__auth.get_access_token(verifier) 
                       key = self.__auth.access_token.key
                       secret = self.__auth.access_token.secret
                       self.__data.raw_sql("INSERT INTO credentials('key', 'secret') VALUES('%s', '%s')" % (key, secret))
                    except tweepy.TweepError:
                        print("Error trying to get access_token, see below for more info")
                        print(traceback.format_exc())
                        print("/!\ Critical error! Quitting now! /!\\")
                        sys.exit(-1)    
                get_user_input("Access token stored on database! \nPlease, press ENTER to continue...")
            else:
                print("You didn't answer yes and without access token we cannot work, so...")
                print("Good bye old friend!")
                sys.exit(-1)
        else:
            try:
               self.__auth.set_access_token(credentials['key'], credentials['secret'])
            except tweepy.TweepError:
                print("Error setting the credentials, read more below.")
                print(traceback.format_exc())
                sys.exit(-1)


    def initialize(self):
        """Method for inicialize the api and."""
        try:
            # All good so far, so we get the api object and fetch the followers
            self.api = tweepy.API(self.__auth)
        except tweepy.TweepError:
            print("Uff, we were so close and suddenly an error, see below for more info...")
            print(traceback.format_exc)
            print("/!\ It's a critical error! So we quitting now...\nGood bye!")
            sys.exit(-1)

    # I'm not thinking in using this method, but is usefull for some folks
    # So, this method have not been tested, but should work, right? right?! :=]
    def follow_all(self, user_name):
        """This method will follow everybody that follow you(if you have read-write permissions."""
        followers = tweepy.Cursor(self.api.followers).items()
        for follower in followers:
            if not self.api.exists_friendship(follower.screen_name, user_name):
                follower.create_friendship(follower.screen_name)
                print("[+] You're now following {0} - https://twitter.com/{0}".format(follower.screen_name))


    def process_followers(self):
        """This is the method that process(determine) the new followers."""
        db_followers = self.__data.get_all(is_follower=1) 
        unfollowers = self.__data.get_all(is_follower=0)
        followers = tweepy.Cursor(self.api.followers).items()
        
        db_user_ids = [ str(u['user_id']) for u in db_followers ]    
        new_followers = [ f for f in followers if str(f.id) not in db_user_ids ]
        
        if not new_followers: return
        
        for f in new_followers:
            was_follower_before = (len([ u for u in unfollowers if str(u['user_id']) == str(f.id) and str(f.id) not in db_user_ids ]) > 0)
            self.new_followers.append(dict(user_id=f.id, screen_name=f.screen_name, was_follower=was_follower_before ))
            print("We have a new follower and his/her name is %s!" % f.screen_name)
            if was_follower_before:
                self.__data.update(f.id, f.screen_name, is_follower=1)
                print("...and he/she unfollowed us before but now is back!")
            else:
                id_new = self.__data.add(f.id, f.screen_name, is_follower=1)
                if id_new: 
                    print("Follower %s has succesfully been added to the database!" % (f.screen_name))
                else:
                    print("Couldn't add user %s, something wrong happened!" % (f.screen_name))


    def process_unfollowers(self):
        """Method for process (determine) new unfollowers."""
        db_followers = self.__data.get_all(is_follower=1) 
        followers = tweepy.Cursor(self.api.followers).items()
        
        tw_user_ids = [ str(u.id) for u in followers ]  
        unfollowers = [ u for u in db_followers if str(u['user_id']) not in tw_user_ids ] # Users who unfollowed us ;(
        
        if not unfollowers: return
        
        for u in unfollowers:
            self.new_unfollowers.append(dict(user_id = u.id, screen_name = u.screen_name))
            self.__data.update(u.user_id, u.screen_name, is_follower=0)
            
            print("Vaya! Someone named %s has unfollowed you!" % u.screen_name)
            print("This is the profile of the *individual* https://twitter.com/%s" % u.screen_name)
            
    
    def process_all(self):
         """Method for initialize and execute all (un)followers operations."""
         self.initialize()
         self.process_followers()
         self.process_unfollowers()

    def get_time_ago(self,  date):
        """This method returns *inteligently* the time ago.""" 
        # We obtain the time in seconds since this person is (un)following us according to our database
        date = datetime.datetime.now().strptime(date, "%Y-%m-%d %H:%M:%S")
        seconds_ago = (datetime.datetime.now() - date).total_seconds()
        time_ago = " on our db "
        if seconds_ago < 60:
             time_ago += str(round(seconds_ago)) + " seconds ago." 
        elif seconds_ago >= 60 and seconds_ago < 3600: 
             time_ago += str(round((seconds_ago / 60))) + " minutes ago." 
        elif seconds_ago >= 3600 and seconds_ago < (24*3600): # (24*3600) == the amount of seconds that a day has
             time_ago += str(round((seconds_ago / 60 / 60))) + " hours ago."
        else:
            time_ago += str(round((seconds_ago / 60 / 60 / 24))) + " days ago."
        return time_ago 


    def show_report(self, mail=False, **kwargs):
        """This method will execute process_all  and show the report."""
        db_followers = self.__data.get_all(is_follower=1) # Get new updated list of followers
        unfollowers = self.__data.get_all(is_follower=0) # Get new updated list of unfollowers
        send_by_mail = False
      
        if mail and kwargs.has_key('subject') and kwargs.has_key('to') \
                and kwargs.has_key('from') and kwargs.has_key('passwd'):
            send_by_mail = True

        message = "=" * 70
        message += "\n\t\t\t\t(UN)FOLLOWERS INFORMATION FROM DATABASE\n"
        message += "=" * 70
        message += "\nTotal of followers: %d" % len(self.__data.get_all(is_follower=1))
        message += "\nTotal of unfollowers: %d" % len(self.__data.get_all(is_follower=0))
        message += "\nTotal of new unfollowers: %d" % len(self.new_unfollowers) 
        message += "\nTotal of new followers: %d" % len(self.new_unfollowers) 
            
        print(message)
        
        if send_by_mail:
            self.send_mail(kwargs.get('from'), kwargs.get('passwd'),kwargs.get('to'), kwargs.get('subject'), message)


    # Function for sending mail to a gmail account using mime text
    # Code snippet from http://stackoverflow.com/a/9179103
    def send_mail(self, user, password, recipient, subject, message): 
        """Method for seding mail from a a gmail account."""
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
           print(traceback.format_exc())
        else:
           print("The message have been successfully sent to gmail adress %s!" % recipient)
        finally:
           if server: server.close()

# End of class TwitterInspector


def main():
    try:
        full_path = os.path.join(DIR, DB_NAME)
        
        if not os.path.exists(DIR): os.mkdir(DIR)
        
        client = TwitterInspector(full_path, CONSUMER_KEY, CONSUMER_SECRET) 

        if len(sys.argv) >= 2 and sys.argv[1] == "--follow-all":
            if len(sys.argv) > 2:
                client.follow_all(sys.argv[2]) # sys.argv[2] == twitter user_name
            else:
                print("You must provide your username to use the follow_all function!")
                print("e.g. %s --follow-all MegaMind" % sys.argv[0])
                sys.exit(-1)
                
        client.process_all() # Get new followers and determine unfollowers
        
        if MAIL: 
            client.show_report(mail=True, **MAIL) 
        else:
                client.show_report() 
    except tweepy.error.RateLimitError as error:
        print("It seems like we exceeded the amount of requests allowed from Twitter!")
        print(error)
        print("Try later in a couple of minutes!")
    except:
        print("Oh oh, something wrong happened!")
        print(traceback.format_exc())


if __name__ == '__main__':
    main()
        
    
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
