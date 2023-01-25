import lmtk

chat = lmtk.modes.raw_gpt.RawGPTMode()
def gpt(query):
    return "".join(chat.ask(query))

class Email:
    """
    Class to represent a single email
    """
    def __init__(self, from_address, to_address, subject, body):
        self.from_address = from_address
        self.to_address = to_address
        self.subject = subject
        self.body = body

    def __str__(self):
        return f"""
from: {self.from_address}
to: {self.to_address}
subject: {self.subject}
body: {self.body}"""

class EmailChain:
    """
    Class to represent a chain of emails
    This is basically just an array of emails with some helper functions!
    """
    def __init__(self):
        self.email_list = []

    def append(self, email):
        self.email_list.append(email)

    def __str__(self):
        return "\n================\n".join(self.email_list)

if __name__ == "__main__":
    test_email = Email("foo", "foo", "foo", "foo")
    print("test_email", test_email)

    print("TEST")
    # print(gpt("TEST"))