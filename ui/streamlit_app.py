import streamlit as st
import pandas as pd
import sys
import os
import pickle
import glob
import json
import asyncio
from datetime import datetime

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipelines.baseline_pipeline import run_baseline_pipeline
from pipelines.optimized_pipeline import run_optimized_pipeline

st.set_page_config(page_title="Insurance Pricing Analysis System", layout="wide")

st.title("Insurance Pricing Analysis System")
st.markdown("*Decision Support for Pricing Analysts, Underwriters, and Audit Teams*")

# --- Custom CSS to Hide Avatars ---
st.markdown("""
<style>
    /* Hide the chat avatars (robot and user face icons) */
    [data-testid="stChatMessageAvatarUser"], 
    [data-testid="stChatMessageAvatarAssistant"],
    .st-emotion-cache-1pxm8y1, 
    .st-emotion-cache-p4mowd {
        display: none !important;
    }
    /* Adjust spacing since avatar is gone */
    [data-testid="stChatMessage"] {
        padding-left: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Tabs ---
tab_copilot, tab_eval = st.tabs(["Pricing Analysis Engine", "System Evaluation Dashboard"])

# --- TAB 1: PRICING COPILOT ---
with tab_copilot:
    # --- Sidebar for Context ---
    with st.sidebar:
        st.header("1. Profile Input")
        age = st.number_input("Age", 18, 100, 30, key="age_input")
        postcode_risk = st.slider("Postcode Risk (0.0=Low, 1.0=High)", 0.0, 1.0, 0.5, key="risk_slider")
        vehicle_group = st.number_input("Vehicle Group (1-50)", 1, 50, 20, key="vg_input")
        claims_count = st.number_input("Claims (Last 5y)", 0, 10, 0, key="claims_input")
        ncb_years = st.number_input("NCB Years", 0, 20, 5, key="ncb_input")

        profile = {
            "age": age,
            "postcode_risk": postcode_risk,
            "vehicle_group": vehicle_group,
            "claims_count": claims_count,
            "ncb_years": ncb_years
        }
        
        st.divider()
        st.header("2. Analysis Scenarios")
        
        persona = st.selectbox(
            "Select User Persona:",
            ["Pricing Analyst (Technical)", "Underwriter (Rules/Guidelines)", "Audit/Governance (Evidence)"],
            key="persona_select"
        )
        
        sample_q = ""
        if persona == "Pricing Analyst (Technical)":
            sample_q = st.radio(
                "Select Query:",
                [
                    "Analyze the key feature contributions (SHAP) for this price.",
                    "Compare this pricing output against the baseline model behavior.",
                    "Identify any anomalies in feature values compared to historical quotes."
                ],
                key="qa_radio"
            )
        elif persona == "Underwriter (Rules/Guidelines)":
            sample_q = st.radio(
                "Select Query:",
                [
                    "Does this premium align with the vehicle group underwriting guidelines?",
                    "Explain the high premium citation for this risk profile.",
                    "Are there any blocking rules for this age group?"
                ],
                key="ug_radio"
            )
        elif persona == "Audit/Governance (Evidence)":
            sample_q = st.radio(
                "Select Query:",
                [
                    "Generate pricing evidence report: Model output + Guidelines + SHAP.",
                    "Validate that postcode risk usage complies with regional policy.",
                    "Show historical consistency for this segment."
                ],
                key="ag_radio"
            )
            
        if st.button("Run Analysis", key="run_btn"):
            st.session_state.current_query = sample_q
            st.session_state.trigger_run = True

    # --- Chat Interface ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "comparison":
             with st.chat_message("assistant", avatar=None):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### Baseline Implementation")
                    st.markdown(message["base"])
                with c2:
                    st.markdown("### Optimized Architecture")
                    st.markdown(message["opt"])
                
                st.markdown(message["metrics"])
        else:
            with st.chat_message(message["role"], avatar=None):
                st.markdown(message["content"])

    # --- Input Handling ---
    query = st.chat_input("Enter custom internal query...")
    if query:
        st.session_state.current_query = query
        st.session_state.trigger_run = True

    if st.session_state.get("trigger_run", False):
        query_text = st.session_state.current_query
        
        st.chat_message("user", avatar=None).markdown(query_text)
        st.session_state.messages.append({"role": "user", "content": query_text})
        
        with st.chat_message("assistant", avatar=None):
            col1, col2 = st.columns(2)
            
            base_res = None
            opt_res = None
            
            with col1:
                 st.subheader("Baseline Implementation")
                 with st.spinner("Processing..."):
                    try:
                        base_res = run_baseline_pipeline(profile, query_text)
                        st.success(f"Execution Completed ({base_res['metrics']['total_latency']:.2f}s)", icon=None)
                        st.markdown(base_res['explanation'])
                    except Exception as e:
                        st.error(f"Error encountered: {e}")

            with col2:
                 st.subheader("Optimized Architecture")
                 with st.spinner("Processing..."):
                    try:
                        opt_res = run_optimized_pipeline(profile, query_text)
                        st.success(f"Execution Completed ({opt_res['metrics']['total_latency']:.2f}s)", icon=None)
                        st.markdown(opt_res['explanation'])
                    except Exception as e:
                        st.error(f"Error encountered: {e}")
            
            # Build Metrics Table
            metrics_md = ""
            if base_res and opt_res:
                base_metrics = base_res['metrics']
                opt_metrics = opt_res['metrics']
                
                metrics_md = "\n\n---\n### System Telemetry Report\n"
                metrics_md += "| Metric | Baseline Implementation | Optimized Architecture |\n"
                metrics_md += "| :--- | :--- | :--- |\n"
                metrics_md += f"| Total Latency | {base_metrics.get('total_latency', 0):.2f}s | {opt_metrics.get('total_latency', 0):.2f}s |\n"
                metrics_md += f"| **Semantic Cache Check** | N/A | {opt_metrics.get('semantic_cache_latency', 0):.4f}s |\n"
                metrics_md += f"| Vector Search | {base_metrics.get('vector_search_latency', 0):.2f}s | {opt_metrics.get('vector_search_latency', 0):.2f}s |\n"
                metrics_md += f"| Pricing/SHAP | {base_metrics.get('pricing_model_latency', 0):.2f}s | {opt_metrics.get('pricing_model_latency', 0):.2f}s |\n"
                metrics_md += f"| LLM Gen Time | {base_metrics.get('llm_latency', 0):.2f}s | {opt_metrics.get('llm_latency', 0):.2f}s |\n"
                metrics_md += f"| Prompt Tokens | {base_metrics.get('llm_prompt_tokens', 0)} | {opt_metrics.get('llm_prompt_tokens', 0)} |\n"
                metrics_md += f"| Output Tokens | {base_metrics.get('llm_tokens_generated', 0)} | {opt_metrics.get('llm_tokens_generated', 0)} |\n"
                
                calc_tps = lambda tokens, dur: f"{tokens / dur:.1f}" if dur > 0 else "0.0"
                base_tps = calc_tps(base_metrics.get('llm_tokens_generated', 0), base_metrics.get('eval_duration', 0))
                metrics_md += f"| Tokens/Sec (TPS) | {base_tps} | "
                opt_tps = calc_tps(opt_metrics.get('llm_tokens_generated', 0), opt_metrics.get('eval_duration', 0))
                metrics_md += f"{opt_tps} |\n"
                
                metrics_md += f"| Time to First Token | {base_metrics.get('prompt_eval_duration', 0):.2f}s | {opt_metrics.get('prompt_eval_duration', 0):.2f}s |\n"
                metrics_md += f"| RAG Calls | {base_metrics.get('rag_calls', 0)} | {opt_metrics.get('rag_calls', 0)} |\n"
                metrics_md += f"| Tool Calls | {base_metrics.get('tool_calls', 0)} | {opt_metrics.get('tool_calls', 0)} |\n"
                
                if opt_metrics['total_latency'] > 0:
                    speedup = base_metrics['total_latency'] / opt_metrics['total_latency']
                    metrics_md += f"\n**Performance Improvement Factor:** {speedup:.1f}x Speed Increase"
                
                st.markdown(metrics_md)
                
                st.session_state.messages.append({
                    "role": "comparison", 
                    "base": base_res['explanation'], 
                    "opt": opt_res['explanation'],
                    "metrics": metrics_md
                })

        st.session_state.trigger_run = False

# --- TAB 2: EVALUATION DASHBOARD ---
with tab_eval:
    st.header("Pipeline Architecture Benchmarking")
    st.markdown("Comparative analysis of the **Baseline Implementation** vs. **Optimized Compound System**.")

    # --- Action Buttons ---
    if st.button("Run Full Architecture Benchmark", width='stretch'):
        with st.status("Executing Comparative Benchmark Suite...", expanded=True) as status:
            from evaluation.eval_pipeline import run_pipeline_evaluation
            
            st.write("1. Benchmarking Baseline Pipeline...")
            base_res = asyncio.run(run_pipeline_evaluation("baseline"))
            
            st.write("2. Benchmarking Optimized Pipeline...")
            opt_res = asyncio.run(run_pipeline_evaluation("optimized"))
            
            if "error" in base_res or "error" in opt_res:
                st.error("Benchmark failed for one or more architectures.")
                status.update(label="Benchmark Failed!", state="error")
            else:
                st.success("Comparative benchmark complete.")
                status.update(label="Benchmark Successful!", state="complete", expanded=False)
                st.rerun()

    st.divider()
    
    # --- Load Latest Reports ---
    reports_base = glob.glob('evaluation/reports/eval_baseline_*.json')
    reports_opt = glob.glob('evaluation/reports/eval_optimized_*.json')
    
    col_left, col_right = st.columns(2)
    
    # Left Column: Baseline
    with col_left:
        st.subheader("Baseline Implementation")
        if reports_base:
            latest_base = max(reports_base, key=os.path.getctime)
            with open(latest_base, 'r') as f:
                base_report = json.load(f)
            
            summary = base_report.get('summary', {})
            st.caption(f"Latest Baseline Report: {os.path.basename(latest_base)}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Concept Coverage", f"{summary.get('avg_concept_coverage', 0)*100:.1f}%")
            c2.metric("Driver Accuracy", f"{summary.get('key_driver_accuracy', 0)*100:.1f}%")
            c3.metric("Avg Latency", f"{summary.get('avg_latency', 0):.2f}s")
            
            if 'judge_avg_professionalism' in summary:
                st.markdown("**Analyst Assessment (Scale 1-5):**")
                j1, j2, j3 = st.columns(3)
                j1.metric("Prof.", f"{summary.get('judge_avg_professionalism', 0):.1f}")
                j2.metric("Clarity", f"{summary.get('judge_avg_clarity', 0):.1f}")
                j3.metric("Safety", f"{summary.get('judge_avg_safety', 0):.1f}")
            
            with st.expander("Show Baseline Feedback"):
                for entry in base_report.get('detailed_results', []):
                    if 'judge_metrics' in entry:
                         st.markdown(f"**Case {entry['case_id']}**")
                         st.write(f"Explanation: {entry['explanation']}")
                         st.divider()
        else:
            st.info("No baseline results available. Run benchmark to generate.")

    # Right Column: Optimized
    with col_right:
        st.subheader("Optimized Architecture")
        if reports_opt:
            latest_opt = max(reports_opt, key=os.path.getctime)
            with open(latest_opt, 'r') as f:
                opt_report = json.load(f)
            
            summary = opt_report.get('summary', {})
            st.caption(f"Latest Optimized Report: {os.path.basename(latest_opt)}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Concept Coverage", f"{summary.get('avg_concept_coverage', 0)*100:.1f}%")
            c2.metric("Driver Accuracy", f"{summary.get('key_driver_accuracy', 0)*100:.1f}%")
            c3.metric("Avg Latency", f"{summary.get('avg_latency', 0):.2f}s")
            
            if 'judge_avg_professionalism' in summary:
                st.markdown("**Analyst Assessment (Scale 1-5):**")
                j1, j2, j3 = st.columns(3)
                j1.metric("Prof.", f"{summary.get('judge_avg_professionalism', 0):.1f}")
                j2.metric("Clarity", f"{summary.get('judge_avg_clarity', 0):.1f}")
                j3.metric("Safety", f"{summary.get('judge_avg_safety', 0):.1f}")

            with st.expander("Show Optimized Feedback"):
                for entry in opt_report.get('detailed_results', []):
                    if 'judge_metrics' in entry:
                         st.markdown(f"**Case {entry['case_id']}**")
                         st.write(f"Explanation: {entry['explanation']}")
                         st.divider()
        else:
            st.info("No optimized results available. Run benchmark to generate.")

    st.divider()
    st.subheader("Comparison Analysis")
    if reports_base and reports_opt:
        b_sum = base_report['summary']
        o_sum = opt_report['summary']
        
        latency_diff = b_sum['avg_latency'] - o_sum['avg_latency']
        if o_sum['avg_latency'] > 0:
            speedup = b_sum['avg_latency'] / o_sum['avg_latency']
            st.write(f"The **Optimized Architecture** is **{speedup:.1f}x faster** than the baseline.")
        
        acc_diff = (o_sum['key_driver_accuracy'] - b_sum['key_driver_accuracy']) * 100
        if acc_diff > 0:
            st.write(f"Decision accuracy improved by **{acc_diff:.1f}%**.")
        elif acc_diff < 0:
             st.write(f"Decision accuracy decreased by **{abs(acc_diff):.1f}%**.")
        else:
            st.write("Decision accuracy remained consistent between architectures.")
    else:
        st.info("Run full benchmark to see comparison analysis.")
