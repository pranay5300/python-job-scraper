# TS EAPCET Mock Exam FAQ

This FAQ documents the current mock-exam implementation, practical limits, known issues, and the fastest fixes.

## What does this module do?

The TS EAPCET module provides:

- 10 engineering-pattern mock papers
- 160 questions per paper
- section split of Mathematics (80), Physics (40), Chemistry (40)
- instant scoring and explanation review after submission
- optional solution-sheet email delivery
- PDF solution-sheet download from the results screen

## What are the main limitations right now?

### 1. It is built for light to moderate traffic, not large exam campaigns

The backend is a single Flask app with synchronous request handling for grading and SMTP email sending.

Practical impact:

- good for demos, pilot groups, and smaller practice batches
- not ideal for a large public exam event with many simultaneous submits and email sends

### 2. The exam timer is client-side

The countdown runs in the browser.

Practical impact:

- tab sleep or background throttling can affect the experience
- refresh/close can interrupt the current attempt
- there is no server-authoritative exam attempt record

### 3. Exam progress is not persisted

Answers, review flags, and remaining time live in frontend state only.

Practical impact:

- refreshing the page can lose the current attempt
- accidental navigation can wipe progress

### 4. Email delivery depends on external SMTP reliability

Solution-sheet email delivery depends on Render environment variables and the Gmail SMTP connection.

Practical impact:

- if SMTP is misconfigured or blocked, email delivery fails
- PDF download is the best fallback

### 5. Email sending is synchronous

The backend sends email during the request itself.

Practical impact:

- slow SMTP can delay the results flow
- multiple simultaneous email sends reduce effective concurrency

### 6. Results and PDF generation are fully client-side

The browser renders all 160 solutions and generates the PDF locally.

Practical impact:

- older phones or low-memory devices may feel slow
- PDF generation may briefly freeze the UI for large solution sets

### 7. Accessibility and mobile UX still need improvement

The UI works, but it is still desktop-first.

Practical impact:

- the palette is dense on phones
- keyboard/screen-reader support can be improved further

### 8. Email is currently required before starting a paper

Even though email delivery is optional after submit, the start flow currently requires an email address.

Practical impact:

- some users may see this as unnecessary friction

## How many users can take the exam at the same time?

This is only an estimate, not a guarantee.

Assuming the current code and a single small Render web service:

- **overview/paper loading**: low tens of concurrent active users is realistic
- **active exam usage without email sending**: roughly **10-30 concurrent users**
- **simultaneous email sends**: roughly **1-3 at a time** before latency becomes noticeable

If the service is underpowered, cold-starting, or running with limited CPU, practical capacity may drop to:

- **single digits to low teens** for active users

## Why is concurrency limited?

Main bottlenecks:

- single-instance backend deployment
- synchronous grading + response generation
- synchronous SMTP email sending
- no background job queue
- no persistent exam attempt store

## What are the most likely production issues?

### 1. Solution-sheet email fails

Symptoms:

- red banner after submit
- SMTP authentication or connection error

Quick fixes:

- verify backend Render env vars:
  - `SMTP_SENDER_EMAIL`
  - `SMTP_SENDER_PASSWORD`
  - `SMTP_HOST=smtp.gmail.com`
  - `SMTP_PORT=587`
- use a Gmail **App Password**, not the normal account password
- redeploy the backend after changing env vars
- use the PDF download fallback immediately

### 2. User loses progress on refresh or accidental leave

Symptoms:

- answers disappear after page refresh
- attempt resets

Quick fixes:

- add autosave to `localStorage`
- restore active paper state on reload
- add leave-confirmation and beforeunload warning

### 3. Timer feels inconsistent

Symptoms:

- browser sleep/background tab affects countdown

Quick fixes:

- store `startedAt` and `expiresAt`
- recompute remaining time from `Date.now()`
- optionally move timing authority to the backend

### 4. Email sending slows results page

Symptoms:

- submit completes slowly when user requests email

Quick fixes:

- move email sending to a background queue
- return results immediately and email asynchronously
- log email job status separately

### 5. Large submit/review load slows the app

Symptoms:

- slow results page
- laggy PDF generation on older devices

Quick fixes:

- paginate or virtualize solution rendering
- generate PDF in a Web Worker or on the server
- split score summary from full solutions

### 6. Public email endpoint abuse risk

Symptoms:

- SMTP quota issues
- sender account rate-limit or block

Quick fixes:

- add rate limiting per IP and per recipient
- add captcha or tokenized exam attempt IDs
- require server-side attempt records before emailing

### 7. Mobile UX feels cumbersome

Symptoms:

- excessive scrolling between question, timer, palette, and submit

Quick fixes:

- add sticky mobile controls
- move palette into a drawer/bottom sheet
- simplify the mobile exam layout

## What is the best fallback if email does not work?

Use one or more of these:

1. **On-page solution review**  
   Already available immediately after submit.

2. **Download solution sheet as PDF**  
   Already implemented and recommended as the primary fallback.

3. **Retry email later**  
   Add a retry button after SMTP issues are fixed.

4. **Tokenized result link**  
   Create a unique results URL instead of relying on email.

## Which fallback is recommended right now?

The best current setup is:

- show the full solution sheet in the results page
- allow **Download solution sheet PDF**
- keep email as a secondary convenience feature

## What are the quickest engineering upgrades?

### Highest-value quick fixes

1. persist exam state in `localStorage`
2. add rate limiting to the email endpoint
3. move SMTP to a background job
4. make email optional before exam start
5. improve mobile submit/timer controls

### Best scaling upgrades

1. run behind Gunicorn with stable worker settings
2. add Redis or database-backed job queue for emails
3. persist exam attempts/results in a database
4. add analytics and operational health checks

## Should this be used for a high-stakes real exam?

No.

This is currently a **practice/mock exam system**, not a hardened proctoring platform.

It is suitable for:

- practice tests
- coaching demos
- smaller internal or pilot student groups

It is not yet suitable for:

- high-stakes official exam delivery
- large simultaneous student cohorts
- audited exam security requirements

## Where should future improvements start?

Recommended order:

1. exam-state persistence
2. asynchronous email queue
3. rate limiting and anti-abuse controls
4. mobile UX improvements
5. accessibility improvements
6. backend attempt persistence and analytics
