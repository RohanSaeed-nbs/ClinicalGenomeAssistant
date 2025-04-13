import streamlit as st
import requests

st.set_page_config(page_title="Genomics AI Assistant", layout="centered")

st.title("🧬 Clinical Genomics AI Assistant")

with st.form("patient_form"):
    st.header("🔹 Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        patient_id = st.text_input("Patient Id")
        dob = st.date_input("Date of Birth")
        ethnicity = st.text_input("Ethnicity (optional)")
    with col2:
        family_history = st.text_input("Family History")
        sex = st.selectbox("Biological Sex", ["Male", "Female", "Other"])
        symptoms = st.text_input("Symptoms")

    st.divider()

    st.header("🧬 Genetic Data Input")
    raw_sequence = st.text_area("Input Genome Variation in HVGS Format", height=150)

    st.divider()

    st.header("⚙️ Choose Action")
    action = st.radio("What do you want the AI to do?", ["Search Genome Variation", "Suggest Clinical Signficance"])

  
    submitted = st.form_submit_button("Submit")

#  Post-submit logic outside the form
if submitted:
    response = requests.get("http://backend:5000/api/search")
    ai_response = response.json()
    st.success("✅ Submitted successfully!")

    st.subheader("📋 Patient Summary")
    st.markdown(f"**Patient ID**: {patient_id}")
    st.markdown(f"**DOB**: {dob}")
    st.markdown(f"**Sex**: {sex}")
    st.markdown(f"**Ethnicity**: {ethnicity or 'Not provided'}")
    st.markdown(f"**Family Medical History**: {family_history}")
    st.markdown(f"**Symptoms**: {symptoms}")
    st.markdown(f"**Selected Action**: {action}")

    st.subheader("🧬 Genome Variation")
    st.code(raw_sequence[:500] + ("..." if len(raw_sequence) > 500 else ""), language="text")
    st.divider()

    st.subheader("🧠 AI Assistant Response")
    
    if action == "Suggest Clinical Signficance":
        st.markdown(ai_response["Answer"])
        st.subheader("🧬 Genomic Variation")
        st.markdown(f"**Variation**: {ai_response['Genome_variation']}")

        st.subheader("🩺 Associated Conditions")
        diseases = ai_response["Associated_Desieases"].split(",")
        for d in diseases:
            st.markdown(f"- {d.strip()}")

        st.subheader("📋 Patient History")
        st.markdown(ai_response["patient_history"])

    st.subheader("📚 Sources")
    for source in ai_response["Sources"]:
        st.markdown(f"**Source**: {source['source']}")
        st.markdown(f"**ID**: {source['id']}")
        st.markdown(f"**Summary**: {source['text']}")

        meta = source["metadata"]
        with st.expander("🔎 **See Metadata**"):
            st.markdown(f"**Gene**: {meta['GeneSymbol']}")
            st.markdown(f"**Type**: {meta['Type']}")
            st.markdown(f"**Clinical Significance**: {meta['ClinicalSignificance']}")
            st.markdown(f"**Phenotypes**: {', '.join(meta['PhenotypeList'])}")
            st.markdown(f"**Review Status**: {meta['ReviewStatus']}")
            st.markdown(f"**Assembly**: {meta['Assembly']}")
            st.markdown(f"**Location**: Chr{meta['Chromosome']}:{meta['Start']}-{meta['Stop']}")
            st.markdown(f"**Ref/Alt**: {meta['ReferenceAllele']} → {meta['AlternateAllele']}")

        st.divider()
    if action == "Suggest Clinical Signficance":
        st.subheader("📝 Confirm Clinical Significance")

        with st.form("confirm_significance_form"):
            significance_response = st.radio(
                "Do you accept the clinical significance provided by the AI?",
                ["Accept", "Decline"],
                horizontal=True
            )

            justification = st.text_area(
                "Optional Comment or Justification (if declined)",
                placeholder="Provide details if you are declining the AI's conclusion..."
            )

            confirm_submitted = st.form_submit_button("Confirm")

        # 👇 Process the confirmation
        if confirm_submitted:
            clinical_significance_response = {
                "decision": significance_response,
                "justification": justification
        }

            st.success(f"✅ You chose to **{significance_response}** the clinical significance.")

            if significance_response == "Decline" and justification.strip() == "":
                st.warning("⚠️ You declined the result, but didn't provide a justification.")

            requests.post("http://localhost:5000/api/confirmation", json=clinical_significance_response)
        
        
    