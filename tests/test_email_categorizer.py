from src.workflows.email.categorizer import EmailCategorizer


def test_email_categorizer_finance(sample_email_text):
    c = EmailCategorizer()
    res = c.run(sample_email_text)
    assert res[0].label == "finance"
