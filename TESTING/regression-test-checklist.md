# RetailMind AI — Regression Test Checklist

## A. Authentication

| ID | Test | Expected | Status |
|---|---|---|---|
| AUTH-01 | Login with valid email + OTP | Login successful | |
| AUTH-02 | Invalid OTP | Login rejected | |
| AUTH-03 | Logout | User returned to login | |
| AUTH-04 | Refresh after login | Session remains active | |
| AUTH-05 | Open protected page without login | User cannot access data | |

## B. Business Data Isolation

| ID | Test | Expected | Status |
|---|---|---|---|
| ISO-01 | Retailer A logs in | Only A data visible | |
| ISO-02 | Retailer B logs in | Only B data visible | |
| ISO-03 | Same invoice ID in same business | 409 duplicate | |
| ISO-04 | Same invoice ID in different business | Upload succeeds | |
| ISO-05 | Same customer phone in different businesses | Both allowed | |
| ISO-06 | Same product in different businesses | Both allowed | |
| ISO-07 | A requests B customer ID | B data not exposed | |
| ISO-08 | A uses Copilot to ask about B data | B data not exposed | |

## C. Invoice Upload

| ID | Test | Expected | Status |
|---|---|---|---|
| INV-01 | Upload valid invoice | Upload succeeds | |
| INV-02 | Upload same invoice again | 409 duplicate | |
| INV-03 | Upload invalid image | Proper error | |
| INV-04 | Upload non-invoice image | Proper error | |
| INV-05 | Invoice with multiple products | All items saved | |
| INV-06 | New customer invoice | Customer created | |
| INV-07 | Existing customer invoice | Existing customer reused | |
| INV-08 | New product | Product created | |
| INV-09 | Existing product | Existing product reused | |
| INV-10 | Invoice with credit | Credit amount correct | |

## D. Customer Profile

| ID | Test | Expected | Status |
|---|---|---|---|
| CUST-01 | Search customer by name | Correct customer appears | |
| CUST-02 | Search customer by phone | Correct customer appears | |
| CUST-03 | Select customer | Correct profile opens | |
| CUST-04 | Update profile | Changes saved | |
| CUST-05 | Search nonexistent customer | Empty result handled | |

## E. Prediction & Next Best Action

| ID | Test | Expected | Status |
|---|---|---|---|
| PRED-01 | Search customer | Customer appears | |
| PRED-02 | Select customer | Customer selected | |
| PRED-03 | Customer with <2 invoices | Not enough data message | |
| PRED-04 | Customer with sufficient history | Prediction generated | |
| PRED-05 | Next Best Action | Correct action displayed | |
| PRED-06 | WhatsApp message generated | Message displayed | |
| PRED-07 | Copy WhatsApp message | Clipboard works | |

## F. Dashboard

| ID | Test | Expected | Status |
|---|---|---|---|
| DASH-01 | Dashboard loads | No errors | |
| DASH-02 | Revenue | Correct value | |
| DASH-03 | Orders | Correct value | |
| DASH-04 | Customers | Correct value | |
| DASH-05 | Average order value | Correct value | |
| DASH-06 | Hero products | Correct products | |
| DASH-07 | Weak products | Correct products | |

## G. Credit / Udhaar

| ID | Test | Expected | Status |
|---|---|---|---|
| CREDIT-01 | Page loads | No errors | |
| CREDIT-02 | Outstanding credit | Correct value | |
| CREDIT-03 | Customer credit | Correct customer | |
| CREDIT-04 | Business isolation | Only current business data | |

## H. Product Bundles

| ID | Test | Expected | Status |
|---|---|---|---|
| BUNDLE-01 | Page loads | No errors | |
| BUNDLE-02 | Bundles displayed | Correct products | |
| BUNDLE-03 | Insufficient data | Proper empty state | |
| BUNDLE-04 | Business isolation | Only current business data | |

## I. Inventory Signals

| ID | Test | Expected | Status |
|---|---|---|---|
| INVNT-01 | Page loads | No errors | |
| INVNT-02 | Signals displayed | Correct products | |
| INVNT-03 | Empty inventory state | Proper message | |
| INVNT-04 | Business isolation | Only current business data | |

## J. Copilot

| ID | Test | Expected | Status |
|---|---|---|---|
| AI-01 | Copilot opens | UI works | |
| AI-02 | Ask revenue question | Correct answer | |
| AI-03 | Ask customer question | Correct answer | |
| AI-04 | Ask product question | Correct answer | |
| AI-05 | Follow-up question | Conversation context works | |
| AI-06 | Ask unrelated question | Graceful response | |
| AI-07 | Ask about another business | No other business data | |

## K. Production / Browser

| ID | Test | Expected | Status |
|---|---|---|---|
| PROD-01 | Desktop Chrome | Works | |
| PROD-02 | Mobile viewport | Works | |
| PROD-03 | Refresh dashboard | Works | |
| PROD-04 | Refresh prediction page | Works | |
| PROD-05 | Direct URL access | Works/auth protected | |
| PROD-06 | Network/API failure | Proper error shown | |
| PROD-07 | Loading states | Buttons behave correctly | |
| PROD-08 | Double-click upload | No duplicate invoice | |