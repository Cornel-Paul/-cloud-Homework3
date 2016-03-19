from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import ndb
import datetime
import cgi


MAIN_PAGE_HTML = """\
<html>
  <body>
    <form action="/createAccount" method="post">
      First name:<br>
      <input type="text" name="firstname"><br>
      Last name:<br>
      <input type="text" name="lastname"><br>
      Email:<br>
      <input type="email" name="email">
      <div><input type="submit" value="Create Account"></div>
    </form>
  </body>
</html>
"""

class Account_DB(ndb.Model):
    """Models an individual Guestbook entry with content and date."""
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def exists_email(cls, email):
        query_result = cls.query(Account_DB.email == email)
        length = 0
        for result in query_result:
            length += 1
        if length == 0:
            return False
        return True



class MainPage(webapp.RequestHandler):
    def get(self):
        time = datetime.datetime.now()
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('<p>HThe time is: %s</p>' % str(time))
        self.response.out.write(MAIN_PAGE_HTML)

class ViewAccounts(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')
        ancestor_key = ndb.Key("Accounts", "Test")
        accounts = Account_DB.query()
        length = 0
        for account in accounts:
            length +=1

        self.response.out.write("<p>Length of accounts: "+ str(length) +"</p>")

        for account in accounts:
            first_name = cgi.escape(account.first_name)
            last_name =  cgi.escape(account.last_name)
            email = cgi.escape(account.email)
            date = account.date
            self.response.out.write("<p>First_name: " + first_name +
                                        " Last_name: " + last_name +
                                        " Email: " + email +
                                        " Date: " + str(date) +
                                    "</p>")


class Create_Account(webapp.RequestHandler):
    def post(self):
        first_name = cgi.escape(self.request.get("firstname"))
        last_name = cgi.escape(self.request.get("lastname"))
        email = cgi.escape(self.request.get("email"))

        print "in POst: " + email

        exists_email = Account_DB.exists_email(email)

        if exists_email:
            self.response.out.write("<p>Email already exists in our database: </p>")
        else:
            account = Account_DB(parent=ndb.Key("Accounts", "Test"),
                                 first_name=first_name,
                                 last_name=last_name,
                                 email=email
                                 )
            account.put()
            self.response.out.write("<p>Account created!</p>")



application = webapp.WSGIApplication([('/', MainPage),('/createAccount', Create_Account),("/accounts", ViewAccounts)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == '__main__':
    main()