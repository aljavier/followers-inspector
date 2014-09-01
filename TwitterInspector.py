#!/usr/bin/env python

import sqlite3 as lite
import sys
import traceback

# If tweepy is not install exit
try:
    import tweepy
except:
    print(sys.exc_info())
    print("Please install tweepy to use %s." % sys.argv[0])
    print("On mostly unix-like systems the easier way to install it is: pip install tweepy.")
    sys.exit(-1)


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

    def seed(script):
        """This method create the neede tables, and could populate also,the database."""
        raise NotImplementedError("You must implement this method!")



class SQLiteConnection(DbConnection):
    """Concrete class for the data persistent on database using SQLite."""
    def __init__(self,DB_NAME, DB_HOST="SQLite", USER=None, PASS=None):
        """The constructor, DB_NAME is the name of the sqlite database,
           neither DB_HOST, USER or PASS are needed here.
        """
        self.db_name = DB_NAME
        self.conn = None

    def connect(self):     
        "This method connect to an embedded SQLite database file."
        try:
            self.conn = lite.connect(self.db_name)
            # In order to get the objects always as dictionary we set this:
            self.conn.row_factory = lite.Row
        except Exception as e:
            print("We got an error here, printing more info below.")
            print traceback.format_exc()
            print("Quitting now...")
            sys.exit(-1)

    def get_all(self, table_name):
        """This method will return a list of dictionaries with all available records or an empty list."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM %s" % table_name)
            rows = cur.fetchall()
            return rows
        except Exception:
            print("We got an error here, printing more info below.")
            print traceback.format_exc()
        finally:
            cur.close()

    def get(self, id, table_name):
        """This method return a dictionary(record) from table_name with the specified id or None."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM " + table_name + " WHERE id = ?", id)
            row = cur.fetchone()
            return row
        except Exception:
            print("We got an error here, printing more info below.")
            print traceback.format_exc()
        finally:
            cur.close()

    def update(self, id, table_name, user_id, screen_name):
        """This method update the record(s) with the specified id."""
        try:
            cur = self.conn.cursor()
            if kwargs:
                # Look that we are expecting a dictionary with this keys and some values, obligatory.
                sql = "UPDATE " + table_name + " SET user_id = ?, scree_name = ? WHERE id = ?"
                cur.execute(sql, user_id, screen_name, id)
                self.conn.commit()
                print("%d records have been updated!" % cur.rowcount)
        except Exception:
            if self.conn:
               self.conn.rollback()
            print("We got an error here, printing more info below.")
            print traceback.format_exc()
        finally:
            cur.close()

    def delete(self, id, table_name):
        """This method remove record(s) from the database with the specified id."""
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM " + table_name + " WHERE id = ?", id)
            self.conn.commit()
        except Exception:
            if self.conn:
               self.conn.rollback()
            print("We got an error here, printing more info below.")
            print traceback.format_exc()
        finally:
            cur.close()

    def add(self, table_name, user_id, screen_name):
        """This method insert a new record in table_name with user_id and screen_name and return the id."""
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO " + table_name + " (user_id, screen_name) VALUES(user_id, screen_name)")
            self.conn.commit()
            return cur.lastrowid
        except Exception:
            if self.conn:
                self.conn.rollback()
            print("We got an error over here, more info below.")
            print traceback.format_exc()
        finally:
            cur.close()

    def seed(self,script):
        pass

    def __str_(self):
        return "Database connection for database named %s." % self.db_name
    

class TwitterInspector(object):
    pass


class MailSender(object):
    pass

class GmailSender(MailSender):
    pass




# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
