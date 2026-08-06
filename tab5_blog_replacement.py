"""
Drop-in replacement for `tab5` in your app.py.

Replace the existing `with tab5:` block (from `with tab5:` down to the end of main())
with this code. Everything else in app.py stays the same.

Usage inside main():
    tab1, tab2, tab3, tab4, tab5 = st.tabs([...])
    ...
    with tab5:
        render_blog_tab()
"""

import streamlit as st
import streamlit.components.v1 as components

# ── helpers ──────────────────────────────────────────────────────────────────

def _img(path: str, caption: str = "", width: str = "100%"):
    """Try to show an image; show a styled placeholder on failure."""
    try:
        st.image(path, width="stretch")
        if caption:
            st.markdown(
                f"<p style='font-size:0.8rem;color:#9a8c78;text-align:center;"
                f"margin-top:-0.4rem;font-style:italic;'>{caption}</p>",
                unsafe_allow_html=True,
            )
    except Exception:
        st.markdown(
            f"<div style='background:#f0ebe0;border:1px dashed #c9b99a;"
            f"border-radius:6px;padding:1.5rem;text-align:center;"
            f"color:#9a8c78;font-size:0.85rem;margin:0.5rem 0;'>"
            f"📂 {path}"
            f"{'<br><em>' + caption + '</em>' if caption else ''}</div>",
            unsafe_allow_html=True,
        )


def _pull_quote(text: str):
    st.markdown(
        f"""
        <blockquote style="
            border-left: 5px solid #e8a838;
            background: linear-gradient(135deg,#fff8ee,#fdf4e3);
            padding: 1.4rem 1.8rem;
            margin: 2rem 0;
            border-radius: 0 10px 10px 0;
            font-family: 'Playfair Display', serif;
            font-size: 1.35rem;
            font-style: italic;
            color: #2e2b26;
            line-height: 1.5;
            box-shadow: 2px 4px 16px rgba(0,0,0,0.06);
        ">
        {text}
        </blockquote>
        """,
        unsafe_allow_html=True,
    )


def _chapter(number: str, title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="
            background: #1c1a17;
            color: #e8a838;
            border-radius: 10px;
            padding: 1.5rem 2rem;
            margin: 3rem 0 1.5rem 0;
            display:flex;
            align-items:baseline;
            gap:1.2rem;
        ">
            <span style="font-size:3rem;font-family:'Playfair Display',serif;
                         font-weight:900;opacity:0.35;line-height:1;">{number}</span>
            <div>
                <div style="font-family:'Playfair Display',serif;
                            font-size:1.5rem;font-weight:700;line-height:1.15;">{title}</div>
                {"<div style='font-size:0.85rem;color:#c9b99a;margin-top:0.25rem;letter-spacing:0.06em;text-transform:uppercase;'>" + subtitle + "</div>" if subtitle else ""}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _stat_row(stats: list):
    """stats = list of (value, label) tuples, 2–4 items."""
    cols = st.columns(len(stats))
    for col, (val, label) in zip(cols, stats):
        col.markdown(
            f"""
            <div style="background:#fff8ee;border:1px solid #e0d5c4;
                        border-left:4px solid #e8a838;border-radius:6px;
                        padding:1rem 1.25rem;text-align:center;">
                <div style="font-family:'Playfair Display',serif;font-size:2rem;
                            font-weight:700;color:#1c1a17;">{val}</div>
                <div style="font-size:0.72rem;text-transform:uppercase;
                            letter-spacing:0.08em;color:#7a6e5e;margin-top:0.2rem;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _sidebar_note(text: str):
    """An editorial aside / sidebar note."""
    st.markdown(
        f"""
        <div style="
            float:right;
            width:38%;
            background:#f0ebe0;
            border-left:3px solid #c9b99a;
            padding:0.9rem 1.1rem;
            margin:0 0 1rem 1.5rem;
            border-radius:0 6px 6px 0;
            font-size:0.85rem;
            color:#5a4e3c;
            line-height:1.65;
            font-style:italic;
        ">
        {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _divider():
    st.markdown(
        """<hr style="border:none;border-top:2px solid #e0d5c4;margin:2.5rem 0;">""",
        unsafe_allow_html=True,
    )


def _lede(text: str):
    """Large drop-cap opening paragraph."""
    st.markdown(
        f"""
        <p style="font-size:1.15rem;line-height:1.85;color:#2e2b26;
                  margin-bottom:1.2rem;">
        {text}
        </p>
        """,
        unsafe_allow_html=True,
    )


def _body(text: str):
    st.markdown(
        f"""<p style="font-size:1rem;line-height:1.8;color:#3a3530;
                      margin-bottom:1rem;">{text}</p>""",
        unsafe_allow_html=True,
    )


def _two_col_images(left_path, left_cap, right_path, right_cap):
    c1, c2 = st.columns(2)
    with c1:
        _img(left_path, left_cap)
    with c2:
        _img(right_path, right_cap)


def _callout_box(title: str, body: str, colour: str = "#e8a838"):
    st.markdown(
        f"""
        <div style="border:1.5px solid {colour};border-radius:8px;
                    padding:1.2rem 1.5rem;margin:1.5rem 0;
                    background:{'#fff8ee' if colour=='#e8a838' else '#f5f9ff'};">
            <div style="font-weight:700;font-size:0.9rem;color:{colour};
                        text-transform:uppercase;letter-spacing:0.07em;
                        margin-bottom:0.5rem;">{title}</div>
            <div style="font-size:0.95rem;color:#3a3530;line-height:1.7;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── main render function ──────────────────────────────────────────────────────

def render_blog_tab():

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #1c1a17 60%, #2e2008 100%);
            border-radius: 12px;
            padding: 3rem 2.5rem 2.5rem 2.5rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position:absolute;top:0;right:0;width:200px;height:200px;
                background:radial-gradient(circle,#e8a83830,transparent 70%);
                pointer-events:none;
            "></div>
            <p style="font-size:0.75rem;letter-spacing:0.15em;text-transform:uppercase;
                       color:#e8a838;margin-bottom:0.75rem;font-weight:600;">
                Long Read · Data Science Investigation
            </p>            <p style="font-family:'Playfair Display',serif;font-size:2.6rem;
                       font-weight:900;color:#c9b99;line-height:1.1;margin:0 0 1rem 0;">
                Rivers of Sand, Rivers of Crime
            </p>
            <p style="font-size:1.1rem;color:#c9b99a;line-height:1.65;
                       max-width:680px;margin:0;">
                How India's housing boom quietly supercharged an illegal extraction industry ,
                and what seven data sources, four causal identification strategies, and 99,000
                river sensor readings tell us about the true cost of cheap concrete.
            </p>
            <div style="margin-top:1.5rem;display:flex;gap:1.5rem;flex-wrap:wrap;">
                <span style="font-size:0.8rem;color:#7a6e5e;">
                    ✍ Urvashi Balasubramaniam &amp; Manya Garg
                </span>
                <span style="font-size:0.8rem;color:#7a6e5e;">
                    📅 CS3340 Final Report · April 2026
                </span>
                <span style="font-size:0.8rem;color:#7a6e5e;">
                    🗂 2,212 incidents · 32 states · 2001–2026
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Table of Contents ─────────────────────────────────────────────────────
    with st.expander("📖 Table of Contents , click to navigate", expanded=False):
        st.markdown("""
**Part I , The Problem**
1. The invisible resource war  
2. What nobody is counting  
3. Five ways sand mining kills  

**Part II , The Data**
4. Seven sources, one picture  
5. Where the mafia lives: geography of extraction  
6. The river corridors  

**Part III , The Policy Trigger**
7. PMAY-U and the 14.7× surge  
8. Four ways to prove causation  
9. The spatial mismatch paradox  

**Part IV , Who Bears the Cost**
10. Poverty, enforcement, and the marginal worker  
11. The groundwater signal  
12. Conductivity doesn't lie: Ganga sensor evidence  

**Part V , What Comes Next**
13. NLP finds the mafia's fingerprints  
14. The enforcement gap map  
15. Six policy levers that could work  
        """)

    _divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # PART I , THE PROBLEM
    # ═══════════════════════════════════════════════════════════════════════════

    st.markdown(
        """<p style="font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;
                      color:#e8a838;font-weight:700;margin-bottom:0.2rem;">
        Part I</p>
        <h2 style="font-family:'Playfair Display',serif;font-size:2rem;
                    color:#1c1a17;margin:0 0 1.5rem 0;">The Problem Nobody Sees</h2>""",
        unsafe_allow_html=True,
    )

    _chapter("01", "The Invisible Resource War", "Sand as the world's most contested secret commodity")

    _lede(
        "Pick up any pebble from a Delhi construction site. Look at the concrete pillars of an "
        "overpass in Patna, the tiles of a new apartment in Bhopal, the bricks being laid in a "
        "government housing colony in UP. They all share an ingredient so ubiquitous it has "
        "become invisible: <strong>sand.</strong>"
    )

    _body(
        "Sand is the second-most exploited natural resource on Earth after water. The United Nations "
        "Environment Programme estimates global extraction at over <strong>50 billion tonnes per year</strong> , "
        "a volume so large it dwarfs the planet's natural replenishment cycle. Rivers deposit sand over "
        "centuries. We extract it in seasons."
    )

    _pull_quote(
        '"Sand is the second most exploited resource in the world, after water. '
        'If you remove sand from the river, you are digging your own grave." , Dinesh Kumar Mishra'
    )

    _body(
        "India sits at the centre of this pressure. It is one of the fastest-urbanising nations on "
        "Earth, with over 400 million people expected to move to cities by 2050. Every new road, "
        "bridge, school, and apartment block requires sand , and vast quantities of it. "
        "The government's own housing scheme, PMAY-U (Pradhan Mantri Awas Yojana-Urban), has "
        "sanctioned nearly <strong>12 million new homes</strong> since 2015 alone. That is 12 million "
        "new reasons to dig up a river."
    )

    _stat_row([
        ("50B+", "tonnes of sand extracted globally each year"),
        ("12M", "houses sanctioned under PMAY-U since 2015"),
        ("14.7×", "surge in documented mining incidents post-2015"),
        ("2,212", "verified mining records in this study"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    _chapter("02", "What Nobody Is Counting", "The data fragmentation that protects the Sand Mafia")

    _body(
        "Here is the first paradox of illegal sand mining in India: <strong>there is no official count.</strong> "
        "Unlike murder, theft, or drug trafficking, which are logged by the NCRB and published annually, "
        "illegal sand extraction exists in a statistical fog. Incidents surface in journalistic archives, "
        "NGT court filings, citizen field reports, environmental sensor streams, and government district "
        "surveys , scattered across systems that were never designed to talk to each other."
    )

    _sidebar_note(
        "<strong>What is the Sand Mafia?</strong><br>"
        "An informal network of criminal groups that extract, transport, and sell "
        "sand illegally from rivers, floodplains, and coastal areas. Between 2019 "
        "and 2023, documented incidents include the deaths of government officials, "
        "journalists, and civilians who tried to report or obstruct mining."
    )

    _body(
        "This fragmentation is not accidental. <strong>The Sand Mafia thrives in informational darkness.</strong> "
        "When there is no official count of incidents, there is no official accountability for failing "
        "to address them. The absence of data is itself a governance failure , and a structural "
        "enabler of impunity."
    )

    _body(
        "This report's defining accomplishment is assembling a unified analytical framework from "
        "<strong>seven heterogeneous data sources</strong>: India Sand Watch (2,212 incident records), "
        "the National Data and Analytics Platform (NDAP), the Water Resources Information System "
        "(7,190 groundwater stations), CPCB air quality data, PMAY-U administrative records, "
        "Census 2011 socioeconomic tables, and two real-time water-quality sensors at Prayagraj "
        "capturing 99,000 one-minute readings."
    )

    # _callout_box(
    #     "The Data Challenge in One Sentence",
    #     "State name variants alone required a 47-entry correction dictionary, Unicode normalization, "
    #     "punctuation stripping, and lowercase conversion before any dataset could be merged with any other.",
    # )

    _chapter("03", "Five Ways Sand Mining Kills", "The cascade of damage from river to community")

    _body(
        "Before the numbers, the human stakes. Why does it matter if someone scoops sand from a "
        "riverbed? The answer cascades:"
    )

    tab_eco, tab_water, tab_air, tab_violence, tab_inequality = st.tabs([
        "🌊 Ecological", "💧 Groundwater", "💨 Air Quality", "⚔️ Violence", "⚖️ Inequality"
    ])

    with tab_eco:
        st.markdown("""
**Rivers are not passive containers of water.** Sand and gravel serve as habitat for thousands of
species, anchor riverbanks, regulate streamflow, and filter groundwater. When sand is removed
faster than deposition can replace it , a process called *riverbed incision* , channels deepen,
banks become unstable, and a cascade follows:

- Bridges lose their foundations
- Floodplains no longer receive seasonal sediment
- The water table drops as the riverbed's natural sponge layer is removed
- Small tributaries dry up
- Aquatic biodiversity collapses

Studies of heavily mined rivers in India have documented all of these outcomes. The Chambal,
the Mahananda, the Narmada , each tells the same story.
        """)

    with tab_water:
        st.markdown("""
**Sand mining disturbs the mineral-rich sediment layer of riverbeds,** releasing dissolved solids
including heavy metals into the water column. Total Dissolved Solids (TDS) , the combined content
of all inorganic and organic substances dissolved in water , are the standard proxy.

This study finds that **100% of Bihar's groundwater monitoring stations** show elevated TDS
near mining sites. In West Bengal, the figure is **78%**. In Bihar's alluvial Gangetic geology,
the water table sits directly beneath the mined riverbed. Disturb one; contaminate the other.
        """)
        _img(
            "sangam_ganga_figures/fig_gwr_coefficients.png",
            "GWR local coefficients: blue = proximity to mining correlates with higher dissolved solids. "
            "The signal is strongest along the Gangetic corridor."
        )

    with tab_air:
        st.markdown("""
**The transport of sand by truck, tractor, and barge** generates large quantities of coarse
particulate matter. PM10 and PM2.5 , particles of 10 and 2.5 micrometers or less ,
have been linked to respiratory disease, cardiovascular damage, and premature death.

In this study, **PM10 is the strongest state-level environmental predictor of mining intensity**,
outperforming PM2.5, crime rates, and socioeconomic variables in OLS regression. The dust
trail of a sand truck is, literally, the evidence.
        """)

    with tab_violence:
        st.markdown("""
**Between 2019 and 2023**, documented Sand Mafia incidents include the deaths of:

- Government district officials attempting to halt operations
- Journalists photographing illegal sites
- Civilians who filed complaints with police

Court documents in this dataset reveal bribery of local officials, threats against whistleblowers,
and environmental regulations routinely violated without sanction. The gap between observed
mining intensity and court-recognized cases is itself a measure of this impunity , and it is
largest in Himachal Pradesh, West Bengal, and Jharkhand.
        """)

    with tab_inequality:
        st.markdown("""
**Illegal sand mining is not uniformly distributed across society.** It concentrates in
communities of marginal workers , those with fewer than 183 working days per year ,
along river-adjacent areas where formal employment is scarce.

The correlation between marginal worker ratio and mining intensity is **r = +0.612**, the
strongest single socioeconomic predictor in the dataset. These are the communities whose
rivers are extracted and whose groundwater is contaminated. They receive no compensation.

This makes illegal sand mining **both an environmental problem and a question of social justice.**
        """)

    _divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # PART II , THE DATA
    # ═══════════════════════════════════════════════════════════════════════════

    st.markdown(
        """<p style="font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;
                      color:#e8a838;font-weight:700;margin-bottom:0.2rem;">
        Part II</p>
        <h2 style="font-family:'Playfair Display',serif;font-size:2rem;
                    color:#1c1a17;margin:0 0 1.5rem 0;">Mapping the Invisible</h2>""",
        unsafe_allow_html=True,
    )

    _chapter("04", "Seven Sources, One Picture", "The art of making fragmented data speak")

    _body(
        "Assembling a coherent picture of illegal sand mining from scratch required merging datasets "
        "with different geographic granularities (state, district, point), different temporal "
        "resolutions (annual, monthly, per-minute), different state-name conventions, and different "
        "measurement standards. The result is not a perfect dataset. It is <strong>the most complete "
        "picture of illegal sand mining in India that can currently be assembled from public sources.</strong>"
    )

    # Interactive data source explorer
    # st.markdown("#### 🗄️ Explore the Data Sources")
    # source = st.selectbox(
    #     "Select a data source to learn more:",
    #     [
    #         "India Sand Watch (Veditum India Foundation)",
    #         "National Data & Analytics Platform (NDAP)",
    #         "Water Resources Info System (WRIS)",
    #         "Central Pollution Control Board (CPCB)",
    #         "PMAY-U Administrative Records",
    #         "Census 2011 Socioeconomic Tables",
    #         "Prayagraj Water Quality Sensors",
    #     ],
    #     label_visibility="collapsed",
    # )

    # source_details = {
    #     "India Sand Watch (Veditum India Foundation)": {
    #         "icon": "🔴",
    #         "records":2,212 incident records · 2001–2026",
    #         "what": "Field reports from citizen observers, journalists, court documents, government district surveys, and news archives.",
    #         "strength": "The only publicly available national-scale mining incident database in India.",
    #         "weakness": "Coverage is uneven , Bihar and MP are overrepresented; northeastern states are nearly absent.",
    #         "sub": "4 sub-datasets: 375 mining observations, 91 court documents, 124 news reports, 2,212 unified geo-coded incidents.",
    #     },
    #     "National Data & Analytics Platform (NDAP)": {
    #         "icon": "🏛️",
    #         "records": "36 states × multiple indicators",
    #         "what": "Official government series: NCRB crime/police data, Census 2011 (population, literacy, marginal workers, housing), CPCB air quality, PMAY-U progress.",
    #         "strength": "Authoritative, standardized, government-backed.",
    #         "weakness": "Annual resolution only; some indicators lag by 10+ years (Census 2011).",
    #         "sub": "Used for: crime rates, police strength, household conditions, poverty proxies, literacy, PMAY allocations.",
    #     },
    #     "Water Resources Info System (WRIS)": {
    #         "icon": "💧",
    #         "records": "7,190 groundwater monitoring stations",
    #         "what": "Station-level latitude, longitude, and Total Dissolved Solids (TDS) measurements, spatially linked to nearest confirmed mining point.",
    #         "strength": "Point-level spatial precision; enables Geographically Weighted Regression at fine scale.",
    #         "weakness": "Snapshot data , not longitudinal; TDS has multiple causes beyond mining.",
    #         "sub": "Used for: GWR contamination analysis; mining-to-monitoring ratio maps.",
    #     },
    #     "Central Pollution Control Board (CPCB)": {
    #         "icon": "💨",
    #         "records": "State-level annual averages",
    #         "what": "PM2.5 and PM10 concentrations from the national ambient air quality monitoring network.",
    #         "strength": "Directly measures the dust signature of sand transport.",
    #         "weakness": "State-level aggregation masks district-level variation.",
    #         "sub": "Used for: spatial regression predictors; Random Forest feature set.",
    #     },
    #     "PMAY-U Administrative Records": {
    #         "icon": "🏗️",
    #         "records": "State and district level",
    #         "what": "Houses sanctioned, grounded, and completed under Pradhan Mantri Awas Yojana-Urban, plus central government assistance (₹ crore) per state.",
    #         "strength": "The primary treatment variable for all causal analyses.",
    #         "weakness": "Potential measurement error in self-reported completion figures.",
    #         "sub": "Used for: DiD, IV/2SLS, synthetic control, mediation analysis, Random Forest.",
    #     },
    #     "Census 2011 Socioeconomic Tables": {
    #         "icon": "📊",
    #         "records": "State-level",
    #         "what": "Total population, literate population, marginal worker proportions (< 183 days/year), household condition (good / liveable / dilapidated).",
    #         "strength": "Comprehensive; standardized definitions.",
    #         "weakness": "15 years old; India has changed dramatically since 2011.",
    #         "sub": "Used for: socioeconomic correlates analysis; mediation analysis.",
    #     },
    #     "Prayagraj Water Quality Sensors": {
    #         "icon": "🌊",
    #         "records": "~99,000 one-minute readings · Jan 2019 – Feb 2020",
    #         "what": "Two monitoring buoys at the Ganga and Sangam (Ganga-Yamuna confluence): dissolved oxygen, pH, ORP, conductivity, temperature, composite WQI.",
    #         "strength": "Extremely high temporal resolution; captures seasonal and event-driven dynamics.",
    #         "weakness": "Only 13 months; only 2 locations; the Kumbh Mela confounds the early period.",
    #         "sub": "Used for: seasonal conductivity analysis; dry-season mining correlation; trend decomposition.",
    #     },
    # }

    # # d = source_details[source]
    # st.markdown(
    #     f"""
    #     <div style="background:#fff8ee;border:1.5px solid #e0d5c4;border-radius:8px;
    #                 padding:1.5rem;margin-top:0.5rem;">
    #         <div style="font-size:2rem;margin-bottom:0.5rem;">{d['icon']}</div>
    #         <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;
    #                     color:#7a6e5e;margin-bottom:0.8rem;">{d['records']}</div>
    #         <div style="color:#2e2b26;line-height:1.7;margin-bottom:0.8rem;">
    #             <strong>What it contains:</strong> {d['what']}</div>
    #         <div style="color:#2e2b26;line-height:1.7;margin-bottom:0.5rem;">
    #             <strong>✅ Strength:</strong> {d['strength']}</div>
    #         <div style="color:#2e2b26;line-height:1.7;margin-bottom:0.5rem;">
    #             <strong>⚠️ Weakness:</strong> {d['weakness']}</div>
    #         <div style="color:#7a6e5e;font-size:0.85rem;font-style:italic;
    #                     border-top:1px solid #e0d5c4;padding-top:0.6rem;margin-top:0.6rem;">
    #             {d['sub']}</div>
    #     </div>
    #     """,
    #     unsafe_allow_html=True,
    # )

    _chapter("05", "Where the Mafia Lives", "Geography of extraction across India")

    _body(
        "Before asking why mining happens, we need to know where. Kernel Density Estimation (KDE) "
        "over 373 geo-coded mining points reveals that illegal extraction is emphatically not random. "
        "It clusters in two distinct corridors , and those corridors map almost perfectly onto "
        "<strong>India's great river systems.</strong>"
    )

    _img(
        "outputs/heatmap_mining_observations.png",
        "KDE intensity surface: illegal mining density across India. "
        "Two corridors dominate , the Gangetic plains and the Central India plateau.",
    )

    _body(
        "The Gangetic Plains corridor stretches along the Ganga and its tributaries through Bihar, "
        "eastern Uttar Pradesh, and West Bengal. <strong>Bihar alone accounts for 193 of 375 total "
        "field observations</strong> , 51% , with Patna district contributing 105 records: the single "
        "hottest geographic concentration in the country."
    )

    _body(
        "The Central India Plateau corridor cuts across Madhya Pradesh and Rajasthan, driven "
        "primarily by the Chambal and Narmada rivers. Morena district in MP holds the highest "
        "district-level count nationally at <strong>81 records</strong> , a figure that reflects both the "
        "Chambal's geography and its political sensitivity."
    )

    c1, c2 = st.columns([3, 2])
    with c1:
        _img(
            "outputs/geographic_distribution_bars.png",
            "State-by-state mining incident distribution. Bihar (field observations) vs "
            "Madhya Pradesh (news + court records) , two very different detection mechanisms.",
        )
    with c2:
        st.markdown("""
**A tale of two datasets**

Bihar dominates *field observations* (193 of 375) because it has the densest citizen observer network.

Madhya Pradesh leads in *news-level incidents* (279) and has a substantial body of NGT court filings.

This asymmetry is itself a finding: **Bihar is heavily mined but weakly prosecuted. MP is both mined and litigated.** The enforcement environment, not just the mining, differs.
        """)

    _chapter("06", "The River Corridors", "Spatial clustering and what it reveals about networks")

    _body(
        "Is mining spatially random, or does it cluster in ways that suggest coordinated criminal "
        "networks? The answer, using Moran's I spatial autocorrelation, is: <strong>marginally clustered, "
        "but the real story is in the hotspots.</strong>"
    )

    _body(
        "Global Moran's I for state-level mining counts is I = 0.121 (z = 1.29, p = 0.108). This "
        "is positive , nearby states tend to have similar mining levels , but falls just below the "
        "α = 0.05 significance threshold. Mining is somewhat patterned but not overwhelmingly so."
    )

    _two_col_images(
        "sangam_ganga_figures/fig_morans_i.png",
        "Global Moran's I scatter plot (I = 0.121). Positive slope indicates mild clustering.",
        "sangam_ganga_figures/fig_lisa_hotspots.png",
        "LISA hotspot map: the red High-High belt (Goa, Gujarat, MP, Rajasthan) shares the Chambal and Narmada.",
    )

    _body(
        "Local Indicators of Spatial Association (LISA) cut through the global signal and reveal "
        "four specific hotspot states: <strong>Goa, Gujarat, Madhya Pradesh, and Rajasthan</strong> form a "
        "geographically contiguous High-High cluster. These states share rivers , most importantly "
        "the Chambal , and almost certainly share criminal networks. This is the spatial fingerprint "
        "of a cross-border Sand Mafia."
    )

    _callout_box(
        "The Chambal Belt",
        "Goa, Gujarat, Madhya Pradesh, and Rajasthan form a contiguous High-High LISA cluster, "
        "suggesting that sand extraction networks in these states are operationally connected , "
        "organized crime, not opportunistic individual actors.",
        colour="#c0392b",
    )

    _divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # PART III , THE POLICY TRIGGER
    # ═══════════════════════════════════════════════════════════════════════════

    st.markdown(
        """<p style="font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;
                      color:#e8a838;font-weight:700;margin-bottom:0.2rem;">
        Part III</p>
        <h2 style="font-family:'Playfair Display',serif;font-size:2rem;
                    color:#1c1a17;margin:0 0 1.5rem 0;">The Policy Trigger</h2>""",
        unsafe_allow_html=True,
    )

    _chapter("07", "PMAY-U and the 14.7× Surge", "How a housing policy accidentally fuelled organized crime")

    _pull_quote(
        '"Mining jumped 14.7× after the PMAY-U housing scheme launched in 2015. '
        'Pre-2015: 13 incidents/year. Post-2015: 191 incidents/year."'
    )

    _lede(
        "In June 2015, the Indian government launched PMAY-U with an ambitious goal: "
        "affordable housing for all urban Indians by 2022. It would sanction nearly 12 million "
        "new homes. It would transform how millions of people lived. It would also, the data "
        "suggests, transform illegal sand mining from a regional problem into a national crisis."
    )

    _img(
        "sangam_ganga_figures/fig_temporal_surge.png",
        "Annual mining incidents 2010–2026. Blue = pre-PMAY baseline (avg 13/year). "
        "Red = post-PMAY surge (avg 191/year). The dashed line marks the 2015 launch.",
    )

    _body(
        "The jump is unmistakable in the raw time series. A Mann-Whitney U test confirms it is "
        "statistically significant (p = 0.0011). But is the <em>cause</em> PMAY, or something else? "
        "Improved reporting infrastructure? A general increase in environmental awareness? "
        "Better citizen observer networks?"
    )

    _body(
        "This is where the analysis moves from description to identification. "
        "To claim that PMAY <em>caused</em> the mining surge , not merely correlated with it , "
        "we need causal inference machinery. We use four independent strategies, and all four "
        "point in the same direction."
    )

    _chapter("08", "Four Ways to Prove Causation", "DiD, IV, synthetic control, and mediation")

    _body("The Evidence Stack")

    with st.expander("📐 Strategy 1: Difference-in-Differences", expanded=True):
        st.markdown("""
**The idea:** Compare states that received large PMAY allocations ("treated") against those that received
small allocations ("control"). If both groups had similar mining trends before 2015, and treated states
diverged sharply after 2015, PMAY is the likely cause , not some confounding state-specific factor.

**The model:**
```
log(mining_it) = β · (Treated_i × Post_t) + state_FE + year_FE + ε_it
```

**The result:** β̂ = **+1.057** (p < 0.001, 95% CI: [0.855, 1.259])

High-PMAY states experienced **187.7% more mining post-2015** than low-PMAY states,
after removing all state-level and year-level confounds through fixed effects.

**The parallel trends test:** F = 0.406, p = 0.805 , pre-2015 trends are statistically
indistinguishable between treated and control states. The assumption holds.
        """)
        _img(
            "sangam_ganga_figures/fig_event_study.png",
            "Event study DiD: pre-period coefficients (green background) are flat and near zero. "
            "Post-period coefficients (pink) rise monotonically to +1.5 log-mining units by year +9.",
        )

    with st.expander("🎯 Strategy 2: Instrumental Variables (2SLS)", expanded=True):
        st.markdown("""
**The concern:** Maybe states that received more PMAY funding were already politically connected,
already had more mining infrastructure, or were already diverging. DiD can't fully rule this out.

**The instrument:** Central government financial assistance (₹ crore) to each state.
This is determined by a national formula based on urban population and housing deficit ,
not by local mining conditions. It is plausibly *exogenous* to state-level mining propensity.

**First stage:** F = 16.40 (p < 0.001) , the instrument strongly predicts PMAY scale.

**2SLS result:** β̂₂SLS = **+0.631**, versus β̂OLS = +0.589.

The IV estimate is *larger* than OLS, consistent with attenuation bias , OLS slightly underestimates
the true causal effect because of measurement error in PMAY allocation figures. The causal
story survives the endogeneity correction.
        """)

    with st.expander("🔬 Strategy 3: Synthetic Control for Uttar Pradesh", expanded=True):
        st.markdown("""
**The idea:** Build a "synthetic Uttar Pradesh" , a weighted combination of donor states
that best matches UP's pre-2015 mining trajectory. Then ask: how much did actual
post-2015 UP mining exceed this counterfactual?

**The pre-period fit:** Root Mean Square Error = 0.12 , a good match.
The synthetic UP draws weights from an unnamed central Indian state (72.4%),
Arunachal Pradesh (11.7%), Madhya Pradesh (9.9%), and Maharashtra (6.0%).

**The post-2015 gap:** Actual UP mining exceeded the synthetic counterfactual by an
average of **+0.948 log-mining units** , equivalent to **158% excess mining** relative to
what UP would have experienced without PMAY.
        """)
        _img(
            "sangam_ganga_figures/fig_synthetic_control.png",
            "Synthetic control: actual UP (red) vs synthetic counterfactual (blue dashed). "
            "The shaded region is the causal excess attributable to PMAY. ATT = +0.948 log-units (+158%).",
        )

    with st.expander("🔗 Strategy 4: Bootstrapped Mediation Analysis", expanded=True):
        st.markdown("""
**The idea:** Poverty → PMAY allocation → sand demand → mining.
How much of poverty's effect on mining is mediated through PMAY construction?

**Method:** 5,000 bootstrap samples to estimate the indirect effect.

**Result:** **63.6% of poverty's total effect on mining is mediated through PMAY construction.**

This quantifies the full causal chain: poorer states receive more PMAY funding,
which increases construction activity, which increases demand for sand,
which increases illegal extraction.

**The cruel paradox:** The government program intended to lift the poor out of
inadequate housing is partly fuelled by an industry that destroys the environmental
resources on which poor communities depend.
        """)

    _stat_row([
        ("187.7%", "more mining in high-PMAY states (DiD)"),
        ("+0.631", "IV causal estimate (2SLS, exogenous instrument)"),
        ("+158%", "excess mining in UP vs synthetic control"),
        ("63.6%", "of poverty's mining effect mediated by PMAY"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    _chapter("09", "The Spatial Mismatch Paradox", "Why demand and supply live in different states")

    _body(
        "Here is the most counterintuitive finding in the entire dataset. If PMAY construction "
        "demand drives illegal mining, you might expect mining to concentrate where construction "
        "is happening , in the states building the most houses. But it doesn't."
    )

    _body(
        "The <strong>Bivariate Moran's I</strong> between PMAY allocation and mining intensity is "
        "just +0.033 (p = 0.417). States with the most construction are not the same states "
        "with the most mining. Sand is dug up in Bihar and Madhya Pradesh, then transported "
        "hundreds of kilometres to construction sites in distant states."
    )

    _img(
        "sangam_ganga_figures/fig_spatial_clusters.png",
        "Side-by-side: PMAY houses sanctioned (left) vs total mining incidents (right). "
        "The maps look different. That's the point.",
    )

    _body(
        "This spatial decoupling has profound implications for enforcement. "
        "States that receive PMAY funding have little incentive to restrict the sand supply "
        "coming from other states. States that bear the extraction cost (Bihar, MP) "
        "receive less construction benefit. The federal structure of Indian governance "
        "means no single actor is accountable for the full chain."
    )

    # _pull_quote(
    #     "\"Supply and demand are spatially decoupled. "
    #     "Bihar digs; Maharashtra builds. The Ganga pays the price.\""
    # )

    _divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # PART IV , WHO BEARS THE COST
    # ═══════════════════════════════════════════════════════════════════════════

    st.markdown(
        """<p style="font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;
                      color:#e8a838;font-weight:700;margin-bottom:0.2rem;">
        Part IV</p>
        <h2 style="font-family:'Playfair Display',serif;font-size:2rem;
                    color:#1c1a17;margin:0 0 1.5rem 0;">Who Bears the Cost</h2>""",
        unsafe_allow_html=True,
    )

    _chapter("10", "Poverty, Enforcement, and the Marginal Worker", "The socioeconomic anatomy of mining")

    _body(
        "If construction demand explains the <em>when</em> and <em>where</em> of the post-2015 surge, "
        "socioeconomic conditions explain the <em>who</em> and <em>why</em>. "
        "Two findings stand out."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(
            """
            <div style="background:#fff8ee;border:1px solid #e0d5c4;border-left:4px solid #e8a838;
                        border-radius:6px;padding:1.2rem;height:100%;">
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;
                            color:#7a6e5e;margin-bottom:0.4rem;">Finding #1</div>
                <div style="font-family:'Playfair Display',serif;font-size:1.5rem;
                            color:#1c1a17;margin-bottom:0.5rem;">r = +0.612</div>
                <div style="font-size:0.9rem;color:#3a3530;line-height:1.65;">
                    Marginal worker ratio is the <strong>strongest socioeconomic predictor</strong>
                    of mining intensity , stronger than poverty rate, literacy, or urbanisation.
                    Illegal sand mining is accessible seasonal income for workers without stable
                    employment alternatives.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown(
            """
            <div style="background:#fff8ee;border:1px solid #e0d5c4;border-left:4px solid #c0392b;
                        border-radius:6px;padding:1.2rem;height:100%;">
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;
                            color:#7a6e5e;margin-bottom:0.4rem;">Finding #2</div>
                <div style="font-family:'Playfair Display',serif;font-size:1.5rem;
                            color:#1c1a17;margin-bottom:0.5rem;">15–45×</div>
                <div style="font-size:0.9rem;color:#3a3530;line-height:1.65;">
                    Madhya Pradesh and Gujarat show <strong>mining-to-police ratios 15 to 45 times higher</strong>
                    than Maharashtra, Tamil Nadu, and Andhra Pradesh. Enforcement failure is
                    structural, not incidental.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    _body(
        "The housing dimension is equally stark. The correlation between a composite "
        "housing quality index and mining intensity is r = −0.750 among the top five mining states. "
        "The correlation between dilapidated housing rates and mining is +0.507 across all states. "
        "Bihar has both the highest dilapidated housing rate (7.5%) and, by field observations, "
        "the most mining."
    )

    _two_col_images(
        "outputs/choropleth_housing_dilapidated.html" if False else "outputs/heatmap_household_conditions.png",
        "Household conditions by state. Bihar, Odisha, West Bengal, and Assam "
        "record the highest dilapidated housing proportions , and are also top mining states.",
        "outputs/heatmap_crime_intensity.png",
        "Crime intensity heatmap: cities in high-mining states (Gwalior, Patna, Jabalpur, Indore) "
        "show consistently elevated crime intensity across 2010–2014.",
    )

    _callout_box(
        "The Enforcement Gap in Numbers",
        """
        <table style="width:100%;border-collapse:collapse;font-size:0.88rem;">
            <tr style="border-bottom:1px solid #e0d5c4;">
                <th style="text-align:left;padding:4px 8px;">State</th>
                <th style="text-align:right;padding:4px 8px;">Mining Incidents</th>
                <th style="text-align:right;padding:4px 8px;">Mining per Police Officer</th>
            </tr>
            <tr><td style="padding:4px 8px;">Madhya Pradesh</td>
                <td style="text-align:right;padding:4px 8px;">279</td>
                <td style="text-align:right;padding:4px 8px;color:#c0392b;font-weight:700;">0.533</td></tr>
            <tr><td style="padding:4px 8px;">Gujarat</td>
                <td style="text-align:right;padding:4px 8px;">114</td>
                <td style="text-align:right;padding:4px 8px;color:#c0392b;font-weight:700;">0.511</td></tr>
            <tr><td style="padding:4px 8px;">Maharashtra</td>
                <td style="text-align:right;padding:4px 8px;">182</td>
                <td style="text-align:right;padding:4px 8px;color:#2ecc71;font-weight:700;">0.034</td></tr>
            <tr><td style="padding:4px 8px;">Andhra Pradesh</td>
                <td style="text-align:right;padding:4px 8px;">99</td>
                <td style="text-align:right;padding:4px 8px;color:#2ecc71;font-weight:700;">0.019</td></tr>
            <tr><td style="padding:4px 8px;">Tamil Nadu</td>
                <td style="text-align:right;padding:4px 8px;">120</td>
                <td style="text-align:right;padding:4px 8px;color:#2ecc71;font-weight:700;">0.012</td></tr>
        </table>
        """,
    )

    _chapter("11", "The Groundwater Signal", "7,190 wells and what they reveal")

    _body(
        "Standard regression explains only 15.8% of the variance in groundwater quality "
        "near mining sites. That low figure is not a failure , it is a discovery. It tells us "
        "that the relationship between mining proximity and water contamination is "
        "<strong>fundamentally local.</strong> The same amount of mining affects water quality "
        "very differently in Bihar's alluvial Gangetic sediment versus Madhya Pradesh's "
        "hard-rock Chambal basin."
    )

    _body(
        "Geographically Weighted Regression (GWR), which allows coefficients to vary in space, "
        "raises explained variance from 15.8% to <strong>54.5%</strong> , a 3.4× improvement. "
        "At each of 7,190 WRIS monitoring stations, GWR estimates a local coefficient for "
        "distance-to-nearest-mining-site. A negative coefficient means: closer to mining = "
        "higher Total Dissolved Solids = worse water quality."
    )

    _img(
        "sangam_ganga_figures/fig_gwr_coefficients.png",
        "GWR local coefficients. Blue/dark = contamination signal (closer to mining → higher TDS). "
        "The signal concentrates in the Gangetic corridor (Bihar, West Bengal).",
    )

    contamination_data = {"Bihar": {"signal": "100%", "median": "-0.346"}, "West Bengal": {"signal": "78%", "median":"-0.505 [stronger per unit]"}, "Madhya Pradesh": {"signal": "39%", "median":"+0.215 [hard-rock geology masks signal]"}}

    table_rows = [

        {"State": state, 
         "Stations with Contamination signal": values["signal"], "Median GWR Coefficient": values["median"],
         
         } for state, values in contamination_data.items()
    ]
    st.table(table_rows)

    _body(
        "Bihar's 100% contamination rate reflects its geology: shallow alluvial sediment connects "
        "the water table directly to the mined riverbed. Disturb one layer, contaminate the other. "
        "Madhya Pradesh's weaker signal isn't good news , it means the Chambal basin's naturally "
        "mineral-rich geology hides the anthropogenic damage."
    )

    _chapter("12", "Conductivity Doesn't Lie", "The Ganga sensor evidence")

    _body(
        "Two water quality buoys floating on the Ganga and Sangam at Prayagraj captured "
        "approximately 99,000 one-minute readings between January 2019 and February 2020. "
        "They were not placed there to study sand mining. But they recorded its signature anyway."
    )

    _body(
        "The hypothesis: river conductivity , dissolved mineral content, a proxy for riverbed "
        "disturbance , should peak during the dry season (November–February) when river levels "
        "fall, exposing the sand, and miners move in."
    )

    _img(
        "sangam_ganga_figures/fig_ganga_sangam_timeseries.png",
        "Full time-series: Ganga and Sangam sensors (Jan 2019 – Feb 2020). "
        "The conductivity spikes in the dry season are clearly visible.",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Dry-season conductivity (avg)", "478 µS/cm", delta="+1.73× monsoon season")
        st.metric("Monsoon conductivity (avg)", "276 µS/cm")
    with col2:
        st.metric("Cohen's d effect size", "1.78", delta="Very large by convention")
        st.metric("Mann-Whitney p-value", "< 0.001", delta="Highly significant")

    _img(
        "sangam_ganga_figures/fig_conductivity_mining_seasonal.png",
        "Monthly water quality: red bars = dry season (Nov–Feb), blue = monsoon. "
        "Both sensors show higher conductivity and worse WQI in dry-season months.",
    )

    _body(
        "The seasonal decomposition of the Ganga conductivity series reveals a long-term "
        "upward trend of <strong>+1.37 µS/cm per day</strong> across the monitoring period , "
        "consistent with progressive riverbed disturbance over 13 months. The 30-day cyclical "
        "component reflects tidal backflow effects. The overall picture: the river is getting "
        "progressively more contaminated, and the contamination peaks precisely when miners arrive."
    )

    _img(
        "sangam_ganga_figures/fig_ganga_seasonal.png",
        "Seasonal decomposition (additive STL): observed conductivity, long-term trend (+1.37 µS/cm/day), "
        "30-day seasonal cycle, and residuals. Kumbh Mela period excluded from fitting.",
    )

    _divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # PART V , WHAT COMES NEXT
    # ═══════════════════════════════════════════════════════════════════════════

    st.markdown(
        """<p style="font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;
                      color:#e8a838;font-weight:700;margin-bottom:0.2rem;">
        Part V</p>
        <h2 style="font-family:'Playfair Display',serif;font-size:2rem;
                    color:#1c1a17;margin:0 0 1.5rem 0;">What Comes Next</h2>""",
        unsafe_allow_html=True,
    )

    _chapter("13", "NLP Finds the Mafia's Fingerprints", "Machine reading 375 field reports")

    _body(
        "Not every mining observation in India Sand Watch is unambiguously illegal. "
        "A JCB beside a riverbed at night is different from a tractor doing permitted extraction "
        "in the morning. To distinguish them at scale, the study built a rule-based scoring "
        "system trained on language patterns extracted from the 91 court documents."
    )

    _body("Each of the 375 field reports was scored across three signal classes:")

    st.markdown(
        """
<div style="color:black">
<strong>Operational signals (3 pts each)</strong><br>
Mentions of JCBs, excavators, pumps, trucks, tractors, trolleys ,
large-scale mechanized extraction inconsistent with permitted small-scale mining.<br><br>
<strong>Risk signals (1–1.5 pts each)</strong><br>
Nighttime activity, high-volume extraction, repeated / daily operations.<br><br>
<strong>Legal signals (2 pts each)</strong><br>
Court-document language: "illegal mining," "no environmental clearance," "lease violation,"<br>
"excess extraction," "unauthorized operation."
</div>
        """,
        unsafe_allow_html=True,
    )

    # Quiz interaction
    st.markdown("#### 🔎 How illegal does this field note look?")
    note = st.text_area(
        "Paste or type a field observation note:",
        value="Three JCB machines and a fleet of trucks observed at 11pm. Extraction continuous "
              "since morning. No visible permit boards. Locals say this has been happening daily "
              "for two months.",
        height=100,
        label_visibility="collapsed",
    )

    if note.strip():
        score = 0
        reasons = []
        kw_ops = ["jcb", "excavator", "pump", "truck", "tractor", "trolley", "machines"]
        kw_risk = ["night", "pm", "daily", "continuous", "months", "high volume", "large"]
        kw_legal = ["illegal", "no permit", "no clearance", "unauthori", "violation", "without permit"]

        for kw in kw_ops:
            if kw in note.lower():
                score += 3
                reasons.append(f"✅ Operational: '{kw}' (+3)")
        for kw in kw_risk:
            if kw in note.lower():
                score += 1
                reasons.append(f"⚠️ Risk: '{kw}' (+1)")
        for kw in kw_legal:
            if kw in note.lower():
                score += 2
                reasons.append(f"⚖️ Legal: '{kw}' (+2)")

        if score >= 8:
            verdict = "🔴 Highly likely illegal"
            colour = "#c0392b"
        elif score >= 4:
            verdict = "🟠 Possibly illegal"
            colour = "#e8a838"
        else:
            verdict = "🟢 Insufficient signal"
            colour = "#27ae60"

        st.markdown(
            f"""
            <div style="background:#fff8ee;border:2px solid {colour};border-radius:8px;
                        padding:1rem 1.2rem;margin-top:0.5rem;">
                <div style="font-size:1.2rem;font-weight:700;color:{colour};
                            margin-bottom:0.5rem;">{verdict} (score: {score})</div>
                {"".join(
                    f"<div style='font-size:0.85rem;color:#5a4e3c;'>{r}</div>"
                    for r in reasons
                )
                or "<div style='font-size:0.85rem;color:#9a8c78;'>No scoring keywords detected.</div>"}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    _body(
        "Applying this classifier to all 375 observations: "
        "<strong>121 (32%) are classified as highly likely illegal; 254 (68%) as possibly illegal.</strong> "
        "The states with the highest absolute counts of highly likely illegal observations: "
        "Uttar Pradesh (32), Madhya Pradesh (30), West Bengal (25), Bihar (19). "
        "When normalised by total observations per state, the highest proportions are "
        "Goa (100%), Himachal Pradesh (100%), Rajasthan (87.5%), and Madhya Pradesh (69.8%)."
    )

    _callout_box(
        "Why Bihar's Proportion is Low",
        "Bihar has the highest raw count of field observations (193) but one of the lowest "
        "proportions of 'highly likely illegal' classifications (9.8%). This is consistent "
        "with Bihar having a large volume of lower-intensity, possibly artisanal (small-scale, "
        "manual) extraction that does not trigger the operational machinery signals. "
        "Bihar is heavily mined , but by a different type of actor than the JCB-and-truck operations "
        "in Goa and Rajasthan.",
    )

    _chapter("14", "The Enforcement Gap Map", "Where observed crime exceeds court action")

    _body(
        "The most actionable output of the NLP analysis is the enforcement gap: for each state, "
        "the difference between the rate of <em>observed</em> illegal mining and the rate of "
        "<em>court-recognized</em> illegal cases. Where this gap is largest, strengthened enforcement "
        "would have the highest expected marginal impact."
    )

    enforcement_data = {
        "Himachal Pradesh": {"observed": 100, "court": 5, "gap": "🔴 Very Large"},
        "West Bengal": {"observed": 52, "court": 8, "gap": "🔴 Very Large"},
        "Jharkhand": {"observed": 38, "court": 6, "gap": "🔴 Large"},
        "Goa": {"observed": 100, "court": 22, "gap": "🟠 Large"},
        "Rajasthan": {"observed": 87, "court": 31, "gap": "🟠 Moderate"},
        "Madhya Pradesh": {"observed": 70, "court": 41, "gap": "🟡 Moderate"},
        "Haryana": {"observed": 22, "court": 35, "gap": "🟢 Negative (proactive)"},
        "Karnataka": {"observed": 18, "court": 29, "gap": "🟢 Negative (proactive)"},
    }

    st.markdown("### Enforcement gap by state")

    table_rows = [
        {
            "State": state,
            "Observed illegal rate": values["observed"],
            "Court-recognized rate": values["court"],
            "Enforcement gap": values["gap"],
        }
        for state, values in enforcement_data.items()
    ]

    st.table(table_rows)

    _chapter("15", "Six Policy Levers That Could Work", "Evidence-based recommendations")

    st.markdown(
        """<p style="color:#5a4e3c;font-size:0.95rem;line-height:1.75;margin-bottom:1.5rem;">
        The analysis points to specific, actionable policy interventions , organised by
        who needs to act and what the evidence says.
        </p>""",
        unsafe_allow_html=True,
    )

    rec_tab1, rec_tab2, rec_tab3 = st.tabs([
        "🏛️ Central Government", "🗺️ State Governments", "⚖️ Courts & Civil Society"
    ])

    with rec_tab1:
        st.markdown("""
**1. Sand Sourcing Compliance Audit for PMAY**

The causal evidence is clear: PMAY construction demand drives illegal extraction.
The central government should require state governments to source sand for PMAY
projects exclusively from verified legal stockpiles, and make this a condition of central
assistance release. Transform the demand-side driver into a demand-side enforcement lever.

**2. Continuous Environmental Monitoring Network**

The Prayagraj sensor analysis demonstrates the feasibility of continuous, automated
water quality monitoring. Deploy conductivity and TDS monitoring buoys at 20–30 sites
along the Ganga, Chambal, and Narmada , with data publicly accessible in real time.
Create an objective, legally admissible evidentiary record of environmental damage.
        """)

    with rec_tab2:
        st.markdown("""
**3. District-Level Enforcement Cells in High-Gap States**

The enforcement gap analysis identifies Himachal Pradesh, West Bengal, Jharkhand,
Gujarat, and Goa as states where observed illegal mining greatly exceeds court-recognized
cases. State governments here should deploy dedicated sand mining enforcement cells
at the district level, with performance metrics tied to district collector accountability.

**4. Machine-Verified Transport Permits (GPS + QR)**

Most illegal sand escapes detection not at extraction but during transport.
A GPS-tracked, QR-code-verified e-permit system for sand transport vehicles, modelled
on the e-way bill system under GST, would allow checkpoint interception without
monitoring every river stretch. Rajasthan and MP have piloted versions; standardise and mandate.

**5. Dry-Season MGNREGA Expansion in Mining Districts**

The marginal worker correlation (r = +0.612) points to a labour supply problem:
illegal mining offers seasonal income to workers without stable alternatives.
Expanding MGNREGA in high-mining districts specifically during October–February (peak
mining season) directly competes with illegal mining for the available labour pool.
        """)

    with rec_tab3:
        st.markdown("""
**Standardised Compliance Requirements**

NGT orders are the most common legal response to illegal mining, but enforcement varies wildly.
The NGT should issue standardised compliance affidavit requirements and appoint state-level
monitoring committees with fixed reporting timelines , reducing district administrator discretion.

**Organised Crime Legislation**

Most sand mining cases proceed under the Mines and Minerals Act or environmental statutes with
relatively light penalties. The organised, cross-district, interstate nature of Sand Mafia operations
(evidenced by the HH spatial cluster in Goa, Gujarat, MP, Rajasthan) qualifies these networks
for prosecution under MCOCA and state equivalents. Enabling asset forfeiture and longer custody should be a consideration. 

**District-Level Longitudinal Panel**

The primary limitation of this causal analysis is cross-sectional state-level data.
A district-level, annually updated panel combining mining incidents, police deployment,
PMAY completion rates, and environmental quality would allow much stronger causal identification.
Encourage NDAP and state data agencies to prioritise this assembly.

**Closing the Geographic Gaps**

Northeastern states, Odisha, Chhattisgarh, and Kerala are nearly absent from the observation
dataset despite significant rivers. Investing in trained observer networks in these states,
targeting riverine communities directly affected by extraction would help plot a clearer picture.
        """)

    _divider()

    # # ── Closing ───────────────────────────────────────────────────────────────
    # _pull_quote(
    #     '"Illegal sand mining is not primarily a story of poverty. '
    #     "It is a story of construction demand, supply-state extraction, "
    #     'and river corridor stress. The data are unambiguous." , Balasubramaniam & Garg, 2026'
    # )

    st.markdown(
        """
        <div style="background:#1c1a17;border-radius:10px;padding:2rem 2.5rem;
                    margin-top:2rem;color:#c9b99a;">
            <div style="font-family:'Playfair Display',serif;font-size:1.3rem;
                        color:#e8a838;margin-bottom:1rem;font-weight:700;">
                The Bottom Line
            </div>
            <p style="line-height:1.8;margin:0 0 0.8rem 0;">
                Illegal sand mining in India is not an isolated environmental problem.
                It is a <strong style="color:#e8dcc8;">systemic outcome of rapid housing policy and construction demand</strong>,
                concentrated in river corridors, enabled by enforcement failure,
                and borne disproportionately by marginal communities.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """<p style="font-size:0.78rem;color:#9a8c78;text-align:center;">
        CS3340 Data Science & Management · Final Report · April 2026 ·
        Urvashi Balasubramaniam & Manya Garg ·
        Data: India Sand Watch, NDAP, WRIS, CPCB, PMAY-U, Census 2011, Prayagraj Sensors
        </p>""",
        unsafe_allow_html=True,
    )