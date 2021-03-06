"""Tests the email worker."""
import datetime

import dnstwister
import patches
import worker_email
import worker_deltas


def test_subscription_email_timing(capsys, monkeypatch):
    """Test that email subscriptions and delta reporting are in sync.

    A bug was found where, because signing up registers for delta reporting
    and the email is sent as soon as the report is generated, it is possible
    to send 2 emails between delta reports.
    """

    # Patch away
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )
    emailer = patches.NoEmailer()
    monkeypatch.setattr('worker_email.emailer', emailer)

    repository = dnstwister.repository

    # Settings
    domain = 'www.example.com'
    sub_id = '1234'
    email = 'a@b.zzzzzzzzzzz'

    # We start with an unregistered domain.
    assert not repository.is_domain_registered(domain)

    # Subscribe a new user.
    repository.subscribe_email(sub_id, email, domain)

    # Subscribing a user does not register the domain.
    assert not repository.is_domain_registered(domain)

    # Process the subscription.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    worker_email.process_sub(sub_id, sub_data)

    # We won't have sent any emails.
    assert emailer.sent_emails == []

    # But the domain is now registered for delta reporting.
    assert repository.is_domain_registered(domain)

    # So let's do a delta report.
    worker_deltas.process_domain(domain)

    # Process the subscription again.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    worker_email.process_sub(sub_id, sub_data)

    # And we've sent an email.
    assert len(emailer.sent_emails) == 1

    # Now we "let" a bit over 24 hours pass since the email was sent and the
    # report was updated.
    passed_time = datetime.timedelta(hours=24, minutes=1)
    repository.update_last_email_sub_sent_date(
        sub_id,
        datetime.datetime.now() - passed_time
    )
    delta_report = repository.get_delta_report(domain)
    repository.update_delta_report(
        domain, delta_report, datetime.datetime.now() - passed_time
    )

    # Now we run the email worker for the sub *before* the delta report.
    worker_email.process_sub(sub_id, sub_data)

    # We've not sent an extra email because it's more than 23 hours since the
    # last delta report.
    assert len(emailer.sent_emails) == 1

    # As soon as the delta report is ran again we can send another email.
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.222', False)
    )
    worker_deltas.process_domain(domain)
    worker_email.process_sub(sub_id, sub_data)
    assert len(emailer.sent_emails) == 2

    # And the emails are different.
    assert emailer.sent_emails[0] != emailer.sent_emails[1]
