Who unfollowed you on Twitter?!
===================================================


A simple script to keep in a SQLite database our followers  of
our **Twitter** account, but more important it also register those
people that unfollowed us, which can be determine by comparing our
followers in database with those the Twitter API returns.

Also this script has a simple function for follow everybody who follow 
you and that you have not followed back yet. For use this function
you should register an app with read-write permission level.

Speaking about registering an app, you can do it going to <https://apps.twitter.com>,
you choose a name for the app, they give you a `consumer key` and `consumer secret` 
both you have to put it at the begging of the script file in
the variables with the same names all on upper case.

There in the *API Keys* section of your app on the Twitter app page you'll have
also `access token` and `access token secret`, which you could pass 
to the script when you run it and it ask for it if there aren't any records
on the credentials table on the database. 

### Requirements ###


 * Python 2.x.x or Python 3.x.x (yes, it works on both versions!).
 * tweepy, a twitter library python.
 
You can install `tweepy` with pip (or easy_install):
 
    pip install tweepy


### Settings ###


You do this at the beginning of the script file, I prefered to keep this in the 
same script instead of making a settings file.

You change the database in the  **DB_NAME** variable, by default its name is
**tw_users.db**.

    DB_NAME = "tw_users.db" # Database name

You can choose the directory where to store the database in the variable
**DIR** by default is **~/follpector/**.

    DIR = "follpector_db" # Directory where store the db

You specified the `consumer tokens` you got from Twitter after registering an app
in the variables **CONSUMER_KEY** and **CONSUMER_SECRET**, their name are self-descriptive
as the other ones.

    CONSUMER_KEY = "YOUR_CONSUMER_KEY"
    CONSUMER_SECRET = "YOUR_CONSUMR_SECRET"

If you want to get the new followers and more important the new unfollowers in your e-mail inbox
you do this by setting the variable **MAIL** which is a dictionary with keys:
	
* `to`: Sender e-mail.
* `from`: Recipient e-mail.
* `subject`: Subject of the mail.
* `passwd`: Password of the sender e-mail.

*Note: Only **gmail accounts** as the `sender e-mail` will work.*

     MAIL = {  
    			'to' : 'walterwhite@gmail.com', 
    			'from' : 'pinkman@gmail.com', 
    			'passwd' : 's3cr3t', 
    			'subject' : '[Follpector] Your (un)followers report' 
            }

### Usage ###


You just have to call the script like any other python script.

    python follpector.py

For using the `follow_all` function call your script like this:

    python follpector.py --follow-all your_username

If the app that you registered on Twitter (from which you got the `consumer access tokens` 
that you're using in the script) has `read-write` permissions then it will work, 
otherwise not, because it needs write permissions for that. Anyway I have not 
tested that function (I don't want to follow all those marketing and politics accounts
that follow me), but it should works.

If you don't have a database yet it will create it, if you don't have access 
tokens in the `credentials` table the script will ask you for it and will store 
it for later use.

You could if you want configure this script to be automatically executed
with `crontab` on GNU/Linux so you will get the report by email. 
You could redirect the standard output and error output to a file, 
something like this:

    python follpector.py --follow-all mrx > ~/home/mrx/.follpector.log 2>&1 

It would redirect all output to that file, also it would rewrite it every time.
You could run the script automatically anytime you want using *crontab*. [Here is
a How-To about crontab](http://www.unixgeeks.org/security/newbie/unix/cron-1.html)

Greetings,

A.J.

