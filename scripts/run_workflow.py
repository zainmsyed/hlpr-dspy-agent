"""Simple runner to exercise a workflow."""
from src.workflows.email.categorizer import EmailCategorizer


def run_example():
    c = EmailCategorizer()
    result = c.run("Please pay this invoice for services.")
    print(result)

if __name__ == "__main__":
    run_example()
