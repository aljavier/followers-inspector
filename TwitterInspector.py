#!/usr/bin/env python

import sqlite3 as lite
import subprocess
import os
import sys

# if no tweepy installed we quit
try:
    import tweepy
except:
    print "Oh no, you don't have tweepy installed! Please install it with pip or easy_install!"
    print "Quitting now\n"
    sys.exit(1)

# Just putting this here
DB_NAME='canttouchthis.db.gpg'

class PersistenceLayer(object):
   def __init__(self, file_name):
      self.file_name = file_name
      self.con = None
      if self.file_name[-4:] != '.gpg':
          print "Well, it looks that the file named: %s is not a encripted sqlite db with gpg\nQuitting now!\n"
          sys.exit(1)
      try:
         if os.path.exists(self.file_name) and os.path.isfile(self.file_name):
            raw_input("Get ready to introduce the password for the .gpg file, before press ENTER please...")
            output = subprocess.Popen(['gpg',self.file_name], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            while output.poll() == None:
               output.stdout.readline()
            if output.returncode == 0:
                self.con = lite.connect(self.file_name[:-4])
            else:
                print "We got an error: %s\nQuitting now!\n" % output.communicate[1]         
                sys.exit(1)
         else: 
             try:
                 print "Creating database %s..." % self.file_name
                 self.con = lite.connect(self.file_name[:-4])
                 print "Creating tables tb_auth, tb_followers and tb_unfollowers\n"
                 self.__create_tables()
             except Exception, e:
                 print "We got an error: %s\nQuitting now!\n" % str(e)
                 sys.exit(1)
      except Exception, e:
          print "We got an error: %s\nQuitting now!\n" % str(e)
          sys.exit(1)
        
   def __create_tables(self):
      try:
         cur = self.con.cursor()
         cur.executescript("""
                            CREATE TABLE tb_auth(Id INTEGER PRIMARY KEY AUTOINCREMENT, consumer_token TEXT,
                            consumer_secret TEXT, key TEXT, secret TEXT);
                            CREATE TABLE tb_followers(Id INTEGER PRIMARY KEY, screen_name);
                            CREATE TABLE tb_unfollowers(Id INTEGER PRIMARY KEY, screen_name);   
                           """)
         self.con.commit()
      except lite.Error, e:
         if self.con: 
             self.con.rollback()
         print "We got an error: %s\Quitting now!\n" % e.args[0]
         sys.exit(1)
  
   def insert_auth(self, auth):
       try:
          cur = self.con.cursor()
          cur.execute("INSERT INTO tb_auth(consumer_token, consumer_secret, key, secret) VALUES(?,?,?,?)",auth)
          self.con.commit()
       except lite.Error, e:
          if self.con:
             self.con.rollback()
          print "We got an error: %si\nQuitting now!\n" % e.args[0]
          sys.exit(1)

   def get_auth(self):
       try:
           self.con.row_factory = lite.Row
           cur = self.con.cursor()
           cur.execute("SELECT * FROM tb_auth LIMIT 1") # Because just must be one, anyway, right?
           row = cur.fetchone()
           return row
       except Exception, e:
           print "We got an error: %s\nQuitting now\n" % str(e)
           sys.exit(1)

   def get_followers(self):  
       try:
           self.con.row_factory = lite.Row
           cur = self.con.cursor()
           cur.execute("SELECT * FROM tb_followers") 
           row = cur.fetchall()
           return row
       except Exception, e:
           print "We got an error: %s\nQuitting now\n" % str(e)
           sys.exit(1)

   def update_follower(self, follower):
        try:
            cur = self.con.cursor()
            cur.execute("UPDATE tb_followers SET screen_name = ? WHERE Id = ?", follower)
            self.con.commit()
        except Exception, e:
            if self.con:
                self.con.rollback()
            print "We got an error: %s\nQuitting now!\n" % str(e)
            sys.exit(1)

   def add_follower(self, follower):
        try:
            cur = self.con.cursor()
            cur.execute("INSERT INTO tb_followers VALUES(?, ?)",follower)
            self.con.commit()
        except Exception, e:
            if self.con:
                self.con.rollback()
            print "We got an error: %s\nQuitting now!\n" % str(e)
            sys.exit(1)
   
   def get_unfollowers(self):  
       try:
           #self.con.row_factory = lite.Row
           cur = self.con.cursor()
           cur.execute("SELECT * FROM tb_unfollowers") 
           row = cur.fetchall()
           return row
       except Exception, e:
           print "We got an error: %s\nQuitting now\n" % str(e)
           sys.exit(1)

   def add_unfollower(self, unfollower):
         try:
            cur = self.con.cursor()
            cur.execute("INSERT INTO tb_unfollowers VALUES(?,?)", unfollower) 
            self.con.commit()
            cur.execute("DELETE FROM tb_followers WHERE Id = ?", unfollower.id)
            self.con.commit()
         except Exception, e:
            if self.con:
                self.con.rollback()
            print "Wow wow We got an error: %s\nQuitting now\n" % str(e)
            sys.exit(1)

    
   def __secure(self):
       if os.path.exists(self.file_name[:-4]) and os.path.isfile(self.file_name[:-4]):
           try:
              raw_input("Get ready to introduce the password for store the updated ecnrypted sqlite db, before press ENTER please...")
              output = subprocess.Popen(['gpg','-c',self.file_name[:-4]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
              while output.poll() == None:
                  output.stdout.readline()
              os.remove(self.file_name[:-4])
           except Exception, e:
               print "Wow, an error has occured, please, run yourself 'gpg -c " + self.file_name[:-4] + "' and delete\
                      the plain text '"+ self.file_name + "' file, just keep the .gpg one\n"
               print "More about the error: %s" % str(e)
               sys.exit(1)         

   def __del__(self):
       if self.con:
           self.con.close()
       self.__secure();
# here end this class

class TweepyWrapper(object):
    def __init__(self):
        self.__data = PersistenceLayer(DB_NAME)
        self.__auth = None
        self.db_followers = []
        self.real_followers = []
        row = self.__data.get_auth()
        if row == None or (row) == 0:
            consumer_key = raw_input("Introduce your consumer_key >>> ")
            consumer_secret = raw_input("Introduce your consumer_secret >>>> ")
            consumer_key = consumer_key.strip()
            consumer_secret = consumer_secret.strip()
            self.__auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            try:
                redirect_url = self.__auth.get_authorization_url()
                print "You can get your access token at >> %s\n" % redirect_url
                verifier = raw_input("Introduce access token >>>> ")
                verifier = verifier.strip()
                self.__auth.get_access_token(verifier)
                auth = ((consumer_key,consumer_secret,self.__auth.access_token.key, self.__auth.access_token.secret))
                self.__data.insert_auth(auth)
            except tweepy.TweepError, e:
                print str(e)
                print "Error! Failed to get request token =(\nQuitting now!\n"
                sys.exit(1)
        else:
            self.__auth = tweepy.OAuthHandler(row[1], row[2])
            self.__auth.set_access_token(row[3], row[4])
        self.api = tweepy.API(self.__auth)
        self.__preload()
    
    def __preload(self):
        try:
           followers = tweepy.Cursor(self.api.followers).items()
           self.db_followers = self.__data.get_followers()
           for follower in followers:
               self.real_followers.append(follower)
        except tweepy.TweepError,e:
           print str(e)
           print "Quitting now!\n"
           sys.exit(1)

    # This method will no be use in this version(at least not by me), 'cause i would have to provide
    # twitter my number phone in order to obtain write access for this app and that
    # is something I don't want to do, but you can, totally.
    def follow_all(self):
        """ Follow everybody who follow me """
        for follower in self.real_followers:
            follower.follow()

    def get_unfollowers(self):
        unfollowers=[]
        db_unfollowers = self.__data.get_unfollowers()
        for unfollower in db_unfollowers:
            unfollowers.append(unfollower) 
        return unfollowers


    def process_followers(self, follow=False):
        aux_unfollowers = self.get_unfollowers()
        new_followers=[]
        new_unfollowers=[]
        if follow:
            self.follow_all()
        for follower in self.real_followers:
            is_new_follower = True
            for f in self.db_followers:
                if follower.id == f[0]:
                    is_new_follower= False
                    if follower.screen_name != f[1]:
                        t_follower = ((follower.id, follower.screen_name))
                        self.__data.update_follower(t_follower)
                    break
            if is_new_follower:
                t_follower = ((follower.id, follower.screen_name))
                self.__data.add_follower(t_follower)
                new_followers.append(follower)
        # Searching for new unfollowers
        for follower in self.db_followers:
           is_unfollower = True
           for f in self.real_followers:
               if follower['id'] == f.id:
                  is_unfollower = False
                  break
           # Then we check if is already in unfollowers table
           if is_unfollower:
              for x in aux_unfollowers:
                  if follower[0] == x[0]:
                     is_unfollower = False  # It's unfollower but already registred on db
                     break
           if is_unfollower:
               new_unfollowers.append((follower[0], follower[1]))
               self.__data.add_unfollower((follower[0], follower[1]))
        # Print resume by console
        unfollowers = self.__data.get_unfollowers()
        followers = self.__data.get_followers()
        print "Currently followers on twitter: {0}\nAmount of unfollowers registered on db: {1}\n".format(len(followers), len(unfollowers))
        if len(new_followers) > 0:
           print "New followers: "
           for follower in new_followers:
               print "[+] " + follower.screen_name + " ---- " + "https://twitter.com/" + follower.screen_name + "\n"
        else:
            print "You have 0 new followers registered in our db"
        if len(new_unfollowers) > 0:
            print "New unfollowers: "
            for unfollower in new_unfollowers:
                print "[-] " + unfollower.screen_name + " ---- " + "https://twitter.com/" + unfollower.screen_name + "\n"
        else:
            print "You have 0 new unfollowers since the last time we check it"

        if len(unfollowers) > 0:
            print " __-- All the people who unfollowed you(that we could know) --__"
            for unfollower in unfollowers:
                print "[-] " + unfollower[1] + " ---- " + "https://twitter.com/" + unfollower[1] + "\n"
        #if len(followers) > 0:
        #    print " __-- All the people who followe you --__"
        #    for follower in followers:
        #        print "[-] " + follower[1] + " ---- " + "https://twitter.com/ " + follower[1] + "\n"



if __name__ == '__main__':
    tw = TweepyWrapper()
    tw.process_followers()
