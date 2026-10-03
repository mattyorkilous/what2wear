# 04 — Day page actions

**What to build:** The wearer can change a day from its Day page:
make it an Office or Home Day, wear a different Shirt, or switch today's
home Outerwear. Each write comes back to the page with a one-line
notice. This builds the POST → redirect → notice flow the other pages
reuse. See `.scratch/phone/spec.md`.

**Blocked by:** 03 — Today's Day page on PythonAnywhere.

**Status:** done

- [x] One button, "Make this an Office Day" / "Make this a Home Day",
      whichever the date isn't (`record_override`)
- [x] "Wear a different shirt": a `<select>` of that date's Closet's
      Shirts (`reset`)
- [x] "Switch to the jacket/sweater" only on today's page when today
      is a Home Day (`reset_outerwear`)
- [x] Each write answers 303 to its page with `?notice=<text>`, worded
      as the CLI's confirmations, owned by the web shell
- [x] The notice tells `recorded` from `already`
- [x] The State is written only when it changes
- [x] A refusal re-shows the page with the core message
- [x] No confirm steps
