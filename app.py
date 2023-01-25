import openai

ENGINE = 'text-davinci-003'
MAX_TOKENS = 1000
TEMPERATURE = 0.0
def complete(prompt):
    completion = openai.Completion.create(
        engine=ENGINE,
        prompt=prompt,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        stop=['================'],
        stream=False,
    )

    # print(completion)
    return completion['choices'][0]['text']

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
        return f"""from: {self.from_address}
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

# 'client@foo.com' is the special client email address

company_definition = {
    'description': "Essays Inc. is a company that helps people write amazing essays",
    'team': {
        'CEO@essays.com': {
            'description': "He's the boss",
            'instructions': "Your goal is to get the client a great essay. Ask clarifying questions to make sure you understand exactly what the client wants. Then send ask essaywriter@essays.com to write the essay for you. Once you have it, send it back to the client."
        },
        'essaywriter@essays.com': {
            'description': "Writes essays at the direction of the CEO",
            'instructions': "Write an excellent essay based on the instructions from the CEO."
        },
    }
}

# Stuff that I could add:
# - CEO@essays.com -> researcher@essays.com: CEO sends it over to the Researcher who will research the topic, provide relevant context, and construct a proposed outline of the essay
# - researcher@essays.com -> drafter@essays.com: The Researcher will then the research and outline that over to the Drafter who will draft the essay. The Researcher makes sure to include the research and outline in her email. 
# - drafter@essays.com -> reviewer@essays.com: The Drafter will then send the drafted essay over to the Reviewer who will provide feedback. The drafter makes sure to include the drafted essay in his email.
# - reviewer@essays.com -> drafter@essays.com: The Reviewer will provide feedback *3 times* and the Drafter will improve the essay each time. These re-drafts will be significantly different and will add entire paragraphs to the essay to make it more and more complete, thorough, and interesting
# - drafter@essays.com -> editor@essays.com: The Drafter will then send the final draft over to the editor who will edit the essay
# - editor@essays.com -> CEO@essays.com: The Editor will then send the edited version back to the CEO who will make sure it is of the quality that the company is looking for
# - CEO@essays.com -> Client@essays.com: The CEO will then send the result back to the client""",


# TODO slice or summarize the email thread if its token count gets too high
def generate_prompt(email_chain):
    team = company_definition['team']
    # TODO remove your own address from the address book
    address_book = "\n".join([f"# {person} - {team[person]['description']}" for person in team])
    return f"""
Company Description: {company_definition['description']}
================
{email_chain}
================
# Instructions:
# You are {email_chain.last_recipient()}
# {company_definition['team'][email_chain.last_recipient()]['instructions']}
# Make sure to format your response as an email with a from: to: subject: and body:
# DO NOT USE ATTACHMENTS. Instead, include all relevant text in the body of the email.
# 
# Here is the company directory:
{address_book}

from: {email_chain.last_recipient()}"""

def parse_email(from_address, text):
    [_, remainder] = text.split("\nto: ")
    [to_address, remainder] = remainder.split("\nsubject: ")
    [subject, body] = remainder.split("\nbody:")

    return Email(from_address, to_address, subject, body)

CLIENT = "client@foo.com"

if __name__ == "__main__":
    starting_email = Email(CLIENT, "CEO@essays.com", "Essay Request", "Please write me an essay about the American Revolution")
    email_chain = EmailChain()
    email_chain.append(starting_email)

    while True:
        print("--------------------------------------")
        if email_chain.last_recipient() == CLIENT:
            client_input = input()
            new_email = Email(CLIENT, email_chain.last_sender(), email_chain[-1].subject, client_input)
        else:
            # If the latest email is addressed to anyone OTHER than the client...
            prompt = generate_prompt(email_chain)
            print("Prompt:\n", prompt)
            completion = complete(prompt)

            print("Completion:\n", completion)
            new_email = parse_email(email_chain.last_recipient(), completion)

        email_chain.append(new_email)