from src.workflows.email.categorizer import EmailCategorizer

c = EmailCategorizer()
print(c.run("Reminder: meeting scheduled for tomorrow"))
