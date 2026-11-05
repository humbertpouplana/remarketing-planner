# Parameters (there is no dataset)

This product has **no real data**: every number in `params.json` is a hypothesis to be replaced with the client's own measurements. Nothing here is anonymised data because nothing here is data.

| key | meaning |
|---|---|
| `defaults.floor` | share of the initial purchase intent that never decays |
| `defaults.fat` | fatigue: conversion divided by `1 + fat * touches in the previous 48 h` |
| `defaults.ue`, `defaults.us` | base unsubscribe rate per email / SMS |
| `defaults.ufat` | unsubscribe uplift per touch in the previous 48 h |
| `defaults.ctrE`, `defaults.ctrS` | click-through rates (for click estimates only) |
| `cohort` | leads per simulated cohort (10,000) |
| `incrementality` | share of conversions that would not have happened without the message |
| `cost_email`, `cost_sms` | EUR per message |
| `response_multiplier` | global multiplier on response rates (`kR`) |
| `funnel` | visitors and step-to-step rates used to size each segment (`pools`) |
| `sensitivity_shock` | relative shock used in the sensitivity analysis (0.25; UI labels assume 25%) |
| `types.<segment>` | `re`, `rs` (response of email / SMS), `tau` (decay in days), `V` (value of a conversion, EUR), `L0` (lifetime value per lead before the flow), `sched` (touch calendar: day, channel, message, destination) |
| `mods` | optional extra touches (post-sale reviews, insurance) |

Calibration route: replace `re`, `rs`, `tau`, `V`, `inc` with observed values from a holdout test (hold out 5-10% of each segment) and rerun `make all`.
