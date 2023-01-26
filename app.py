import openai
from tokenizers import Tokenizer

tokenizer = Tokenizer.from_pretrained("openai-gpt")

ENGINE = 'text-davinci-003'
MAX_TOKENS = 1000
TEMPERATURE = 0.3
def complete(prompt):
    completion = openai.Completion.create(
        engine=ENGINE,
        prompt=prompt,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        stop=['================'],
        stream=False,
    )

    return completion['choices'][0]['text']

class Email:
    """
    Class to represent a single email
    """
    def __init__(self, from_address, to_address, subject, body, attachments="[]"):
        self.from_address = from_address
        self.to_address = to_address
        self.subject = subject
        self.body = body
        self.attachments = attachments

    def __str__(self):
        # attachments_str = [] if len(self.attachments) is 0 else "".join(map(str, self.attachments))

        return f"""from: {self.from_address}
to: {self.to_address}
subject: {self.subject}
body: {self.body}
attachments: {self.attachments}"""

class EmailChain:
    """
    Class to represent a chain of emails
    This is basically just an array of emails with some helper functions!
    """
    def __init__(self):
        self.email_list = []

    def append(self, email):
        """
        Add an email to the EmailChain
        """
        self.email_list.append(email)

    def __getitem__(self, key):
        """
        Look up a particular email by index
        """
        return self.email_list[key]

    def last_recipient(self):
        return email_chain[-1].to_address

    def last_sender(self):
        return email_chain[-1].from_address

    def __str__(self):
        return "\n================\n".join(map(str, self.email_list))
        
company_definition = {
    'description': "Essays Inc. is a company that helps people write amazing essays",
    'team': {
        'sales@essays.com': {
            'description': "Sales",
            'instructions': "Your goal is to get the client a great essay. Ask clarifying questions to make sure you understand exactly what the client wants. Then send ask essaywriter@essays.com to write the essay for you."
        },
        'essaywriter@essays.com': {
            'description': "Essay Writer",
            'instructions': "Write an excellent essay based on the instructions from the client. Once you write an essay, send it over to editor@essays.com for editing."
        },
        'editor@essays.com': {
            'description': "Essay Editor",
            'instructions': "Edit essays that you are sent for grammer, clarity, and consistency. Then send it back to the client."
        }
    }
}

# TODO slice or summarize the email thread if its token count gets too high
def generate_prompt(email_chain):
    team = company_definition['team']
    # TODO remove your own address from the address book
    address_book = "\n".join([f"# {person} - {team[person]['description']}" for person in team])

    # Clip the email chain to fit in a certain token budget
    TOKENS_FOR_EMAIL_CHAIN = 2000
    # email_chain_clipped = tokenizer.decode(tokenizer.encode(str(email_chain)).ids[-TOKENS_FOR_EMAIL_CHAIN:])
    email_chain_clipped = str(email_chain)[-6000:]

    return f"""
Company Description: {company_definition['description']}
================
{email_chain_clipped}
================
# Instructions:
# You are {email_chain.last_recipient()}
# {company_definition['team'][email_chain.last_recipient()]['instructions']}
# Make sure to format your response as an email with a from: to: subject: body: and attachments:
# The attachments should be a list of dictionaries where each dictionary has "filename": and "full_text":
# 
# Here is the company directory:
{address_book}

from: {email_chain.last_recipient()}"""

def parse_email(from_address, text):
    [_, remainder] = text.split("\nto: ")
    [to_address, remainder] = remainder.split("\nsubject: ")
    [subject, remainder] = remainder.split("\nbody:")
    [body, attachments] = remainder.split("\nattachments:")

    return Email(from_address, to_address, subject, body, attachments)

CLIENT = "client@foo.com"

if __name__ == "__main__":
    # starting_email = Email(CLIENT, input("to: "), input("subject: "), input("body: "))
    starting_email = Email(CLIENT, "sales@essays.com", "Essay Request", "Please write me an essay about the Anatomy of the Eye.")
    email_chain = EmailChain()
    email_chain.append(starting_email)

    while True:
        print("--------------------------------------")
        if email_chain.last_recipient() == CLIENT:
            print(f"from: {CLIENT} | to: {email_chain.last_sender()} | subject: {email_chain[-1].subject}")
            new_email = Email(CLIENT, email_chain.last_sender(), email_chain[-1].subject, input("body: "))
        else:
            # If the latest email is addressed to anyone OTHER than the client...
            prompt = generate_prompt(email_chain)
            print(prompt)
            completion = complete(prompt)
            print(completion)
            new_email = parse_email(email_chain.last_recipient(), completion)

        email_chain.append(new_email)