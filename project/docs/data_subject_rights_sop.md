A — Public Data Subject Rights SOP

Filename: project/docs/data_subject_rights_sop.md
Audience: clients, schools, parents, adult users
Classification: PUBLIC
Tone: clear, practical, compliant**

HumanOS Tech — Data Subject Rights (DSR) Standard Operating Procedure

Version: v1.0
Last Updated: {{auto-fill on commit}}
Purpose:
To explain how HumanOS handles user, parent, and school requests for:

data export

data deletion

withdrawal of participation

corrections (future enhancement)

HumanOS complies with NDPR, GDPR, COPPA, and FERPA.

1. Who Can Make a Request

Adult users

Parents/guardians of minors

Authorized school administrators

Legal representatives (where applicable)

Requests must include:

participant ID

requester’s identity

type of request

For minors, HumanOS always requires parental or school authorization.

2. Available Rights
2.1 Right to Access (Export)

Users or parents may request a copy of:

tasks completed

behavioral metrics

timestamps

scoring logic applied

consent record

Export format: machine-readable JSON.

Response time: within 72 hours.

2.2 Right to Deletion (Erase)

Users or parents may request deletion of:

participant identifiers

session history

behavioral metrics

HumanOS performs:

anonymization (default)

full erasure when legally required

A confirmation report is issued after deletion.

2.3 Right to Withdraw

Users may request that HumanOS:

stop further data collection

deactivate active sessions

prevent future behavioral logging

Existing analytics may remain anonymized.

2.4 Right to Correction (Future Release)

HumanOS will add an interface allowing schools or users to correct incorrect demographic or metadata fields (non-sensitive).

3. How Requests Are Submitted

Requests may be submitted via:

school admin portal

HumanOS support email

parent verification portal (future feature)

4. How HumanOS Processes Requests

Verify identity

Verify guardianship or school authorization (if minor)

Locate participant records

Generate export or anonymize/delete data

Send confirmation

5. Response Times
Request Type	Response SLA
Data Export	≤ 72 hours
Data Deletion	≤ 72 hours
Withdrawal	≤ 48 hours
Minor-related requests	≤ 72 hours
6. Record Keeping

HumanOS maintains:

timestamp of request

requester identity

type of request

actions performed

confirmation report

No sensitive personal data is stored in the logs.

7. Exceptions

HumanOS may deny or limit requests where:

request is fraudulent

deletion compromises legal obligations

analytics already anonymized (irreversible)

END OF PUBLIC VERSION
