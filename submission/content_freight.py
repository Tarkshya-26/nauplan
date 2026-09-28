"""Slide text for SIH26006, v3: matches the working prototype (github.com/Tarkshya-26/nauplan).
Template pointers are copied word-for-word from the SIH 2026 template. Example money figures come from
a synthetic cargo programme with placeholder costs and are labelled as such. No em/en dashes in our copy."""

TEAM_NAME = "Vector66"
TEAM_ID = "183490"

TITLE_VALUES = [
    ("Problem Statement ID –", "SIH26006"),
    ("Problem Statement Title-", "Development of an Intelligent Freight Forecasting Model for Optimized Vessel "
                                 "Chartering and Bulk Cargo Procurement from overseas to East Coast of India"),
    ("Theme-", "Transportation & Logistics"),
    ("PS Category-", "Software"),
    ("Team ID-", TEAM_ID),
    ("Team Name (Registered on portal)", "- " + TEAM_NAME),
]

SUBTITLE = "NAUPLAN"
IDEA_TITLE = "IDEA TITLE: NAUPLAN"

B = lambda t: {"t": t, "b": True}


def item(*runs, **kw):
    return {"kind": "item", "runs": list(runs), **kw}


def pointer(text, **kw):
    return {"kind": "pointer", "text": text, **kw}


REFERENCES = [
    ("SIH 2026 problem statement SIH26006 (Ministry of Steel, SAIL)",
     "https://sih.gov.in/sih2026PS", "sih.gov.in/sih2026PS"),
    ("Baltic Exchange: Guide to Market Benchmarks v8.7 (Aug 2026), standard vessels and TCE method",
     "https://www.balticexchange.com/content/dam/balticexchange/consumer/documents/data-services/documentation/ocean-bulk-guides-policies/GMB.pdf",
     "balticexchange.com/.../ocean-bulk-guides-policies/GMB.pdf"),
    ("East Coast limits: Visakhapatnam Port Authority berth dimensions; Paradip Port Authority",
     "https://vpt.shipping.gov.in/admin_assets/uploads/1640237145_Berth%20Details.pdf",
     "vpt.shipping.gov.in/admin_assets/uploads/1640237145_Berth Details.pdf | paradipport.gov.in"),
    ("Adani Ports: Gangavaram BPTS (Oct 2024) and Dhamra BPTS (Oct 2025), berth parameters",
     "https://www.adaniports.com/-/media/Project/Ports/PortsAndTerminals/Quick-Links/Dhamra-BPTS_DPC_01-WEF-1st-Oct-2025.pdf",
     "cdn.gac.com/prod/docs/INDIA-Gangavaram_New-BPTS-Oct-2024.pdf | adaniports.com (Dhamra BPTS)"),
    ("Load ports: DBCT Terminal Information Booklet (Hay Point); Port of Gladstone Handbook",
     "https://dbct.squarespace.com/s/Terminal-Information-Booklet-Procedure.pdf",
     "dbct.squarespace.com/s/Terminal-Information-Booklet-Procedure.pdf | gpcl.com.au"),
    ("Passages: Torres Pilots draft limits; Suez Canal Authority; Danish Maritime Authority",
     "https://torrespilots.com.au/pilot-info/draft-restrictions/",
     "torrespilots.com.au/pilot-info/draft-restrictions | suezcanal.gov.eg | soefartsstyrelsen.dk"),
    ("Data feeds: FRED (Brent, USD/INR); World Bank Pink Sheet; Open-Meteo ERA5 marine; BDRY",
     "https://fred.stlouisfed.org/series/DEXINUS",
     "fred.stlouisfed.org | worldbank.org/en/research/commodity-markets | open-meteo.com"),
    ("Methods: searoute (Eurostat MARNET); HiGHS solver; LightGBM; statsmodels",
     "https://highs.dev", "github.com/genthalili/searoute-py | highs.dev | lightgbm.readthedocs.io"),
    ("Project repository, method notes and backtest report (Team Vector66)",
     "https://github.com/Tarkshya-26/nauplan", "github.com/Tarkshya-26/nauplan"),
]

SLIDES = {
    # ------------------------------------------------------------ slide 2: IDEA TITLE
    1: {
        "sizes": {"heading": 28, "pointer": 20, "item": 14.5, "pointer_before": 7},
        "geom": (None, 1.3, None, 5.6),
        "blocks": [
            {"kind": "heading", "text": "Proposed Solution (Describe your Idea/Solution/Prototype)", "after": 3},
            {"kind": "plain", "marL": 0.375, "size": 14.5, "after": 0,
             "runs": [B("NauPlan: "), "a working prototype that moves SAIL from daily spot fixtures to "
                                     "short / medium term multi-voyage contracts for East Coast coal imports."]},
            pointer("Detailed explanation of the proposed solution"),
            item(B("Freight forecast: "), "P10 / P50 / P90 ranges 1 to 26 weeks ahead, judged by walk-forward backtest"),
            item(B("Vessel-port fit: "), "Baltic standard ships vs draft, LOA, beam at 7 East Coast and 12 load ports"),
            item(B("Contract strategy: "), "optimiser picks spot, 3 / 6-month time charter or COA, and when to fix"),
            item(B("Idle control: "), "spare chartered days relet to the market; idle days tracked each month"),
            item(B("Early warnings: "), "sea state at all 7 ports, freight volatility, missing data flagged"),
            pointer("How it addresses the problem"),
            item("Replaces daily fixing with a contract plan tested on 200 freight scenarios"),
            item("Shows why each ship can or cannot call, and the cargo cut at each draft limit"),
            pointer("Innovation and uniqueness of the solution"),
            item("Plans on honest ranges and worst-case cost (CVaR), not on a single price guess"),
            item("Every port limit cites its source; Paradip Capesize cargo within 1% of a real call"),
        ],
    },
    # ------------------------------------------------------------ slide 3: TECHNICAL APPROACH
    2: {
        "sizes": {"pointer": 18, "item": 13, "pointer_before": 3},
        "geom": (None, 1.18, 12.0, 1.9),
        "blocks": [
            pointer("Technologies to be used (e.g. programming languages, frameworks, hardware)"),
            item(B("Data & ML: "), "Python, pandas, statsmodels, LightGBM; FRED, World Bank, Open-Meteo, BDRY feeds"),
            item(B("Ports & routes: "), "cited berth limits for 19 ports; searoute (MARNET) with deep-draft and avoid-Suez routes"),
            item(B("Optimisation: "), "two-stage stochastic MILP in PuLP with the HiGHS solver; CVaR risk term"),
            item(B("App: "), "FastAPI backend, React + Vite + d3 dashboard; 37 automated tests; code on GitHub"),
            pointer("Methodology and process for implementation (Flow Charts/Images/ working prototype)",
                    before=5),
        ],
    },
    # ------------------------------------------------------------ slide 4: FEASIBILITY AND VIABILITY
    3: {
        "sizes": {"pointer": 20, "item": 14, "pointer_before": 7},
        "geom": (None, 1.3, 12.0, 5.6),
        "blocks": [
            pointer("Analysis of the feasibility of the idea", before=0),
            item(B("Built: "), "data pipeline, cited limits for 19 ports, forecasting, optimiser, dashboard (37 tests)"),
            item(B("Checked: "), "Hay Point to Paradip Capesize, model 153,810 t vs 152,702 t actual call (6 Sep 2026)"),
            item(B("Tested: "), "forecasts backtested on 2021 to 2026 data; a 6-month plan solves in seconds"),
            item(B("Cost: "), "open-source stack on a laptop or one cloud VM; code public on GitHub"),
            item(B("Needs from SAIL: "), "import plan, fixture history, bunker and port costs (placeholders today)"),
            pointer("Potential challenges and risks"),
            item("1. Public data cannot predict freight direction (no model beat \"no change\" in testing)"),
            item("2. Per-class and period freight rates are licensed data"),
            item("3. Port limits change with tide and dredging; a few are not yet sourced"),
            item("4. Managers may not trust a black-box plan"),
            pointer("Strategies for overcoming these challenges"),
            item("1. Plan on ranges and scenarios; add the FFA forward curve with licensed data"),
            item("2. Baltic S8 route (Indonesia to East Coast India) or SAIL fixtures use the same pipeline"),
            item("3. Each limit stored with source and date; gaps shown on the dashboard"),
            item("4. Reasons for every ship choice; manager sets the risk weight; plan shown against all spot"),
        ],
    },
    # ------------------------------------------------------------ slide 5: IMPACT AND BENEFITS
    4: {
        "sizes": {"pointer": 21, "item": 15.5, "pointer_before": 14, "item_after": 4},
        "geom": (None, 1.3, 12.0, 5.6),
        "blocks": [
            pointer("Potential impact on the target audience", before=0),
            item(B("Chartering team: "), "a forward contract plan and ship choice with reasons, not daily market scanning"),
            item(B("Plant operations: "), "steadier coal arrivals, fewer stock-outs"),
            item(B("Port users: "), "ships sized to each port's draft, fewer waiting days"),
            item(B("Management: "), "expected and worst-case freight cost visible before committing"),
            pointer("Benefits of the solution (social, economic, environmental, etc.)"),
            item(B("Economic (example run*): "), "worst-10% programme cost $128.9M all spot vs $98.5M with the plan"),
            item(B("Operational: "), "spare chartered days relet, not idle; every decision auditable"),
            item(B("Environmental: "), "fewer ballast and waiting days means less fuel burnt"),
            {"kind": "plain", "marL": 0.75, "size": 12, "before": 8, "after": 0,
             "runs": ["*Synthetic 3.88 Mt, 6-month programme with placeholder costs and 200 freight scenarios; "
                      "real figures need SAIL data."]},
        ],
    },
    # ------------------------------------------------------------ slide 6: RESEARCH AND REFERENCES
    5: {
        "sizes": {"pointer": 20, "item": 13.5, "pointer_before": 0, "item_after": 0},
        "geom": (None, 1.3, 12.0, 5.6),
        "blocks": [pointer("Details / Links of the reference and research work", before=0)]
        + [b for (t, u, s) in REFERENCES for b in (
            {"kind": "item", "runs": [B(t)], "after": 0},
            {"kind": "plain", "marL": 0.75, "size": 11.5, "after": 5,
             "runs": [{"t": s, "u": True, "color": "0563C1", "link": u}]},
        )],
    },
}

FLOW = {
    "x": 0.75, "y": 3.12, "w": 11.85, "h": 1.2, "gap": 0.35, "head_h": 0.34, "font": 10.5, "head_font": 12,
    "stages": [
        {"head": "1. Data", "lines": ["Freight proxy, fuel, FX, coal prices",
                                     "Berth limits for 19 ports, cited",
                                     "Sea routes and sea state"]},
        {"head": "2. Forecast", "lines": ["6 models, walk-forward backtest",
                                         "P10 / P50 / P90, 1 to 26 weeks",
                                         "Volatility warning"]},
        {"head": "3. Optimise (MILP)", "lines": ["Ship fit and draft cargo cut",
                                                "Spot vs TC vs COA, entry month",
                                                "200 scenarios, cost + CVaR"]},
        {"head": "4. Decide", "lines": ["Dashboard: plan and timeline",
                                       "Why each ship fits or not",
                                       "Warnings; manager approves"]},
    ],
    "captions": [],
}

# Screenshots of the running prototype (slide 3). Crop boxes are in screenshot pixels.
PICTURES = [
    {"path": "dash_hero.png", "crop": (0, 0, 1440, 810), "x": 0.75, "y": 4.46, "h": 2.12,
     "caption": "Prototype: recommended plan on a chart of voyage tracks"},
    {"path": "dash_gauge.png", "crop": (0, 95, 1440, 675), "x": 4.72, "y": 4.46, "h": 2.12,
     "caption": "Draft gauge: which ship fits Hay Point to Paradip"},
]

STATUS_BOX = {
    "x": 10.18, "y": 4.46, "w": 2.42, "h": 2.12,
    "head": "Built and running",
    "lines": ["One-command data refresh",
              "19 ports, every limit cited",
              "Forecast backtest report",
              "Plan in seconds",
              "37 automated tests",
              "Public code on GitHub"],
}
