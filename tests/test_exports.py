"""Test the csv/json export functionality."""
import binascii
import textwrap

import patches


def test_csv_export(webapp, monkeypatch):
    """Test CSV export"""
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )

    domain = 'a.com'
    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/search/{}/csv'.format(hexdomain))

    assert response.body.strip() == textwrap.dedent("""
        a.com,Original*,a.com,999.999.999.999,False
        a.com,Addition,aa.com,999.999.999.999,False
        a.com,Addition,ab.com,999.999.999.999,False
        a.com,Addition,ac.com,999.999.999.999,False
        a.com,Addition,ad.com,999.999.999.999,False
        a.com,Addition,ae.com,999.999.999.999,False
        a.com,Addition,af.com,999.999.999.999,False
        a.com,Addition,ag.com,999.999.999.999,False
        a.com,Addition,ah.com,999.999.999.999,False
        a.com,Addition,ai.com,999.999.999.999,False
        a.com,Addition,aj.com,999.999.999.999,False
        a.com,Addition,ak.com,999.999.999.999,False
        a.com,Addition,al.com,999.999.999.999,False
        a.com,Addition,am.com,999.999.999.999,False
        a.com,Addition,an.com,999.999.999.999,False
        a.com,Addition,ao.com,999.999.999.999,False
        a.com,Addition,ap.com,999.999.999.999,False
        a.com,Addition,aq.com,999.999.999.999,False
        a.com,Addition,ar.com,999.999.999.999,False
        a.com,Addition,as.com,999.999.999.999,False
        a.com,Addition,at.com,999.999.999.999,False
        a.com,Addition,au.com,999.999.999.999,False
        a.com,Addition,av.com,999.999.999.999,False
        a.com,Addition,aw.com,999.999.999.999,False
        a.com,Addition,ax.com,999.999.999.999,False
        a.com,Addition,ay.com,999.999.999.999,False
        a.com,Addition,az.com,999.999.999.999,False
        a.com,Bitsquatting,c.com,999.999.999.999,False
        a.com,Bitsquatting,e.com,999.999.999.999,False
        a.com,Bitsquatting,i.com,999.999.999.999,False
        a.com,Bitsquatting,q.com,999.999.999.999,False
        a.com,Replacement,1.com,999.999.999.999,False
        a.com,Replacement,s.com,999.999.999.999,False
        a.com,Replacement,2.com,999.999.999.999,False
        a.com,Replacement,w.com,999.999.999.999,False
        a.com,Replacement,y.com,999.999.999.999,False
        a.com,Replacement,z.com,999.999.999.999,False
        a.com,Vowel swap,u.com,999.999.999.999,False
        a.com,Vowel swap,o.com,999.999.999.999,False
        a.com,Various,wwa.com,999.999.999.999,False
        a.com,Various,wwwa.com,999.999.999.999,False
        a.com,Various,www-a.com,999.999.999.999,False
        a.com,Various,acom.com,999.999.999.999,False
    """).strip()


def test_json_export(webapp, monkeypatch):
    """Test JSON export"""
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )

    domain = 'a.com'
    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/search/{}/json'.format(hexdomain))

    assert response.json == {
        u'a.com': {
            u'fuzzy_domains': [
                {
                    u'domain-name': u'a.com',
                    u'fuzzer': u'Original*',
                    u'hex': u'612e636f6d',
                    u'resolution': {
                        u'error': False,
                        u'ip': u'999.999.999.999'
                    }
                },
                {
                    u'domain-name': u'a.co',
                    u'fuzzer': u'Pretend',
                    u'hex': u'612e636f',
                    u'resolution': {
                        u'error': False,
                        u'ip': u'999.999.999.999'
                    }
                }
            ]
        }
    }
