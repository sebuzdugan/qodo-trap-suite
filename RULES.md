# Team rules

These are the standards a reviewer, human or agent, is expected to enforce.
They are the kind of thing that usually lives in scattered instruction files
and drifts. Trap 2 breaks rule 1.

1. **Never log personally identifiable information.** Email addresses, phone
   numbers and full names must never reach log output. Log the opaque user id.
2. **Money is handled in minor units, and minor units are currency specific.**
   Never assume two decimal places. JPY and KRW have none.
3. **Authorisation defaults deny.** A user with no roles has no privileges.
   Never grant a role to make a legacy record work.
4. **Calendar arithmetic is wall clock arithmetic.** A day is not always 24
   hours. Never add 86400 seconds to move to "the same time tomorrow".
5. **Pagination bounds are half open.** `page_bounds` returns `(start, end)`
   where `end` is exclusive. Off-by-one here loses rows silently.
