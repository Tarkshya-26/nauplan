# Charter plan (example)

Generated 2026-09-28 by `uv run nauplan plan`. **The cargo programme is synthetic** (config/synthetic_programme.toml) and fuel, port, waiting and contract parameters are placeholders (config/assumptions.toml). Vessel specs are Baltic standard vessels; today's hire is converted from the Baltic indices (Baltic ticker read 2026-09-28). Treat money figures as illustrative.

200 hire scenarios over 6 months, resampled from real 4-week moves of the BDRY freight proxy and scaled so expected hire equals today's. CVaR = average cost of the worst 10% of scenarios.

## Vessel choice per route (today's hire)

### hay_point > paradip

| vessel_class | discharge_at | feasible | cargo_t | laden_draft_m | route | round_trip_days | spot_usd_per_t | why |
|---|---|---|---|---|---|---|---|---|
| Panamax/Kamsarmax | paradip | True | 79200 | 14.430 | deep_draft | 52.600 | 23.780 |  |
| Capesize | paradip | True | 153810 | 16.500 | deep_draft | 57.400 | 26.650 | draft 16.95 m at hay_point (tidal rule at 4.0 m tide (tide is a placeholder)) limits cargo; draft 16.50 m at paradip (published max draft) limits cargo |
| Supramax/Ultramax | paradip | True | 60960 | 13.420 | deep_draft | 51.300 | 29.030 |  |
| Handysize | paradip | False | 36672 | 10.540 |  |  |  | 38,200 DWT is below the 40,000 DWT minimum at hay_point |

### gladstone > vizag

| vessel_class | discharge_at | feasible | cargo_t | laden_draft_m | route | round_trip_days | spot_usd_per_t | why |
|---|---|---|---|---|---|---|---|---|
| Panamax/Kamsarmax | vizag | True | 79200 | 14.430 | deep_draft | 53.300 | 24.100 |  |
| Capesize | vizag | True | 161078 | 17.090 | deep_draft | 58.500 | 25.930 | draft 17.09 m at gladstone (water depth / 1.1 (placeholder)) limits cargo |
| Supramax/Ultramax | vizag | True | 60960 | 13.420 | deep_draft | 52.000 | 29.430 |  |
| Handysize | vizag | True | 36672 | 10.540 | shortest | 44.600 | 35.830 |  |

### hampton_roads > dhamra

| vessel_class | discharge_at | feasible | cargo_t | laden_draft_m | route | round_trip_days | spot_usd_per_t | why |
|---|---|---|---|---|---|---|---|---|
| Panamax/Kamsarmax | dhamra | True | 79200 | 14.430 | deep_draft | 82.500 | 37.760 |  |
| Capesize | dhamra | True | 138312 | 15.240 | deep_draft | 86.200 | 45.340 | draft 15.24 m at hampton_roads (published max draft) limits cargo |
| Supramax/Ultramax | dhamra | True | 60960 | 13.420 | deep_draft | 81.200 | 46.270 |  |
| Handysize | dhamra | True | 36672 | 10.540 | shortest | 79.600 | 64.640 |  |

### tanjung_bara > haldia

| vessel_class | discharge_at | feasible | cargo_t | laden_draft_m | route | round_trip_days | spot_usd_per_t | why |
|---|---|---|---|---|---|---|---|---|
| Panamax/Kamsarmax | sandheads | True | 79200 | 14.430 | deep_draft | 32.300 | 19.940 |  |
| Capesize | sandheads | True | 162420 | 17.200 | deep_draft | 39.900 | 22.610 | draft 17.20 m at tanjung_bara (published max draft) limits cargo |
| Supramax/Ultramax | sandheads | True | 60960 | 13.420 | deep_draft | 30.600 | 22.750 |  |
| Handysize | haldia | True | 29136 | 9.000 | shortest | 27.400 | 27.450 | draft 9.00 m at haldia (published max draft) limits cargo |
| Handysize | sandheads | True | 36672 | 10.540 | shortest | 28.300 | 28.200 |  |
| Supramax/Ultramax | haldia | False | 33833 | 9.000 |  |  |  | beam 32.24 m exceeds 32 m at haldia; draft 9.00 m at haldia (published max draft) limits cargo; draft limits cut cargo to 56% of intake |
| Panamax/Kamsarmax | haldia | False | 40918 | 9.000 |  |  |  | beam 32.25 m exceeds 32 m at haldia; draft 9.00 m at haldia (published max draft) limits cargo; draft limits cut cargo to 52% of intake |
| Capesize | haldia | False | 61560 | 9.000 |  |  |  | draft 17.20 m at tanjung_bara (published max draft) limits cargo; LOA 292 m exceeds 230 m at haldia; beam 45 m exceeds 32 m at haldia; draft 9.00 m at haldia (published max draft) limits cargo; draft limits cut cargo to 35% of intake |

## Strategies compared

| plan | expected_cost_usd_m | cvar_usd_m | p90_usd_m | std_usd_m | expected_usd_per_t |
|---|---|---|---|---|---|
| all spot (current practice) | 99.570 | 128.950 | 119.660 | 14.010 | 25.660 |
| optimised, expected cost only | 98.080 | 120.150 | 112.490 | 10.430 | 25.280 |
| optimised, risk-aware (weight 0.5) | 98.320 | 98.520 | 98.470 | 0.130 | 25.340 |

## Recommended plan: optimised, risk-aware (weight 0.5)

### Period time charters

| vessel_class | vessels | start | months | hire | hire_usd_day |
|---|---|---|---|---|---|
| Panamax/Kamsarmax | 1 | 2026-11 | 3 | market rate at start |  |
| Panamax/Kamsarmax | 14 | 2026-10 | 6 | fixed now at today's rate | 21663.000 |

### COA liftings

| route | vessel_class | months | month | tonnes | usd_per_t |
|---|---|---|---|---|---|
| hay_point > paradip | Panamax/Kamsarmax | 6 | 2026-12 | 35960.300 | 24.500 |
| hay_point > paradip | Panamax/Kamsarmax | 6 | 2027-01 | 32526.000 | 24.500 |
| hay_point > paradip | Panamax/Kamsarmax | 6 | 2027-03 | 101768.400 | 24.500 |

### Expected shipments by month and mode (tonnes)

| month | COA | spot | time charter |
|---|---|---|---|
| 2026-10 | 0.000 | 136562.000 | 553438.000 |
| 2026-11 | 0.000 | 0.000 | 540000.000 |
| 2026-12 | 35960.000 | 18831.000 | 615209.000 |
| 2027-01 | 32526.000 | 55788.000 | 601686.000 |
| 2027-02 | 0.000 | 900.000 | 579100.000 |
| 2027-03 | 101768.000 | 49110.000 | 559122.000 |

### Chartered fleet use (vessel-days, scenario average)

| vessel_class | month | vessels | vessel_days | voyage_days | relet_days | idle_days |
|---|---|---|---|---|---|---|
| Panamax/Kamsarmax | 2026-10 | 14 | 425.600 | 425.600 | 0.000 | 0.000 |
| Panamax/Kamsarmax | 2026-11 | 15 | 456.000 | 344.700 | 111.300 | 0.000 |
| Panamax/Kamsarmax | 2026-12 | 15 | 456.000 | 456.000 | 0.000 | 0.000 |
| Panamax/Kamsarmax | 2027-01 | 15 | 456.000 | 456.000 | 0.000 | 0.000 |
| Panamax/Kamsarmax | 2027-02 | 14 | 425.600 | 370.800 | 54.800 | 0.000 |
| Panamax/Kamsarmax | 2027-03 | 14 | 425.600 | 425.200 | 0.400 | 0.000 |

## Sensitivity: period hire premium vs today's spot

| period_premium | risk_weight | expected_usd_m | cvar_usd_m | tc_vessel_months | coa_kt |
|---|---|---|---|---|---|
| 0.000 | 0.000 | 98.080 | 120.150 | 72.000 | 0.000 |
| 0.000 | 0.500 | 98.320 | 98.520 | 87.000 | 170.250 |
| 0.050 | 0.000 | 99.570 | 128.950 | 0.000 | 0.000 |
| 0.050 | 0.500 | 100.940 | 100.940 | 66.000 | 823.470 |
| 0.100 | 0.000 | 99.570 | 128.950 | 0.000 | 0.000 |
| 0.100 | 0.500 | 102.040 | 102.040 | 0.000 | 3190.000 |
