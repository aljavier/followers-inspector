Twitter followers inspector...or whatever
===================================================

A simple script to keep in a SQLite database our followers  of
our *Twitter* account, but more important it also register those
people that unfollowed us, the one it can determine by the database.

Also this script has a simle function for follow everybody who follow 
you and that you have not followed back yet. For use this function
you should register an app with read-write permission level.

Speaking about registering an app, you can do it going to <https://apps.twitter.com>,
you choose a name for the name, they give you a consumer key, consumer 
secret both you have to put it at the begging of the script file in
the variables with the same names all on upper case.

There in the *API Keys* of your app on the Twitter app page you'll have
also access token and access token secret, which you could pass them
to the script when you run it and it ask for it if there are any records
on the credentials table on the database. 

For use the follow_all function call your script like this:

		python follpector.py --follow-all your_username

If the app your registered on Twitter to get the consumer keys you choose
read-write permission then it will work, otherwise not, 'cause you write
permissions for that. Anyway I have not tested that function, I don't want
to give my phone number to twitter.

In order to the script send you the report by email, you have to set the 
`MAIL` variable at the beginnign of the script file, which is a dictionary,
there is more help about this on the script file.

You could if you want configure this script to be automatically executed
with crontab on GNU/Linux so you will get the report by email and it wouldn't
care to execute for yourself the script. You could redirect the standard output
and error to a file, something like this:

		python follpector.py --follow-all n3x07 > ~/home/alex/.follpector.log 2>&1 

It should redirect all output to that file, also it would rewrite it everytime.
You could run automatically anytime you want using  *crontab*.

Feedback is appreciated. You could write me to stackncode[at]gmail[dot]com

Anyway, I'm not really thinking anybody else more than me will ever
use this script x)
