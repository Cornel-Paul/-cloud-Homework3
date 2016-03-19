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
      <input type="text" name="lastname">
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
    def query_book(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(cls.date)


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
        accounts = Account_DB.query(Account_DB.first_name=="Vasile")
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
        self.response.out.write('<html><body>You wrote:<pre>')
        self.response.out.write(self.request.get('firstname'))
        self.response.out.write(self.request.get('lastname'))
        self.response.out.write('</pre></body></html>')

        account = Account_DB(parent=ndb.Key("Accounts", "Test"),
                             first_name=self.request.get("firstname"),
                             last_name=self.request.get("lastname"),
                             email="test@example.com"
                             )
        account.put()



application = webapp.WSGIApplication([('/', MainPage),('/createAccount', Create_Account),("/accounts", ViewAccounts)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == '__main__':
    main()