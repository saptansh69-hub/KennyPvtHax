# KennyPvtHax — API Contracts & Integration Plan

## Auth (JWT, email/password OR telegram)
- POST /api/auth/signup { name, email?, telegram?, password } -> { token, user }
  - Requires at least one of email/telegram. Password hashed (pbkdf2_sha256).
- POST /api/auth/login { identifier (email or telegram), password } -> { token, user }
- GET /api/auth/me (Bearer) -> user

## Orders (order intake + key delivery record)
- POST /api/orders { telegram, email?, method (upi|stripe), currency (inr|usd), items:[{projectId,project,planId,plan,duration,inr,usd}] }
  - Optional Bearer -> links to user. Generates a license key per item (KENNY-XXXX-...). Saves order. status="paid" (mocked payment).
  - Returns order with keys.
- GET /api/orders/me (Bearer) -> user's orders/purchases

## Feedback
- POST /api/feedback { name, rating(1-5), message } (Bearer optional) -> feedback (auto-approved for demo)
- GET /api/feedback -> latest feedbacks (public)

## Frontend integration
- context/AuthContext.jsx: token in localStorage, me() on load, login/signup/logout
- Auth modal/page: signup+login (email or telegram)
- Account page (/account): shows profile + purchases (GET /orders/me)
- Checkout: POST /orders (mocked payment), shows generated key(s)
- Feedback section on Home: list from GET /feedback + submit form
- mock.js: keep static content (projects, pricing, features). telegram links updated.

## Mocked / pending
- Real UPI/Stripe payment gateways (frontend marks payment as mocked; order saved as paid).
- Real Telegram bot key delivery (key stored in DB; bot token to be added later).
- Real Telegram OAuth login (using username+password for now).
