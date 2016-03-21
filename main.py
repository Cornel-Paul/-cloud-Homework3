from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import ndb
import datetime
import cgi
from random import randint
from google.appengine.api import mail

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
    def email_validation(cls, email, code):
        #check daca codul de pe mail e ok
        return True

    @classmethod
    def phone_validation(cls, email, code):
        #check daca codul de pe telefon e ok
        return True

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

    def generateCode(self):
        return randint(1000,9999)

    def send_email(self, to_addr, subject, message):
        mail.send_mail(sender="paulacrismaru@gmail.com", to=to_addr, subject=subject, body=message)

    def post(self):
        first_name = cgi.escape(self.request.get("firstname"))
        last_name = cgi.escape(self.request.get("lastname"))
        email = cgi.escape(self.request.get("email"))
        phone = cgi.escape(self.request.get("phone"))
        password = cgi.escape(self.request.get("password"))
        re_password = cgi.escape(self.request.get("re_password"))



        if self.check_email(email) and self.check_phone(phone) and self.check_password(password,re_password):
            code_email = self.generateCode()
            message = "Enter the following code in email code field: " + `code_email`
            self.send_email(email, "Email Verification", message)
            code_phone = self.generateCode()
            message = "Enter the following code in phone code field: " + `code_phone`
            # trimite mesaj
            account = Account_DB(parent=ndb.Key("Accounts2", "Test"),
                                 first_name=first_name,
                                 last_name=last_name,
                                 email=email,
                                 phone=phone,
                                 password=password,
                                 email_validation=code_email,
                                 phone_validation="FALSE"
                                 )
            account.put()
            self.redirect("/checkCode")
            # self.response.out.write("<p>Account created!</p>")

class CheckCodes(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        page = """\
        <html>
          <body>
            <form action="/checkCodes" method="post">
              Phone code:<br>
              <input type="text" name="phone_code"><br>
              Mail code:<br>
              <input type="text" name="mail_code"><br>
              <div><input type="submit" value="Submit codes"></div>
            </form>
          </body>
        </html>
        """
        self.response.out.write(page)

    def post(self):
        p_code = cgi.escape(self.request.get("phone_code"))
        e_code = cgi.escape(self.request.get("mail_code"))
        email_validation = Account_DB.email_validation(email, e_code)
        if not email_validation:
            self.response.out.write("<p>Email validation failed</p>")
            # sterge din baza de date emailul si tot
            return False
        phone_validation = Account_DB.phone_validation(email, p_code)
        if not phone_validation:
            self.response.out.write("<p>Phone validation failed</p>")
            # sterge din baza de date emailul si tot
            return False
        self.response.out.write("<p>Account created!</p>")


application = webapp.WSGIApplication([('/', MainPage),('/createAccount', CreateAccount),("/accounts", ViewAccounts), ("/checkCode", CheckCodes)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
