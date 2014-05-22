#!/usr/bin/env python

import tweepy
import sqlite3 as lite
import subprocess
import os
import sys

DATABASE_NAME='nothing_to_see.db'

class db_layer(Object):
   def _init__(self, file_name):
      self.file_name = file_name
      self.con = None
      if self.file_name[-4:] != '.gpg':
          print "Well, it looks that the file named: %s is not a encripted sqlite db with gpg\nQuitting now!\n"
          sys.exit(1)
      try:
         if os.path.exists(self.file_name) and os.path.isfile(self.file_name):
            output = subprocess.Popen(['gpg',self.file_name])
            while output.poll() == None:
               output.stdout.readline()
            if output.returncode == 0:
                self.con = lite.connect(self.file_name)
            else:
                print "We got an error: %s\nQuitting now!\n" % output.communicate[1]         
                sys.exit(1)
         else: 
             try:
                 print "Creating database %s..." % self.file_name
                 self.con = lite.connect(self.file_name)
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
         cur = con.cursor()
         cur.executescript("""
                            CREATE TABLE tb_auth(Id INTEGER PRIMARY KEY AUTOINCREMENT, consumer_token TEXT,
                            consumer_secret TEXT, key TEXT, secret TEXT);
                            CREATE TABLE tb_followers(Id INTEGER PRIMARY KEY AUTOINCREMENT);
                            CREATE TABLE tb_unfollowers(Id INTEGER PRIMARY KEY);   
                           """)
         con.commit()
      except lite.Error, e:
         if con: 
            con.rollback()
         print "We got an error: %s" % e.args[0]
         sys.exit(1)
  
   def insert_auth(self,c_token,c_secret, key, secret):
       try:
          cur = con.cursor()
          cur.execute("INSERT INTO tb_auth(consumer_token, consumer_secret, 
               key, secret) VALUES(c_token, c_secret, key, secret)")
          con.commit()
        except lite.Error, e:
            if con:
                con.rollback()
          print "We got an error: %s" % e.args[0]
          sys.exit(1)

   def get_auth(self):
       try:
           con.row_factory = lite.Row
           cur = con.cursor()
           cur.execute("SELECT * FROM tb_auth LIMIT 1") # Because just must be one, anyway, right?
           con.commit()
           row = cur.fetchone()
           return row
       except Exception, e:
           print "We got an error: %s\nQuitting now\n" % str(e)
           sys.exit(1)

   def get_followers(self):  
       try:
           con.row_factory = lite.Row
           cur = con.cursor()
           cur.execute("SELECT * FROM tb_followers") 
           con.commit()
           row = cur.fetchall)
           return row
       except Exception, e:
           print "We got an error: %s\nQuitting now\n" % str(e)
           sys.exit(1)
   
   def get_followers(self):  
       try:
           con.row_factory = lite.Row
           cur = con.cursor()
           cur.execute("SELECT * FROM tb_unfollowers") 
           con.commit()
           row = cur.fetchall)
           return row
       except Exception, e:
           print "We got an error: %s\nQuitting now\n" % str(e)
           sys.exit(1)

  

def load_setting(setting_file):
    try:
        if os.path.exists(setting_file) and os.path.isfile(setting_file):
            output = subprocess.Popen(['gpg',setting_file])
            while output.poll() == None:
                output.stdout.readline()
            if output.returncode == 0:
                 



def set_auth():
    


