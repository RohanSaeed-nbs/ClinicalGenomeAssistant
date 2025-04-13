import streamlit as st
import requests
import re
import json
# Helper for genome variation validation (currently unused)
def validate_and_breakdown_genome_variation(user_query):
    pattern = re.compile(r"""
        (?P<refseq>NM_\d+\.\d+)               
        \((?P<gene>[A-Za-z0-9]+)\)            
        :
        (?P<cdna>                              
            c\.
            (?:
                \d+[A-Z]>[A-Z] |               
                \d+del[A-Z]* |                 
                \d+dup[A-Z]* |                 
                \d+_\d+ins[A-Z]+ |             
                \d+_\d+delins[A-Z]+            
            )
        )
        \s*                                    
        \(?p\.
        (?P<protein>                           
            [A-Za-z]{3}\d+[A-Za-z]{3}(fs)?     
        )
        \)?                                    
    """, re.VERBOSE | re.DOTALL)

    return bool(pattern.search(user_query))

st.set_page_config(page_title="Genomics AI Assistant", layout="centered")

st.title("🧬 Clinical Genomics AI Assistant")

# --- Patient Input Form ---
with st.form("patient_form"):
    st.header("1. Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        patient_id = st.text_input("Case Id")
        age = st.text_input("Age")
        ethnicity = st.text_input("Ethnicity (optional)")
    with col2:
        family_history = st.text_input("Family History")
        sex = st.selectbox("Biological Sex", ["Male", "Female", "Other"])
        symptoms = st.text_input("Symptoms")

    st.divider()
    st.header("2. Genetic Data Input")
    raw_sequence = st.text_area("Input Genome Variation in HVGS Format")

    st.divider()
    st.header("3. Choose Action")
    action = st.radio("What do you want the AI to do?", ["Search Genome Variation", "Suggest Clinical Significance"])

    submitted = st.form_submit_button("Submit", use_container_width=True)

# --- Handle Patient Submission ---
if submitted:
    if not raw_sequence:
        st.error("Please input genome variation.")
    elif not all([patient_id, age, family_history, symptoms]):
        st.error("Fill in all required fields.")
    else:
        history = f"{age} years old {ethnicity or ''} {sex or ''}. "
        if family_history.lower() != "none":
            history += f"Family history of {family_history}. "
        if symptoms.lower() != "none":
            history += f"Symptoms include {symptoms}."

        st.session_state['submitted_data'] = {
            "case_id": patient_id,
            "age": age,
            "ethnicity": ethnicity,
            "sex": sex,
            "family_history": family_history,
            "symptoms": symptoms,
            "action": action,
            "sequence": raw_sequence,
            "history": history
        }

        try:
            response = requests.post("http://backend:5000/api/genome_search_or_diagnose")  
            ai_response = response.json() if response.status_code == 200 else {}
            st.session_state["ai_response"] = ai_response
            st.success("✅ Submitted successfully!")
        except Exception as e:
            st.error(f"Backend error: {e}")
            st.stop()

# --- Display After Submit ---
if "submitted_data" in st.session_state and "ai_response" in st.session_state:
    data = st.session_state["submitted_data"]
    ai_response = st.session_state["ai_response"]

    st.subheader("📋 Patient Summary")
    st.markdown(f"**Patient ID**: {data['case_id']}")
    st.markdown(f"**Age**: {data['age']}")
    st.markdown(f"**Sex**: {data['sex']}")
    st.markdown(f"**Ethnicity**: {data['ethnicity'] or 'Not provided'}")
    st.markdown(f"**Family Medical History**: {data['family_history']}")
    st.markdown(f"**Symptoms**: {data['symptoms']}")
    st.markdown(f"**Selected Action**: {data['action']}")

    st.subheader("🧬 Genome Variation")
    st.code(data["sequence"][:500] + ("..." if len(data["sequence"]) > 500 else ""), language="text")

    st.subheader("🧠 AI Assistant Response")
    if data["action"] == "Suggest Clinical Significance":
        st.markdown(ai_response.get("Answer", "No answer returned."))

        st.subheader("🧬 Genomic Variation")
        st.markdown(f"**Variation**: {ai_response.get('Genome_variation', '')}")

        st.subheader("🩺 Associated Conditions")
        diseases = ai_response.get("Associated_Desieases", "").split(",")
        for d in diseases:
            st.markdown(f"- {d.strip()}")

        st.subheader("📋 Patient History")
        st.markdown(ai_response.get("patient_history", ""))

    st.subheader("📚 Sources")
    for source in ai_response.get("Sources", []):
        if isinstance(source, dict):
            st.markdown(f"**Source**: {source.get('source', '')}")
            st.markdown(f"**ID**: {source.get('id', '')}")
            st.markdown(f"**Summary**: {source.get('text', '')}")

            meta = source.get("metadata", {})
            if isinstance(meta, dict):
                with st.expander("Metadata", expanded=True):
                    st.markdown(f"**Gene**: {meta.get('GeneSymbol', '')}")
                    st.markdown(f"**Type**: {meta.get('Type', '')}")
                    st.markdown(f"**Clinical Significance**: {meta.get('ClinicalSignificance', '')}")
                    st.markdown(f"**Phenotypes**: {', '.join(meta.get('PhenotypeList', []))}")
                    st.markdown(f"**Review Status**: {meta.get('ReviewStatus', '')}")
                    st.markdown(f"**Assembly**: {meta.get('Assembly', '')}")
                    st.markdown(f"**Location**: Chr{meta.get('Chromosome', '')}:{meta.get('Start', '')}-{meta.get('Stop', '')}")
                    st.markdown(f"**Ref/Alt**: {meta.get('ReferenceAllele', '')} → {meta.get('AlternateAllele', '')}")
            st.divider()

    # --- Confirmation Form (SECOND FORM) ---
    if data["action"] == "Suggest Clinical Significance" :
        st.subheader("📝 Confirm Clinical Significance")
        with st.form("confirm_significance_form"):
            significance_response = st.radio(
                "Do you accept the clinical significance provided by the AI?",
                ["Accept", "Decline"],
                horizontal=True
            )
            confirm_submitted = st.form_submit_button("Confirm")

        if confirm_submitted:
            try:
                # Use .copy() to avoid mutation issues and ensure clean serialization
                confirm_payload = {
                    "decision": significance_response,
                    "ai_response": json.loads(json.dumps(ai_response)),  # Ensures serialization
                    "submitted_data": json.loads(json.dumps(st.session_state.get("submitted_data", {})))
                }

                response = requests.post(
                    "http://backend:5000/api/diagnosis_confirmation",
                    json=confirm_payload,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    st.success(f"✅ You chose to **{significance_response}** the clinical significance.")
                else:
                    st.error(f"❌ Backend responded with {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"Failed to send confirmation: {e}")
