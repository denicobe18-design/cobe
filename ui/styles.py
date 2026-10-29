import streamlit as st


def apply_brutal_styles() -> None:
    st.markdown(
        """
        <style>
        :root { color-scheme: dark; }
        .stApp {
            background:
                radial-gradient(900px 420px at 15% -10%, rgba(62,224,197,.14), transparent 55%),
                radial-gradient(700px 380px at 100% 0%, rgba(255,45,149,.10), transparent 50%),
                #070b12;
            color: #d7ece8;
            font-family: Inter, "Segoe UI", sans-serif;
        }
        [data-testid="stHeader"] { background: transparent; }
        #MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
        .block-container { max-width: 1380px; padding: 0.6rem 1.2rem 2.4rem; }
        h1, h2, h3, p, span, li, label { color: #d7ece8; }
        .mast {
            display: flex; justify-content: space-between; gap: 1rem; align-items: end;
            margin-bottom: 0.85rem; padding-bottom: 0.75rem;
            border-bottom: 1px solid rgba(62,224,197,.22);
        }
        .mast h1 {
            margin: 0; font-size: 1.45rem; letter-spacing: .18em; font-weight: 750;
        }
        .mast h1 span { color: #3ee0c5; }
        .mast p { margin: .28rem 0 0; color: #8eacb4; font-size: .78rem; }
        .chips { display: flex; flex-wrap: wrap; gap: .4rem; justify-content: flex-end; }
        .chips b {
            padding: .38rem .62rem; border-radius: 999px;
            border: 1px solid rgba(62,224,197,.35);
            background: rgba(12, 28, 32, .8);
            color: #d7fff6; font-size: .72rem; letter-spacing: .06em; font-weight: 650;
        }
        .deck { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem; margin-bottom: .55rem; }
        .tile {
            background: linear-gradient(180deg, rgba(16, 32, 38, .92), rgba(8, 14, 20, .92));
            border: 1px solid rgba(62,224,197,.28);
            border-radius: 14px; padding: .55rem .75rem .5rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
        }
        .tile span { display: block; color: #8eacb4; font-size: .68rem; letter-spacing: .14em; text-transform: uppercase; }
        .tile strong {
            display: block; margin-top: .12rem; color: #f4fffb;
            font-size: 1.35rem; font-variant-numeric: tabular-nums; letter-spacing: .01em;
        }
        .tile em { font-style: normal; color: #8eacb4; font-size: .75rem; }
        .tile em.up { color: #3dff8a; }
        .tile em.down { color: #ff3358; }
        .bars { grid-column: 1 / -1; padding: .15rem .1rem .2rem; }
        .bars label {
            display: flex; justify-content: space-between; color: #8eacb4;
            font-size: .72rem; letter-spacing: .04em; margin-top: .15rem;
        }
        .bars b { color: #d7fff4; font-weight: 650; }
        .scene {
            position: relative; height: 580px; overflow: hidden; border-radius: 18px;
            border: 1px solid rgba(62,224,197,.28);
            background:
                linear-gradient(rgba(62,224,197,.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(62,224,197,.05) 1px, transparent 1px),
                radial-gradient(ellipse at 50% 45%, rgba(62,224,197,.12), transparent 60%),
                #080d14;
            background-size: 28px 28px, 28px 28px, auto, auto;
            box-shadow: inset 0 0 80px rgba(0,0,0,.45);
        }
        .scene:after {
            content: ""; position: absolute; inset: 0; pointer-events: none;
            background: repeating-linear-gradient(to bottom, transparent 0 2px, rgba(0,0,0,.08) 3px);
        }
        .hud {
            position: absolute; z-index: 3; left: 14px; right: 14px; top: 12px;
            display: flex; justify-content: space-between; gap: .6rem;
            font-family: ui-monospace, "SFMono-Regular", monospace;
            letter-spacing: .12em; font-size: .72rem; color: #b7fff0;
        }
        .hud .brand span { color: #3ee0c5; }
        .rok { color: #ffb020; font-weight: 700; }
        .pill {
            padding: .18rem .5rem; border-radius: 999px; border: 1px solid rgba(62,224,197,.45);
            color: #b7fff0;
        }
        .pill.live { color: #3ee0c5; border-color: rgba(62,224,197,.7); }
        .pill.warn { color: #ffb020; border-color: rgba(255,176,32,.8); }
        .pill.dead { color: #ff3358; border-color: rgba(255,51,88,.8); }
        .pill.won { color: #3dff8a; border-color: rgba(61,255,138,.7); }
        .floor {
            position: absolute; left: 18%; right: 18%; top: 250px; height: 180px;
            background: radial-gradient(ellipse at center, rgba(62,224,197,.16), transparent 68%);
            transform: rotateX(68deg); pointer-events: none;
        }
        .scene.shut .iso, .scene.shut .lesson { filter: grayscale(.85) brightness(.55); }
        .stamp {
            position: absolute; z-index: 6; left: 50%; top: 46%;
            transform: translate(-50%, -50%) rotate(-12deg);
            border: 4px solid #ff3355; color: #ff3355;
            font-weight: 800; letter-spacing: .18em; font-size: 1.55rem;
            padding: .45rem .85rem; background: rgba(0,0,0,.55);
            font-family: ui-monospace, "SFMono-Regular", monospace;
        }
        .stamp.won { border-color: #3ee0c5; color: #3ee0c5; }
        .iso {
            width: 560px; margin: 92px auto 0;
            display: grid; grid-template-columns: repeat(3, 168px); gap: 16px;
            transform: rotateX(48deg) rotateZ(-34deg);
            transform-style: preserve-3d;
        }
        .cell {
            position: relative; height: 128px;
            background: linear-gradient(160deg, rgba(28, 70, 74, .55), rgba(6, 10, 16, .88));
            border: 1px solid rgba(62,224,197,.45);
            box-shadow: 10px 14px 0 rgba(0,0,0,.35), inset 0 0 24px rgba(62,224,197,.08);
        }
        .upright {
            position: absolute; inset: 0;
            display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px;
            transform: rotateZ(34deg) rotateX(-48deg);
            text-align: center;
        }
        .upright span { font-size: .68rem; letter-spacing: .12em; color: #9fd8cf; }
        .upright strong { font-size: .95rem; letter-spacing: .06em; }
        .upright b { font-family: ui-monospace, monospace; color: #3ee0c5; font-size: 1rem; }
        .op, .mon { display: block; }
        .op {
            width: 12px; height: 18px; border-radius: 6px 6px 2px 2px;
            background: linear-gradient(#e9fff8, #1f8f78); position: relative; margin-bottom: 2px;
        }
        .op:before {
            content: ""; position: absolute; top: -7px; left: 1px; width: 10px; height: 10px;
            border-radius: 50%; background: #f4fffc; box-shadow: 0 0 8px #3ee0c5;
        }
        .mon {
            width: 26px; height: 14px; margin-bottom: 4px;
            background: #03140f; border: 1px solid #3ee0c5; box-shadow: 0 0 10px rgba(62,224,197,.7);
        }
        .cylinder {
            width: 46px; height: 70px; border-radius: 26px;
            display: grid; place-items: center;
            background: linear-gradient(90deg, #04241c, #7dffe8 42%, #083028 78%);
            box-shadow: 0 0 22px rgba(62,224,197,.75), inset 0 0 10px rgba(255,255,255,.35);
            animation: corepulse 2.6s ease-in-out infinite;
            color: #042018; line-height: 1;
        }
        .cylinder b { font-size: 1.15rem; }
        .cylinder span { font-size: .52rem; letter-spacing: .14em; }
        .cell.hot { border-color: #3ee0c5; box-shadow: 0 0 18px rgba(62,224,197,.45), 10px 14px 0 rgba(0,0,0,.35); }
        .cell.boost { border-color: #ff2d95; }
        .cell.veto, .cell.block { border-color: #ff3358; }
        .cell.freeze { border-color: #ffb020; animation: blink 1s steps(2) infinite; }
        .cell.brain { border-color: #e8c56b; }
        .lesson {
            position: absolute; z-index: 3; left: 14px; right: 14px; bottom: 10px;
            margin: 0; color: #d7c27a; font-size: .75rem; letter-spacing: .02em;
        }
        .rail { display: grid; grid-template-columns: repeat(4, 1fr); gap: .55rem; margin-top: .7rem; }
        .agent {
            min-height: 108px; padding: .6rem .7rem .7rem; border-radius: 12px;
            background: rgba(10,16,26,.9); border: 1px solid rgba(120,160,170,.2);
        }
        .agent header { display: flex; gap: .4rem; align-items: baseline; }
        .agent header span { color: #8eacb4; font-size: .62rem; letter-spacing: .12em; }
        .agent header strong { letter-spacing: .08em; font-size: .82rem; }
        .agent header b { margin-left: auto; color: #3ee0c5; font-family: ui-monospace, monospace; }
        .agent p {
            margin: .35rem 0 0; color: #b7c9c6; font-size: .74rem; line-height: 1.35;
            display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
        }
        .agent.hot { border-color: rgba(62,224,197,.7); }
        .agent.boost { border-color: rgba(255,45,149,.75); }
        .agent.veto, .agent.block { border-color: rgba(255,51,88,.8); }
        .agent.freeze { border-color: rgba(255,176,32,.85); }
        .agent.brain-card { border-color: rgba(232,197,107,.7); }
        .reason {
            margin: .4rem 0 .2rem; padding: .55rem .7rem; border-left: 3px solid #3ee0c5;
            background: rgba(8,16,24,.8); color: #d7fff4; font-size: .86rem;
        }
        .positions { display: flex; flex-direction: column; gap: .45rem; margin: .8rem 0; }
        .pos, .empty {
            display: grid; grid-template-columns: 1.1fr .9fr .9fr .9fr .7fr 1.6fr;
            gap: .4rem; align-items: center; padding: .65rem .75rem; border-radius: 12px;
            background: rgba(10,16,26,.9); border: 1px solid rgba(62,224,197,.2);
            font-variant-numeric: tabular-nums; font-size: .82rem;
        }
        .empty { display: block; color: #8eacb4; }
        .pos .sl { color: #ff3358; }
        .pos .tp { color: #3dff8a; }
        .pos .up { color: #3dff8a; }
        .pos .down { color: #ff3358; }
        .pos em { color: #8eacb4; font-style: normal; }
        .journal { display: grid; grid-template-columns: 1.2fr .8fr; gap: .8rem; margin-top: .4rem; }
        .journal section {
            background: rgba(8,12,18,.75); border: 1px solid rgba(120,160,170,.18);
            border-radius: 12px; padding: .4rem .8rem .8rem; max-height: 280px; overflow: auto;
        }
        .journal h3 { margin: .4rem 0; font-size: .84rem; letter-spacing: .12em; color: #8eacb4; }
        .journal ul { list-style: none; margin: 0; padding: 0; }
        .journal li { padding: .28rem 0; border-bottom: 1px solid rgba(255,255,255,.04); font-size: .78rem; line-height: 1.35; }
        .journal time { display: inline-block; width: 4.6rem; color: #6f8f98; font-family: ui-monospace, monospace; }
        .muted { color: #6f8f98; }
        .progress {
            height: 8px; margin: .35rem 0 .8rem; border-radius: 99px; overflow: hidden;
            background: #121a24; border: 1px solid rgba(62,224,197,.25);
        }
        .progress span { display: block; height: 100%; background: linear-gradient(90deg, #145c4c, #3dff8a); }
        .progress.quota span { background: linear-gradient(90deg, #6a4a12, #ffb020); }
        .dock-label {
            margin: .9rem 0 .35rem; color: #8eacb4; letter-spacing: .16em;
            font-size: .68rem; text-transform: uppercase;
        }
        [data-testid="stPlotlyChart"] {
            border: 1px solid rgba(62,224,197,.28); border-radius: 16px;
            background: #0b121b; overflow: hidden;
            box-shadow: inset 0 0 40px rgba(0,0,0,.25);
        }
        .stButton > button {
            border: 1px solid rgba(62,224,197,.45); background: #101820; color: #e7fff8;
            border-radius: 10px; min-height: 42px;
        }
        .stButton > button:hover { border-color: #3ee0c5; color: white; }
        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background: #101820; color: #e7fff8; border-color: rgba(62,224,197,.35);
        }
        @keyframes corepulse {
            50% { box-shadow: 0 0 32px rgba(125,255,232,.95), inset 0 0 12px white; }
        }
        @keyframes blink { 50% { filter: brightness(1.6); } }
        @media (max-width: 900px) {
            .iso { transform: none; width: auto; margin: 78px 12px 0; grid-template-columns: repeat(3, 1fr); }
            .upright { transform: none; }
            .floor { display: none; }
            .scene { height: auto; min-height: 520px; }
            .rail, .journal, .pos, .deck { grid-template-columns: 1fr; }
            .mast, .chips { flex-direction: column; align-items: start; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
