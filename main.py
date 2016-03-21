from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import ndb
import datetime
import cgi

PHONE_NUMBER_LENGTH = 10

MAIN_PAGE_HTML = """\
<html>
  <body>
    <form action="/createAccount" method="post">
      First name:<br>
      <input type="text" name="firstname"><br>
      Last name:<br>
      <input type="text" name="lastname"><br>
      Email:<br>
      <input type="email" name="email"><br>
      Phone number:<br>
      <input type="text" name="phone"><br>
      Password:<br>
      <input type="password" name="password"><br>
      Retype password:<br>
      <input type="password" name="re_password"><br>
      <div><input type="submit" value="Create Account"></div>
    </form>
  </body>
</html>
"""

class Account_DB(ndb.Model):
    """Models an individual Account entry with content and date."""
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    password = ndb.StringProperty()
    email_validation = ndb.StringProperty()
    phone_validation = ndb.StringProperty()
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

    @classmethod
    def exists_phone(cls, phone):
        query_result = cls.query(Account_DB.phone == phone)
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
        self.response.out.write('<p>The time is: %s</p>' % str(time))
        self.response.out.write(MAIN_PAGE_HTML)


class ViewAccounts(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')
        ancestor_key = ndb.Key("Accounts2", "Test2")
        accounts = Account_DB.query()
        length = 0
        for account in accounts:
            length += 1

        self.response.out.write("<p>Length of accounts: " + str(length) + "</p>")

        for account in accounts:
            first_name = account.first_name
            last_name = account.last_name
            email = account.email
            # phone = account.phone
        #     date = account.date
        #     email_validation = account.email_validation
        #     phone_validation = account.phone_validation
            self.response.out.write("<p>First_name: " + first_name +
                                        " Last_name: " + last_name +
                                        " Email: " + email +
            #                             " Phone: " + phone +
        #                                 # " validation email: " + str(email_validation) +
        #                                 # " validation phone" + str(phone_validation) +
        #                                 # " Created date: " + str(date) +
                                    "</p>")


class CreateAccount(webapp.RequestHandler):

    def check_email(self, email):
        if len(email) < 1:
            self.response.out.write("<p>Email empty!</p>")
            return False

        exists_email = Account_DB.exists_email(email)
        if exists_email:
            self.response.out.write("<p>Email already exists in our database! </p>")
            return False
        return True

    def check_phone(self, phone):
        if len(phone) != PHONE_NUMBER_LENGTH:
            self.response.out.write("<p>Phone number must have 10 digits!</p>")
            return False

        exists_phone = Account_DB.exists_phone(phone)
        if exists_phone:
            self.response.out.write("<p>Phone number already exists in our database! </p>")
            return False
        return True


    def check_password(self, password, re_password):
        if password != re_password:
            self.response.out.write("<p>Password and Retype Password must be identically!</p>")
            return False
        return True

    def post(self):
        first_name = cgi.escape(self.request.get("firstname"))
        last_name = cgi.escape(self.request.get("lastname"))
        email = cgi.escape(self.request.get("email"))
        phone = cgi.escape(self.request.get("phone"))
        password = cgi.escape(self.request.get("password"))
        re_password = cgi.escape(self.request.get("re_password"))



        if self.check_email(email) and self.check_phone(phone) and self.check_password(password,re_password):
            #Aici ar trebui generate codurile si apoi trimis email-ul/sms-ul
            # email_validation = randint....
            # phone_validation = randint...
            account = Account_DB(parent=ndb.Key("Accounts2", "Test"),
                                 first_name=first_name,
                                 last_name=last_name,
                                 email=email,
                                 phone=phone,
                                 password=password,
                                 email_validation="False",
                                 phone_validation="False"
                                 )
            account.put()
            self.response.out.write("<p>Account created!</p>")





application = webapp.WSGIApplication([('/', MainPage),('/createAccount', CreateAccount),("/accounts", ViewAccounts)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == '__main__':
    main()