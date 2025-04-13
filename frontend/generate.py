import streamlit as st
import pandas as pd
from io import StringIO
import requests

st.set_page_config(page_title="Genomics AI Assistant", layout="centered")

st.title("🧬 Clinical Genomics AI Assistant")

with st.form("patient_form"):
    st.header("🔹 Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name")
        dob = st.date_input("Date of Birth")
        ethnicity = st.text_input("Ethnicity (optional)")
    with col2:
        last_name = st.text_input("Last Name")
        sex = st.selectbox("Biological Sex", ["Male", "Female", "Other"])

    st.divider()

    st.header("🧬 Genetic Data Input")
    input_type = st.radio(
        "How do you want to enter genetic data?",
        ["Paste Sequence", "Enter Variants", "Upload File"]
    )

    genome_build = st.selectbox("Genome Build", ["GRCh37", "GRCh38"])

    raw_sequence = ""
    variants_df = None
    uploaded_file = None
    variants_csv = ""

    if input_type == "Paste Sequence":
        raw_sequence = st.text_area("Paste DNA Sequence (FASTA/Raw)", height=150)

    elif input_type == "Enter Variants":
        st.caption("Enter variants as CSV: Chromosome,Position,Reference,Alternate,Zygosity")
        variants_csv = st.text_area("Paste Variant Table (CSV)", height=150)

    else:
        uploaded_file = st.file_uploader("Upload Genetic File", type=["vcf", "fasta", "bam", "fastq"])

    st.divider()

    st.header("⚙️ Choose Action")
    action = st.radio("What do you want the AI to do?", ["Search Genetic Sequence", "Diagnose and Provide Citation"])

  
    submitted = st.form_submit_button("Submit")

# ⬇️ Post-submit logic outside the form
if submitted:
    response = requests.get("http://localhost:5000/api/search")
    ai_response = response.json()
    st.success("✅ Submitted successfully!")

    st.subheader("📋 Patient Summary")
    st.markdown(f"**Name**: {first_name} {last_name}")
    st.markdown(f"**DOB**: {dob}")
    st.markdown(f"**Sex**: {sex}")
    st.markdown(f"**Ethnicity**: {ethnicity or 'Not provided'}")
    st.markdown(f"**Genome Build**: {genome_build}")
    st.markdown(f"**Selected Action**: {action}")

    st.subheader("🧬 Genetic Input")
    if input_type == "Paste Sequence":
        st.code(raw_sequence[:500] + ("..." if len(raw_sequence) > 500 else ""), language="text")

    elif input_type == "Enter Variants":
        try:
            variants_df = pd.read_csv(StringIO(variants_csv))
            st.dataframe(variants_df)
        except Exception as e:
            st.error("❌ Invalid CSV input. Please format it correctly.")

    else:
        if uploaded_file:
            st.write(f"Uploaded file: `{uploaded_file.name}`")
        else:
            st.warning("No file uploaded.")

    st.divider()
    st.subheader("🧠 AI Assistant Response")

    if action == "Search Genetic Sequence":
        st.info("🔍 Searching sequence in the known database... [This is a placeholder for search logic]")
    else:
        st.info("🧬 Running diagnosis and generating citations... [This is a placeholder for AI diagnostic output]")

    st.subheader("🧠 AI Interpretation")
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
        st.markdown(f"{source['text']}")

    meta = source["metadata"]
    with st.expander("🔎 Metadata Details"):
        st.markdown(f"**Gene**: {meta['GeneSymbol']}")
        st.markdown(f"**Type**: {meta['Type']}")
        st.markdown(f"**Clinical Significance**: {meta['ClinicalSignificance']}")
        st.markdown(f"**Phenotypes**: {', '.join(meta['PhenotypeList'])}")
        st.markdown(f"**Review Status**: {meta['ReviewStatus']}")
        st.markdown(f"**Assembly**: {meta['Assembly']}")
        st.markdown(f"**Location**: Chr{meta['Chromosome']}:{meta['Start']}-{meta['Stop']}")
        st.markdown(f"**Ref/Alt**: {meta['ReferenceAllele']} → {meta['AlternateAllele']}")

