import os
import time
import streamlit as st

# ---------- Page setup ----------
st.set_page_config(page_title="E-Commerce AI Agent", page_icon="🛒", layout="wide")

# Load API keys from Streamlit secrets (cloud) into environment variables
try:
    for key in ("OPENAI_API_KEY", "GROQ_API_KEY", "GEMINI_API_KEY", "SERPER_API_KEY"):
        if key in st.secrets:
            os.environ[key] = st.secrets[key]
except Exception:
    pass  # no secrets file locally, that's fine

# ---------- Custom CSS ----------
st.markdown("""
<style>
.hero {background: linear-gradient(135deg,#6C5CE7,#a29bfe); padding:28px 32px;
       border-radius:16px; color:white; margin-bottom:20px;}
.hero h1 {margin:0; font-size:2rem;}
.hero p {margin:6px 0 0; opacity:.9;}
.card {background:#F4F2FF; padding:16px 18px; border-radius:12px;
       border-left:5px solid #6C5CE7; margin-bottom:10px;}
.stButton>button {width:100%; border-radius:10px; font-weight:600; padding:.6rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🛒 E-Commerce Operations & Marketing Agent</h1>
  <p>Analyze customer reviews, generate SEO product descriptions, and create social media posts, all in one click.</p>
</div>
""", unsafe_allow_html=True)


# ---------- Backend connection ----------
def run_agents(name, desc, reviews, tone):
    try:
        from crew_logic import run_crew  # Momna's CrewAI function
        result = run_crew(name, desc, reviews, tone)
        result["_demo"] = False
        return result
    except ImportError:
        # crew_logic.py not available yet: return mock data
        time.sleep(2)
        return {
            "_demo": True,
            "sentiment": {"positive": 70, "neutral": 20, "negative": 10},
            "pros": ["Great product quality", "Fast delivery"],
            "cons": ["Price is slightly high", "Packaging could be better"],
            "seo_title": f"Buy {name} Online | Best Price & Fast Delivery",
            "seo_description": (
                f"Discover {name}: premium quality, great value, and fast delivery. "
                "Loved by customers. Order yours today!"
            ),
            "keywords": [name.lower(), "best price", "online shopping", "fast delivery"],
            "posts": {
                "Instagram": f"✨ Meet {name}! Quality you can feel. Tap the link in bio to order. #NewArrival #ShopNow",
                "Facebook": f"Introducing {name}. Premium quality, fast delivery. Order now!",
                "X (Twitter)": f"{name} is here 🔥 Grab yours today! #Sale",
            },
        }


# ---------- Sidebar (inputs) ----------
with st.sidebar:
    st.header("📦 Product Details")
    name = st.text_input("Product Name", placeholder="e.g. Wireless Earbuds")
    desc = st.text_area("Short Description", height=90)
    tone = st.selectbox("Brand Tone", ["Professional", "Friendly", "Luxury", "Funny"])
    uploaded = st.file_uploader("Upload reviews file (.txt / .csv)", type=["txt", "csv"])
    reviews = st.text_area("Or paste reviews here", height=150)
    if uploaded:
        reviews = uploaded.read().decode("utf-8")
    go = st.button("🚀 Generate", type="primary")

# ---------- Run ----------
if go:
    if not name or not reviews.strip():
        st.warning("Product name and reviews are required.")
    else:
        with st.status("Agents are working...", expanded=True) as status:
            st.write("🔍 Review Analyst agent is running...")
            st.write("✍️ SEO Writer agent is running...")
            st.write("📣 Social Media agent is running...")
            try:
                st.session_state["result"] = run_agents(name, desc, reviews, tone)
                status.update(label="Done! ✅", state="complete")
            except Exception as e:
                status.update(label="Something went wrong", state="error")
                st.error(f"Error: {e}")

# ---------- Output ----------
res = st.session_state.get("result")
if res:
    if res.get("_demo"):
        st.caption("⚠️ Demo mode: showing sample data (CrewAI backend not connected yet).")

    tab1, tab2, tab3 = st.tabs(["📊 Review Analysis", "🔎 SEO Description", "📱 Social Posts"])

    with tab1:
        s = res["sentiment"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Positive", f"{s['positive']}%")
        c2.metric("Neutral", f"{s['neutral']}%")
        c3.metric("Negative", f"{s['negative']}%")
        st.bar_chart(s)
        a, b = st.columns(2)
        with a:
            st.subheader("👍 Pros")
            for p in res["pros"]:
                st.markdown(f'<div class="card">{p}</div>', unsafe_allow_html=True)
        with b:
            st.subheader("👎 Cons")
            for c in res["cons"]:
                st.markdown(f'<div class="card">{c}</div>', unsafe_allow_html=True)

    with tab2:
        st.text_input("SEO Title", res["seo_title"])
        st.text_area("Meta / Product Description", res["seo_description"], height=160)
        st.write("**Keywords:** " + " • ".join(res["keywords"]))

    with tab3:
        for platform, text in res["posts"].items():
            st.subheader(platform)
            st.code(text, language=None)  # copy button is built in

    report = (
        f"SEO Title: {res['seo_title']}\n{res['seo_description']}\n\n"
        + "\n\n".join(f"[{k}]\n{v}" for k, v in res["posts"].items())
    )
    st.download_button("⬇️ Download Report", report, file_name="report.txt")
else:
    st.info("👈 Fill in the product details in the sidebar and click Generate.")
