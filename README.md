Twitter followers inspector...or whatever
===================================================


A simple script to keep in a SQLite database our followers  of
our **Twitter** account, but more important it also register those
people that unfollowed us, those one it can determine by the database.

Also this script has a simple function for follow everybody who follow 
you and that you have not followed back yet. For use this function
you should register an app with read-write permission level.

Speaking about registering an app, you can do it going to <https://apps.twitter.com>,
you choose a name for the name, they give you a consumer key, consumer 
secret both you have to put it at the begging of the script file in
the variables with the same names all on upper case.

There in the *API Keys* section of your app on the Twitter app page you'll have
also access token and access token secret, which you could pass them
to the script when you run it and it ask for it if there are any records
on the credentials table on the database. 


SETTING
---------

You do this at the beginning of the script file, I prefered to keep this in the 
same script instead of making a settings file.

You change the database in the  **DB_NAME** variable, by default its name is
**tw_user**.

You can choose the directory where to store the database in the variable
**DIR** by default is **~/.follpector/**.

You specified your consumer tokens got from Twitter after registering an app
in the variables **CONSUMER_KEY** and **CONSUMER_SECRET** their name are self-descriptive
as the other ones.

If you want to get the new followers and more important the new unfollowers for mail
you do this in the variable **MAIL** which is a dictionary with keys: 'to' that is where to
send the mail, 'from' the address sender, 'subject' the subject the mail will have of course,
and 'passwd' the password of your address sender(the 'from').

It would be something like this:
  
     MAIL = {'to' : 'walterwhite@gmail.com', 'from' : 'pinkman@gmail.com', 'passwd' : 's3cr3t', 'subject' : '[Follpector] Your (un)followers report'}


USAGE
------

You just have to call the script like any other python script.

		python follpector.py

Or if you give execution permission with `chmod +x follpector.py`:

    ./follpector.py

For use the follow_all function call your script like this:

		python follpector.py --follow-all your_username

If the app your registered on Twitter to get the consumer access token that
you're using in the script has read-write permission then it will work, 
otherwise not, 'cause you need write permissions for that. Anyway I have not 
tested that function, I don't want to give my phone number to twitter.

If you don't have a database yet it will create it, if you don't
have access tokens in the `credentials` table the script will prompt asking
for it and will store it for later use of course.

You could if you want configure this script to be automatically executed
with crontab on GNU/Linux so you will get the report by email and it wouldn't
care to execute for you the script. You could redirect the standard output
and error to a file, something like this:

		python follpector.py --follow-all n3x07 > ~/home/alex/.follpector.log 2>&1 

It would redirect all output to that file, also it would rewrite it every time.
You could run the script automatically anytime you want using  *crontab*.

FURTHER CONSIDERATIONS
---------------------

Since the script store the `consumer key` and `consumer secret` and the email
password, if you use any to send the report by email, make sure you keep this
script when nobody else can see the source code or maybe take it off the read
permissions chmod -r follpector.py but let it the the execution permission +x.

The other thing is the database, I guess it's not problem that others see your followers
'cause they can see it anyway on Twitter, or your unfollowers anyway, it's not
sensitive information. But you don't want anyway to be able to see your access tokens
'cause they could use it for access your information. So try keep the SQLite
database out of the eyes of other people. Maybe you could encrypt it with `gnupg`
but you would have to decrypt it of course anytime you want it to use the script
or read it for yourself.

If you have gnupg install you can encrypt the database file or any file like this:

		gpg -c my_database.db

You would have to manually delete the .db file and just keep the new created `.db.gpg` one.

Then anytime you want it to decrypt it you run this command:
      
		gpg my_database.db.gpg

(I use the name my_database.db just as an example, could be any name. if you're reading this
you probably know all this, even more than me maybe, but I just write this just in case.)
		

CONTACT
--------

Feedback is appreciated. You can write me to `stackncode[at]gmail[dot]com` or find me on twiiter 
[@aljavi3r](https://twitter.com/aljavi3r).

