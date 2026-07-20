"""Streamlit UI for the layered Review Analytics application."""

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import config  # noqa: E402
from database.db_manager import (  # noqa: E402
    get_summaries_by_category,
    get_summary_by_id,
    init_db,
    clear_summaries,
    save_summary,
)
from services.gemini_service import analyze_review_sentiment  # noqa: E402


st.set_page_config(page_title="Review Analyst Pro", page_icon="📈", layout="wide")
init_db()

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "new_analysis"
if "selected_summary_id" not in st.session_state:
    st.session_state.selected_summary_id = None


def format_timestamp(value: str) -> str:
    """Format SQLite timestamps without assuming fractional seconds."""
    try:
        return datetime.fromisoformat(str(value)).strftime("%b %d, %H:%M")
    except ValueError:
        return str(value)


def show_result(filename: str, summary: str, rating: int, category: str) -> None:
    """Render a saved or newly-created analysis consistently."""
    st.subheader(filename)
    metric_col, category_col = st.columns([1, 4])
    metric_col.metric("Overall rating", f"{rating} / 10")
    if category == "Good":
        category_col.success("Positive customer sentiment — Good category")
    elif category == "Average":
        category_col.warning("Mixed customer sentiment — Average category")
    else:
        category_col.error("Critical customer sentiment — Bad category")
    st.markdown("### Synthesis summary")
    st.markdown(summary)


with st.sidebar:
    st.title("📁 Navigation & History")
    if st.button("🔄 Refresh history", use_container_width=True,
                 help="Reload saved summaries from SQLite and clear Streamlit caches."):
        # The database layer currently reads SQLite on every call, but clearing
        # Streamlit caches here also makes this safe if cached queries/resources
        # are added later. Rerunning rebuilds the sidebar from the latest DB.
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

    if st.button("🗑️ Wipe database", use_container_width=True,
                 help="Permanently delete every saved review summary."):
        clear_summaries()
        st.session_state.view_mode = "new_analysis"
        st.session_state.selected_summary_id = None
        st.success("All saved summaries were deleted.")
        st.rerun()

    if st.button("➕ Analyze New Reviews", type="primary", use_container_width=True):
        st.session_state.view_mode = "new_analysis"
        st.session_state.selected_summary_id = None
        st.rerun()

    st.divider()
    st.subheader("Filter Past Summaries")
    categories = {
        "🟢 Good (8–10)": "Good",
        "🟡 Average (4–7)": "Average",
        "🔴 Bad (0–3)": "Bad",
    }
    for label, db_category in categories.items():
        with st.expander(label):
            records = get_summaries_by_category(db_category)
            if not records:
                st.caption("No historical records found.")
            for record_id, filename, timestamp in records:
                button_label = f"📄 {filename} ({format_timestamp(timestamp)})"
                if st.button(
                    button_label, key=f"record_{record_id}", use_container_width=True
                ):
                    st.session_state.view_mode = "view_past"
                    st.session_state.selected_summary_id = record_id
                    st.rerun()


if (
    st.session_state.view_mode == "view_past"
    and st.session_state.selected_summary_id is not None
):
    record = get_summary_by_id(st.session_state.selected_summary_id)
    if record:
        filename, summary, rating, category, created_at = record
        st.title("📜 Archived Review Analysis")
        st.caption(f"Analyzed on {created_at} · Category: {category}")
        show_result(filename, summary, rating, category)
    else:
        st.error("The selected historical record could not be found.")
else:
    st.title("📊 Customer Review Analytics Engine")
    st.caption(f"Gemini model: **{config.GEMINI_MODEL}**")
    st.write(
        "Upload a UTF-8 text file containing customer feedback. The app will "
        "summarize it, assign a 0–10 sentiment rating, and save the result."
    )

    if not config.GEMINI_API_KEY:
        st.warning(
            "GEMINI_API_KEY is not configured. You can browse history, but must "
            "configure the key before running a new analysis."
        )

    uploaded_file = st.file_uploader("Upload customer reviews", type=["txt"])
    if uploaded_file is not None:
        try:
            review_text = uploaded_file.getvalue().decode("utf-8")
            if not review_text.strip():
                st.error("The uploaded review file is empty.")
            else:
                with st.expander("Review file preview"):
                    st.text(review_text)
                if st.button(
                    "🚀 Execute Sentiment Analysis",
                    type="primary",
                    use_container_width=True,
                ):
                    with st.spinner("Gemini is analyzing the reviews..."):
                        summary, rating, category = analyze_review_sentiment(review_text)
                        record_id = save_summary(
                            uploaded_file.name, summary, rating, category
                        )
                    st.success(
                        f"Analysis saved under the {category} category "
                        f"(record #{record_id})."
                    )
                    show_result(uploaded_file.name, summary, rating, category)
        except UnicodeDecodeError:
            st.error("The uploaded file must use UTF-8 text encoding.")
        except (ValueError, RuntimeError) as error:
            st.error(str(error))
        except Exception as error:
            st.error(f"Analysis failed: {error}")
