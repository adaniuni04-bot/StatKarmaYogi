import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.core.security import get_password_hash
from app.models.users import User, Department, Designation
from app.models.competencies import (
    CompetencyDomain,
    Competency,
    SubCompetency,
    CompetencyLevel,
    RoleCompetency,
    UserCompetency,
    CompetencyHistory,
)
from app.models.resources import Resource, ResourceCompetency, TrainingProgramme
from app.models.assessments import Assessment, Question, QuestionOption
from app.models.learning import LearningPath, LearningPathItem
from app.models.documents import Document, DocumentChunk
from app.models.future_skills import FutureSkill
from app.services.ai.factory import get_embedding_provider
from app.services.skill_gap.engine import evaluate_user_skill_gaps


def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "employee@example.com").first():
            print("[INFO] Database already contains seed data. Refreshing dynamic gap caches...")
            emp = db.query(User).filter(User.email == "employee@example.com").first()
            evaluate_user_skill_gaps(db, emp.id)
            return

        print("[1/8] Seeding Departments & Designations...")
        fod = Department(name="Field Operations Division (FOD)", code="FOD", description="Executes large-scale socio-economic household surveys across India.")
        sdrd = Department(name="Survey Design and Research Division (SDRD)", code="SDRD", description="Develops survey methodologies, sampling designs, and questionnaires.")
        nad = Department(name="National Accounts Division (NAD)", code="NAD", description="Compiles National Accounts, GDP, Capital Formation, and Macro aggregates.")
        psd = Department(name="Price Statistics Division (PSD)", code="PSD", description="Compiles Consumer Price Index (CPI) and Wholesale Price Index (WPI).")
        db.add_all([fod, sdrd, nad, psd])
        db.flush()

        desig_so = Designation(name="Statistical Officer", code="SO", cadre="Subordinate Statistical Service")
        desig_sso = Designation(name="Senior Statistical Officer", code="SSO", cadre="Subordinate Statistical Service")
        desig_survey = Designation(name="Survey Officer", code="SURVEY_OFF", cadre="Indian Statistical Service")
        desig_da = Designation(name="Data Analyst", code="DATA_ANALYST", cadre="Technical Cadre")
        desig_dir = Designation(name="Director", code="DIR", cadre="Indian Statistical Service")
        db.add_all([desig_so, desig_sso, desig_survey, desig_da, desig_dir])
        db.flush()

        print("[2/8] Seeding Competency Domains & Competencies...")
        dom_stat = CompetencyDomain(code="STATISTICAL", name="Statistical Methods & Operations", description="Core methodology, sampling, survey design, and official standards.")
        dom_tech = CompetencyDomain(code="TECHNICAL", name="Technical & Computational", description="Programming, database systems, geospatial analytics, and AI/ML.")
        dom_gov = CompetencyDomain(code="DIGITAL_GOVERNANCE", name="Digital Governance & Data Security", description="Data privacy, cybersecurity, digital public infrastructure.")
        dom_mgmt = CompetencyDomain(code="BEHAVIOURAL", name="Behavioural & Managerial", description="Leadership, communication, ethics, and project management.")
        db.add_all([dom_stat, dom_tech, dom_gov, dom_mgmt])
        db.flush()

        competencies_data = [
            # Statistical Domain
            ("SAMPLING", "Sampling Techniques & Estimation", dom_stat.id, "Probability sampling, stratification, cluster sampling, PPS, variance calculation.", 1.2),
            ("SURVEY_DESIGN", "Survey Design & Methodology", dom_stat.id, "Instrument design, framing, pilot testing, and non-sampling error control.", 1.1),
            ("DATA_QUALITY", "Data Quality & Assurance (NQAF)", dom_stat.id, "National Quality Assurance Framework principles, validation rules, imputation.", 1.3),
            ("STAT_INFERENCE", "Statistical Inference & Modelling", dom_stat.id, "Hypothesis testing, estimation theory, regression, and confidence intervals.", 1.0),
            ("NATIONAL_ACCOUNTS", "National Accounts & Macro Compilation", dom_stat.id, "SNA 2008 framework, GDP, GVA, supply-use tables, and deflators.", 1.2),
            ("PRICE_STATISTICS", "Price Statistics & Index Numbers", dom_stat.id, "Consumer Price Index (CPI), WPI, Laspeyres/Paasche formulations.", 1.1),
            ("OFFICIAL_STATISTICS", "Fundamental Principles of Official Statistics", dom_stat.id, "UN Fundamental Principles, statistical independence, confidentiality.", 1.2),
            ("SDG_INDICATORS", "SDG Indicators & Tracking", dom_stat.id, "Sustainable Development Goals monitoring, metadata, and state indicators.", 1.1),
            ("DISCLOSURE_CONTROL", "Statistical Disclosure Control", dom_stat.id, "Microdata anonymization, cell suppression, k-anonymity, noise addition.", 1.3),

            # Technical Domain
            ("PYTHON", "Python for Statistical Production", dom_tech.id, "Data wrangling with Pandas, NumPy, Statsmodels, and workflow automation.", 1.2),
            ("SQL", "SQL for Statistical Databases", dom_tech.id, "Relational queries, window functions, indexing, and administrative microdata joins.", 1.2),
            ("GIS", "Geospatial Data Analytics (GIS)", dom_tech.id, "QGIS, coordinate reference systems, spatial joins, thematic mapping.", 1.2),
            ("AI_ML", "AI/ML in Official Statistics", dom_tech.id, "Machine learning for classification, imputation, text mining, satellite data.", 1.5),
            ("DATA_VISUALIZATION", "Data Visualization & Dissemination", dom_tech.id, "Designing intuitive charts, dashboards, thematic maps, and infographics.", 1.0),
            ("BIG_DATA", "Big Data & Cloud Analytics", dom_tech.id, "Distributed computing, scanner data, mobile logs, and cloud pipelines.", 1.4),
            ("R_STATS", "R for Statistical Computing", dom_tech.id, "Survey package in R, complex survey analysis, and reproducible reports.", 1.1),

            # Digital Governance Domain
            ("DATA_PRIVACY", "Data Privacy & Protection", dom_gov.id, "Compliance with DPDP Act, confidential information protection, user consent.", 1.4),
            ("CYBERSECURITY", "Cybersecurity & Information Security", dom_gov.id, "Information security management, endpoint defense, zero trust fundamentals.", 1.3),
            ("DATA_GOVERNANCE", "Statistical Data Governance", dom_gov.id, "Metadata repositories, data catalogs, lineage, standard classifications.", 1.2),

            # Behavioural Domain
            ("COMMUNICATION", "Statistical Communication & Reporting", dom_mgmt.id, "Translating complex statistical metrics into actionable policy briefs.", 1.1),
            ("PROJECT_MANAGEMENT", "Statistical Project Management", dom_mgmt.id, "Field mission planning, budget allocation, schedule monitoring, GSBPM.", 1.0),
            ("ETHICS", "Professional Ethics & Integrity", dom_mgmt.id, "Code of conduct for statistical personnel, transparency, conflict of interest.", 1.3),
            ("PROBLEM_SOLVING", "Analytical Problem Solving", dom_mgmt.id, "Diagnosing field anomalies, inconsistent records, and methodological roadblocks.", 1.0),
        ]

        comp_dict = {}
        for code, name, dom_id, desc, future_rel in competencies_data:
            c = Competency(
                code=code,
                name=name,
                domain_id=dom_id,
                description=desc,
                definition=desc,
                future_relevance=future_rel,
                version="1.0",
                active=True
            )
            db.add(c)
            db.flush()
            comp_dict[code] = c

        print("[3/8] Seeding Role Requirements for Statistical Officer...")
        # Exact requirements matching Master Prompt Section 11 & Section 13:
        so_requirements = [
            ("SAMPLING", 80.0, 1.2, True),
            ("SURVEY_DESIGN", 80.0, 1.1, True),
            ("STAT_INFERENCE", 70.0, 1.0, True),
            ("PYTHON", 60.0, 1.0, True),
            ("SQL", 60.0, 1.1, True),
            ("DATA_VISUALIZATION", 70.0, 1.0, True),
            ("DATA_QUALITY", 75.0, 1.2, True),
            ("GIS", 40.0, 0.9, False),
            ("AI_ML", 50.0, 1.1, False),
            ("COMMUNICATION", 70.0, 1.0, True),
            ("PROJECT_MANAGEMENT", 65.0, 1.0, True),
            ("ETHICS", 80.0, 1.3, True),
        ]

        for c_code, req_score, importance, mandatory in so_requirements:
            if c_code in comp_dict:
                db.add(RoleCompetency(
                    designation_id=desig_so.id,
                    competency_id=comp_dict[c_code].id,
                    required_level=4 if req_score >= 80 else (3 if req_score >= 60 else 2),
                    required_score=req_score,
                    importance=importance,
                    mandatory=mandatory,
                    future_relevance=comp_dict[c_code].future_relevance
                ))
        db.flush()

        print("[4/8] Seeding Demo Users (Rahul, Priya, Rajesh)...")
        # Employee 1: Rahul Sharma (Statistical Officer)
        rahul = User(
            email="employee@example.com",
            password_hash=get_password_hash("demo123"),
            first_name="Rahul",
            last_name="Sharma",
            role="EMPLOYEE",
            designation_id=desig_so.id,
            designation_name="Statistical Officer",
            department_id=fod.id,
            years_experience=4,
            education="M.Sc. Statistics, University of Delhi",
            current_assignment="Periodic Labour Force Survey (PLFS) & Household Consumption",
            career_goal="Senior Statistical Officer (SDRD / Methodology Division)",
            preferred_language="en",
            status="ACTIVE"
        )

        # Employee 2: Priya Patel (Trainer / Survey Officer)
        priya = User(
            email="trainer@example.com",
            password_hash=get_password_hash("demo123"),
            first_name="Priya",
            last_name="Patel",
            role="TRAINER",
            designation_id=desig_survey.id,
            designation_name="Survey Officer",
            department_id=sdrd.id,
            years_experience=8,
            education="M.Stat, Indian Statistical Institute (ISI) Kolkata",
            current_assignment="Lead Faculty for Sampling Techniques, NSSTA",
            career_goal="Joint Director (Training)",
            preferred_language="en",
            status="ACTIVE"
        )

        # Employee 3: Dr. Rajesh Verma (MoSPI Director & Admin)
        rajesh = User(
            email="admin@example.com",
            password_hash=get_password_hash("demo123"),
            first_name="Dr. Rajesh",
            last_name="Verma",
            role="ADMIN",
            designation_id=desig_dir.id,
            designation_name="Director",
            department_id=nad.id,
            years_experience=18,
            education="Ph.D. Economics, ISS 2008 Batch",
            current_assignment="Head of National Accounts Macro Aggregates",
            career_goal="Director General (Statistics)",
            preferred_language="en",
            status="ACTIVE"
        )
        db.add_all([rahul, priya, rajesh])
        db.flush()

        # Seed exact Rahul initial scores (Section 13)
        rahul_scores = [
            ("SAMPLING", 42.0, 2, "Basic", 0.55),
            ("PYTHON", 70.0, 4, "Advanced", 0.85),
            ("SQL", 30.0, 2, "Basic", 0.50),
            ("GIS", 20.0, 1, "Foundation", 0.40),
            ("AI_ML", 31.0, 2, "Basic", 0.45),
            ("DATA_VISUALIZATION", 74.0, 4, "Advanced", 0.80),
            ("SURVEY_DESIGN", 61.0, 3, "Intermediate", 0.70),
            ("DATA_QUALITY", 72.0, 4, "Advanced", 0.75),
            ("STAT_INFERENCE", 65.0, 3, "Intermediate", 0.70),
            ("COMMUNICATION", 68.0, 3, "Intermediate", 0.70),
            ("PROJECT_MANAGEMENT", 62.0, 3, "Intermediate", 0.65),
            ("ETHICS", 82.0, 5, "Expert", 0.90),
        ]

        for c_code, score, level, level_name, conf in rahul_scores:
            if c_code in comp_dict:
                db.add(UserCompetency(
                    user_id=rahul.id,
                    competency_id=comp_dict[c_code].id,
                    score=score,
                    level=level,
                    level_name=level_name,
                    confidence=conf,
                    evidence_count=2,
                    source="DIAGNOSTIC_ASSESSMENT",
                    last_assessed_at=datetime.now(timezone.utc)
                ))
        db.flush()

        print("[5/8] Seeding Learning Resources & iGOT/NSSTA Courses...")
        res_list = [
            (
                "IGOT", "igot-sam-01", "IGOT_COURSE",
                "Probability Sampling & Variance Estimation in Official Surveys",
                "Flagship e-learning module by MoSPI on iGOT Karmayogi. Covers stratified sampling, cluster design, and inclusion probabilities.",
                "https://igotkarmayogi.gov.in/course/sampling-variance-official-surveys",
                180, "INTERMEDIATE", "TIER_A", "iGOT Karmayogi / MoSPI",
                "Apply probability proportional to size (PPS) sampling and compute sampling errors.",
                ["SAMPLING", "SURVEY_DESIGN"]
            ),
            (
                "IGOT", "igot-sql-02", "IGOT_COURSE",
                "SQL Mastery for Administrative Registries & Survey Microdata",
                "Comprehensive SQL course focusing on analytical queries, joins on state registries, and aggregation functions.",
                "https://igotkarmayogi.gov.in/course/sql-microdata-analytics",
                120, "BASIC", "TIER_A", "iGOT Karmayogi",
                "Write performant queries, window functions, and extract weighted summaries.",
                ["SQL", "DATA_QUALITY"]
            ),
            (
                "IGOT", "igot-aiml-03", "IGOT_COURSE",
                "Applied Machine Learning for Official Statistics & Remote Sensing",
                "Introduction to supervised machine learning models for survey imputation, crop area classification, and scanner price matching.",
                "https://igotkarmayogi.gov.in/course/aiml-official-statistics",
                210, "INTERMEDIATE", "TIER_A", "iGOT Karmayogi / NSO",
                "Train Random Forest and XGBoost classifiers for missing data imputation in surveys.",
                ["AI_ML", "PYTHON"]
            ),
            (
                "NSSTA", "nssta-prog-01", "NSSTA_PROGRAM",
                "Residential Workshop on Advanced Sampling & Multiplier Calibration",
                "5-day intensive residential program at NSSTA Greater Noida campus. Practical labs using NSS microdata.",
                "https://nssta.gov.in/calendar-2026/sampling-workshop",
                1800, "ADVANCED", "TIER_A", "National Statistical Systems Training Academy (NSSTA)",
                "Master complex multi-stage sampling weights and calibration equations.",
                ["SAMPLING", "SURVEY_DESIGN"]
            ),
            (
                "NSSTA", "nssta-prog-02", "NSSTA_PROGRAM",
                "Executive Certification in Geospatial Data Analytics & QGIS",
                "3-day hybrid workshop on spatial joins, administrative boundary mapping, and census GIS planning.",
                "https://nssta.gov.in/calendar-2026/gis-certification",
                1080, "INTERMEDIATE", "TIER_A", "National Statistical Systems Training Academy (NSSTA)",
                "Create thematic choropleth maps and execute spatial overlay queries.",
                ["GIS", "DATA_VISUALIZATION"]
            ),
            (
                "INTERNAL", "mospi-nqaf-01", "DOCUMENT",
                "National Quality Assurance Framework (NQAF) Field Handbook",
                "Official guidelines for enumerators and supervisors on managing non-sampling error and validation checks.",
                "https://mospi.gov.in/sites/default/files/reports/nqaf_handbook.pdf",
                90, "FOUNDATION", "TIER_A", "MoSPI Quality Assurance Division",
                "Understand the 19 NQAF requirements and institutional quality safeguards.",
                ["DATA_QUALITY", "OFFICIAL_STATISTICS"]
            ),
            (
                "INTERNAL", "mospi-sna-02", "DOCUMENT",
                "System of National Accounts (SNA 2008) Indian Compilation Practice",
                "Detailed methodology for compiling Gross Domestic Product, Gross Value Added, and FISIM adjustments.",
                "https://mospi.gov.in/national-accounts-manual",
                240, "ADVANCED", "TIER_A", "National Accounts Division (NAD)",
                "Understand supply and use tables (SUT) and price deflator mechanics.",
                ["NATIONAL_ACCOUNTS", "STAT_INFERENCE"]
            ),
        ]

        for prov, ext_id, r_type, title, desc, url, dur, diff, tier, src_org, outcomes, c_codes in res_list:
            r = Resource(
                provider=prov,
                external_id=ext_id,
                resource_type=r_type,
                title=title,
                description=desc,
                url=url,
                duration_minutes=dur,
                difficulty=diff,
                language="en",
                authority_tier=tier,
                source_organization=src_org,
                learning_outcomes=outcomes,
                mock_data=False,
                active=True
            )
            db.add(r)
            db.flush()

            for code in c_codes:
                if code in comp_dict:
                    db.add(ResourceCompetency(
                        resource_id=r.id,
                        competency_id=comp_dict[code].id,
                        relevance_score=1.0
                    ))
        db.flush()

        print("[6/8] Seeding Diagnostic & Skill Assessments with Questions...")
        assess_diag = Assessment(
            title="Sampling & Survey Design Diagnostic Assessment",
            description="Official baseline assessment evaluating sampling designs, stratification, and survey variance calculations.",
            assessment_type="DIAGNOSTIC",
            competency_id=comp_dict["SAMPLING"].id,
            difficulty="INTERMEDIATE",
            duration_minutes=20,
            passing_score=60.0,
            active=True
        )
        db.add(assess_diag)
        db.flush()

        questions_data = [
            (
                "In stratified random sampling, what is the primary condition that defines how strata should be formed?",
                "Units within each stratum must be as homogeneous as possible, while strata should be heterogeneous between each other.",
                [
                    "Units within each stratum must be as homogeneous as possible, while strata should be heterogeneous between each other.",
                    "Units within each stratum must be completely heterogeneous, while strata means should be identical.",
                    "Strata must always contain an equal number of First Stage Units (FSUs).",
                    "The sampling fraction must be 100% across all designated sub-populations."
                ],
                "Effective stratification minimizes within-stratum variance (homogeneity) and maximizes between-strata variance, reducing total sampling error.",
                "MoSPI Sampling Techniques Manual (Section 4.1)",
                comp_dict["SAMPLING"].id
            ),
            (
                "Under Probability Proportional to Size (PPS) sampling, when is PPS with Replacement (PPSWR) typically preferred over SRS in official surveys?",
                "When First Stage Units (FSUs) such as villages or census blocks vary significantly in population size.",
                [
                    "When First Stage Units (FSUs) such as villages or census blocks vary significantly in population size.",
                    "When all population units possess exactly equal measures of size.",
                    "Only when the entire target population frame is smaller than 100 households.",
                    "When non-sampling bias is known to be strictly zero."
                ],
                "PPS allocates higher selection probabilities to larger units, ensuring efficient estimator variance when variable values correlate with unit size.",
                "MoSPI NSS Survey Methodology Handbook (Section 3.2)",
                comp_dict["SAMPLING"].id
            ),
            (
                "In survey microdata estimation, what is the mathematical role of the 'sample multiplier' (inflation factor)?",
                "It represents the inverse of the inclusion probability of the sample unit, scaling the sample observation to the population total.",
                [
                    "It represents the inverse of the inclusion probability of the sample unit, scaling the sample observation to the population total.",
                    "It indicates the percentage of non-response observed in the respective stratum.",
                    "It is a random perturbation added to preserve respondent confidentiality under disclosure control.",
                    "It measures the ratio of sampling variance to non-sampling variance."
                ],
                "Under the Horvitz-Thompson estimation framework, each sample unit weight equals 1/π_i, blowing up sample values to unbiased population totals.",
                "UNSD Guidelines on Household Sample Surveys (Chapter 7)",
                comp_dict["SAMPLING"].id
            ),
            (
                "When comparing Cluster Sampling with Simple Random Sampling (SRS) of the same sample size, Cluster Sampling generally exhibits:",
                "Higher sampling variance (lower statistical efficiency) but significantly lower operational field survey costs.",
                [
                    "Higher sampling variance (lower statistical efficiency) but significantly lower operational field survey costs.",
                    "Lower sampling variance and higher operational costs.",
                    "Identical sampling variance regardless of the intra-cluster correlation coefficient.",
                    "Complete immunity to non-sampling errors."
                ],
                "Clusters typically exhibit positive intra-cluster correlation (homogeneity within clusters), leading to a design effect (Deff) greater than 1.",
                "NSSTA Sampling Techniques Lecture Notes",
                comp_dict["SAMPLING"].id
            ),
            (
                "In SQL, which clause is specifically designed to calculate moving averages or running aggregates across partitions of survey records without collapsing rows?",
                "Window function clause (e.g. OVER (PARTITION BY ... ORDER BY ...))",
                [
                    "Window function clause (e.g. OVER (PARTITION BY ... ORDER BY ...))",
                    "GROUP BY clause with HAVING count(*) > 1",
                    "DISTINCT ON expression",
                    "CROSS JOIN LATERAL"
                ],
                "Window functions evaluate aggregate calculations across a set of table rows related to the current row without reducing the row count.",
                "PostgreSQL Statistical Analytics Documentation",
                comp_dict["SQL"].id
            ),
            (
                "Under the UN National Quality Assurance Framework (NQAF), which dimension evaluates the degree to which data can be successfully integrated with other statistical datasets?",
                "Coherence and Comparability",
                [
                    "Coherence and Comparability",
                    "Timeliness and Punctuality",
                    "Prudence and Parsimony",
                    "Commercial Viability"
                ],
                "Coherence reflects the degree to which statistics derived from different sources or methods are logically consistent and can be combined.",
                "UN NQAF Guidelines for National Statistical Systems",
                comp_dict["DATA_QUALITY"].id
            ),
        ]

        for q_text, correct_answer, options, expl, src, c_id in questions_data:
            q = Question(
                assessment_id=assess_diag.id,
                competency_id=c_id,
                question_type="SINGLE_CHOICE",
                difficulty="INTERMEDIATE",
                question_text=q_text,
                explanation=expl,
                source_reference=src,
                source_tier="TIER_A",
                generated_by="SYSTEM",
                validation_status="PUBLISHED",
                ai_validation_score=1.0
            )
            db.add(q)
            db.flush()

            for o_idx, o_text in enumerate(options):
                db.add(QuestionOption(
                    question_id=q.id,
                    option_text=o_text,
                    is_correct=(o_text == correct_answer),
                    order_index=o_idx
                ))
        db.flush()

        print("[7/8] Seeding Official Statistical Documents for RAG & Ingestion...")
        sample_doc_content = (
            "GOVERNMENT OF INDIA - MINISTRY OF STATISTICS AND PROGRAMME IMPLEMENTATION\n"
            "NATIONAL STATISTICAL SYSTEMS TRAINING ACADEMY (NSSTA)\n\n"
            "TECHNICAL HANDBOOK ON SAMPLING TECHNIQUES & FIELD METHODOLOGY (REVISED EDITION)\n\n"
            "1. PROBABILITY SAMPLING PRINCIPLES\n"
            "In official socio-economic surveys conducted by the National Statistical Office (NSO), "
            "sampling designs must adhere strictly to probability sampling. Non-probability methods such as quota "
            "or convenience sampling are prohibited for official parameter estimation.\n\n"
            "2. STRATIFICATION MECHANISMS IN HOUSEHOLD SURVEYS\n"
            "Stratification serves two primary objectives: first, to increase the precision of all-India and state-level estimates "
            "by dividing heterogeneous populations into homogeneous sub-populations; second, to ensure adequate sample sizes "
            "for key administrative domains (e.g., rural vs. urban sectors, or district-level indicators).\n\n"
            "3. FIRST STAGE UNITS (FSUs) AND SECOND STAGE STRATIFICATION (SSS)\n"
            "In the Periodic Labour Force Survey (PLFS), the First Stage Units (FSUs) are the 2011 Census enumeration blocks "
            "in urban sectors and census villages in rural areas. Within each selected FSU, households are listed and partitioned "
            "into Second Stage Strata (SSS) based on household education level and consumption expenditure to ensure representation "
            "of varying socio-economic strata.\n\n"
            "4. HORVITZ-THOMPSON ESTIMATION AND MULTIPLIERS\n"
            "Let y_i be the variable of interest (e.g., monthly per capita expenditure) for unit i. Under unequal probability sampling "
            "without replacement, the unbiased Horvitz-Thompson estimator of the population total Y is:\n"
            "Y_hat = sum_{i in sample} (y_i / pi_i)\n"
            "where pi_i is the first-order inclusion probability. The sample multiplier is defined as w_i = 1 / pi_i.\n\n"
            "5. NATIONAL QUALITY ASSURANCE FRAMEWORK (NQAF)\n"
            "Statistical quality is multi-dimensional. Quality assurance encompasses: (1) Relevance, (2) Accuracy and Reliability, "
            "(3) Timeliness and Punctuality, (4) Accessibility and Clarity, (5) Coherence and Comparability, and (6) Metadata completeness. "
            "Supervisory field inspections and real-time validation rules during Computer Assisted Personal Interviewing (CAPI) "
            "are deployed to minimize non-sampling measurement errors."
        )

        doc = Document(
            title="MoSPI Sampling Techniques & Field Methodology Handbook",
            filename="mospi_sampling_methodology_handbook.txt",
            file_path="uploads/seed/mospi_sampling_methodology_handbook.txt",
            file_type="TXT",
            mime_type="text/plain",
            file_size_bytes=len(sample_doc_content),
            source_organization="Ministry of Statistics & Programme Implementation (MoSPI)",
            authority_tier="TIER_A",
            status="READY",
            total_pages=5,
            total_chunks=3,
            scan_status="CLEAN",
            uploaded_by=priya.id
        )
        db.add(doc)
        db.flush()

        # Add chunks with synthetic normalized embeddings
        embedder = get_embedding_provider()
        chunks = [
            ("Chapter 1: Probability Sampling Principles and Stratification in NSO Surveys.", 1, "SAMPLING"),
            ("Chapter 3: First Stage Units (FSUs) and Second Stage Stratification in the Periodic Labour Force Survey.", 2, "SAMPLING"),
            ("Chapter 5: Horvitz-Thompson Estimation, Multipliers, and NQAF Quality Assurance Dimensions.", 3, "DATA_QUALITY"),
        ]

        import asyncio
        for idx, (chunk_text, page, comp_code) in enumerate(chunks):
            # Run mock embedding synchronously for seed script
            h_vec = [0.0] * 1536
            for w in chunk_text.lower().split():
                h_vec[hash(w) % 1536] += 1.0
            import math
            n = math.sqrt(sum(x*x for x in h_vec)) or 1.0
            norm_vec = [round(x/n, 6) for x in h_vec]

            db.add(DocumentChunk(
                document_id=doc.id,
                chunk_index=idx,
                content=chunk_text,
                page_number=page,
                section_header=f"Section {idx+1}",
                competency_code=comp_code,
                token_count=len(chunk_text.split()),
                embedding_json=json.dumps(norm_vec)
            ))
        db.flush()

        print("[8/8] Seeding Future Skills Forecasting...")
        future_skills_data = [
            ("Generative AI for Statistical Dissemination", "AI/ML", 24.0, 92.0, 68.0, "CRITICAL", "iGOT Course: GenAI & RAG for Public Policy", "UN Statistical Commission 2026"),
            ("Privacy-Preserving Technologies & Differential Privacy", "Digital Governance", 18.0, 88.0, 70.0, "CRITICAL", "NSSTA Workshop: Microdata Anonymization & Noise Addition", "MoSPI Modernization Vision"),
            ("High-Frequency Satellite & Scanner Data Analytics", "Technical", 32.0, 85.0, 53.0, "HIGH", "NSSTA Workshop: Big Data for CPI & Remote Sensing", "OECD Working Group on Big Data"),
            ("Automated Imputation & Data Quality AI", "Statistical", 40.0, 80.0, 40.0, "HIGH", "MoSPI Quality Assurance Division Hands-on Lab", "UN NQAF Guidelines"),
        ]

        for name, dom, curr, exp, gap, prio, train, src in future_skills_data:
            db.add(FutureSkill(
                name=name,
                domain=dom,
                current_readiness=curr,
                expected_importance=exp,
                gap=gap,
                priority=prio,
                recommended_training=train,
                trend_source=src,
                rationale="Critical competency required for transitioning to real-time administrative and modern data sources."
            ))

        db.commit()

        # Evaluate and populate Rahul's initial Skill Gaps and Learning Path!
        print("[SUCCESS] Seeding complete! Evaluating initial skill gaps for Rahul Sharma...")
        evaluate_user_skill_gaps(db, rahul.id)
        print("[READY] India Official Statistical System platform database initialized successfully!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Database seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
