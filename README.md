TwitterInspector...not sure if a good name
==========================================

This script is for know who unfollowed you on `Twitter`, it works like this:
At first run it will store all your friends in a `sqlite3` database, so when
it check again the database and your current friends on twitter, retrieved
using the twitter api(exactly with `tweepy` module for python), then if it finds
followers in the database but it does not find that(those) friend(s) in the
current friend lists obtained by the api then *it will know that person unfollow
you*.

I put a method in the script(which anyway should be modified a little) for follow
everyone who follow me(or you?), but I don't use this method in this version. The 
main reason why we don't use that method un this version is because in order to be
able to tweet, follow or unfollow we need to have permission for read-write access,
and for that I would have to provide twitter my numer phone, at the moment that's
something I don't really want to do...yeah, I'm kind of `paranoid`. Anyway, maybe I
will look a way for that later, probably using a "ghost phone number".

This application, *encrypt* and *decrypt* with `gnugp` the sqlite database anytime we
run the script, anyway.

Requirements
-------------
* You should have gnupg installed, because you encrypt the sqlite dabatase
* You need to have tweepy python module installed
* You need to have sqlite2 installed

Well, not to much to say, a simple script, but a little useful, other features should
be implemented soon, as sending report by mail and maybe provinding the ability to
tweet, follow and follow and all that to the app, anyway is for personal use. You can
get the `consumer key` and `consumer secret` registering the app at [Twitter Developer](https://apps.twitter.com/)
page. The application provide you a link for the `access token`.

Have fun!


