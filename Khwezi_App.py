# KHWEZI MINING MONITERING - MINN2020A

import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Khwezi Mining", page_icon="⛏️", layout="wide")


FOLDER = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(FOLDER, "Khwezi_Mining_Data.xlsx")
WORKER_FILE = os.path.join(FOLDER, "worker_records.csv")

# PART A
permissions = {
    "Administrator": ["Dashboard", "Worker Safety", "Safety Incidents", "Equipment", "Maintenance", "Risk Assessment", "Alerts", "Reports", "Manage Users"],
    "Safety Officer": ["Dashboard", "Worker Safety", "Safety Incidents", "Risk Assessment", "Reports"],
    "Mining Engineer": ["Dashboard", "Worker Safety", "Safety Incidents", "Equipment", "Maintenance", "Risk Assessment", "Reports"],
    "Maintenance Engineer": ["Dashboard", "Equipment", "Maintenance", "Reports"],
    "Manager": ["Dashboard", "Worker Safety", "Safety Incidents", "Equipment", "Maintenance", "Risk Assessment", "Reports"],
}


def load_data():
    if not os.path.exists(EXCEL_FILE):
        st.error("Place Khwezi_Mining_Data.xlsx in the same folder as this app.")
        st.stop()
    data = pd.read_excel(EXCEL_FILE, sheet_name=None)
    if os.path.exists(WORKER_FILE):
        data["Worker Safety"] = pd.read_csv(WORKER_FILE).fillna("")
    return data


def show_table(table, filename):
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", table.to_csv(index=False), file_name=filename, mime="text/csv")

# PART B: Find workers who need attention.
def worker_warnings(workers):
    warnings = []
    for _, worker in workers.iterrows():
        problems = []
        if str(worker["PPE Compliance"]).lower() == "no":
            problems.append("PPE not compliant")
        if str(worker["Safety Training Status"]).lower() == "incomplete":
            problems.append("Training incomplete")
        if str(worker["Fatigue Level"]).lower() == "high":
            problems.append("High fatigue")
        if str(worker["Risk level"]).lower() == "high":
            problems.append("High safety risk")
        if str(worker["Risk level"]).lower() == "critical":
            problems.append("CRITICAL safety risk")
        for problem in problems:
            warnings.append({"Worker ID": worker["Worker ID"], "Department": worker["Department"], "Warning": problem})
    return pd.DataFrame(warnings, columns=["Worker ID", "Department", "Warning"])

# PART A: Main Mining Monitoring Dashboard
def dashboard(data):

    st.title("⛏️ Mining Monitoring")
    st.caption("Khwezi Mining | Health, safety and equipment overview")

    
    workers = data["Worker Safety"]
    incidents = data["Safety Incidents"]
    observations = data["Safety Observations"]
    equipment = data["Equipment"]
    alerts = data["Alerts"]

    # this is our calculation for safety indicators
    total_workers = workers["Worker ID"].nunique()
    total_incidents = incidents["Incident ID"].nunique()

    near_misses = (
        incidents["Incident Type"].astype(str).str.lower() == "near miss"
    ).sum()

    high_risk = (
        observations["Risk Level"].astype(str).str.lower().isin(
            ["high", "critical"]
        )
    ).sum()

    ppe_compliance = (
        workers["PPE Compliance"].astype(str).str.lower() == "yes"
    ).mean() * 100 if not workers.empty else 0

    # this is our calculation for equipment indicators
    total_equipment = equipment["Equipment ID"].nunique()

    under_maintenance = (
        equipment["Maintenance Status"].astype(str).str.lower()
        == "under maintenance"
    ).sum()

    available_equipment = total_equipment - under_maintenance

    equipment_alerts = alerts[
        alerts["Source"].astype(str).str.lower() == "equipment"
    ]

    average_availability = pd.to_numeric(
        equipment["Availability (%)"], errors="coerce"
    ).mean()

    critical_alerts = equipment_alerts[
        (equipment_alerts["Severity"].astype(str).str.lower() == "critical") &
        (equipment_alerts["Status"].astype(str).str.lower() == "open")
    ]

    
    st.subheader("Mining Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Workers", total_workers)
    col2.metric("Safety incidents", total_incidents)
    col3.metric("Equipment", total_equipment)
    col4.metric("Open critical alerts", len(critical_alerts))

    st.divider()

    # Overview of Worker Safety 
    st.subheader("Worker Safety Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total workers", total_workers)
    col2.metric("Safety incidents", total_incidents)
    col3.metric("Near misses", near_misses)
    col4.metric("High-risk observations", high_risk)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("PPE compliance", f"{ppe_compliance:.1f}%")

    st.divider()

    # Overview of Equipment 
    st.subheader("Equipment Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total equipment", total_equipment)
    col2.metric("Available equipment", available_equipment)
    col3.metric("Under maintenance", under_maintenance)
    col4.metric("Equipment alerts", len(equipment_alerts))

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Average availability",
        f"{average_availability:.1f}%"
    )

    col2.metric(
        "Open critical equipment alerts",
        len(critical_alerts)
    )

    st.divider()

    # Charts of Safety 
    st.subheader("Safety Monitoring")

    left, right = st.columns(2)

    with left:
        st.write("Incidents by severity")
        st.bar_chart(incidents["Severity"].value_counts())

    with right:
        st.write("Worker risk levels")
        st.bar_chart(workers["Risk level"].value_counts())

    # Chart of Equipment 
    st.subheader("Equipment Monitoring")
    st.bar_chart(equipment["Maintenance Status"].value_counts())

    # Table of Critical alerts 
    st.subheader("Open Critical Equipment Alerts")

    if critical_alerts.empty:
        st.success("No open critical equipment alerts found.")
    else:
        st.dataframe(
            critical_alerts,
            use_container_width=True,
            hide_index=True
        )

# PART B: part where we view, search and add workers.
def worker_safety(data):
    st.header("Part B | Worker Health and Safety")
    workers = data["Worker Safety"]
    tab1, tab2, tab3 = st.tabs(["Worker records", "Add worker", "Safety warnings"])
    with tab1:
        search = st.text_input("Search Worker ID or Department")
        if search:
            matches = workers.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False))
            shown = workers[matches.any(axis=1)]
        else:
            shown = workers
        show_table(shown, "workers.csv")
    with tab2:
        with st.form("new_worker"):
            worker_id = st.text_input("Worker ID").strip().upper()
            department = st.text_input("Department").strip()
            ppe = st.selectbox("PPE Compliance", ["Yes", "No"])
            training = st.selectbox("Safety Training", ["Completed", "Incomplete"])
            fatigue = st.selectbox("Fatigue Level", ["Low", "Medium", "High"])
            risk = st.selectbox("Risk Level", ["Low", "Medium", "High", "Critical"])
            save = st.form_submit_button("Save worker")
        if save:
            existing = workers["Worker ID"].astype(str).str.upper().tolist()
            if not worker_id or not department:
                st.error("Worker ID and Department cannot be empty.")
            elif worker_id in existing:
                st.error("Worker ID already exists.")
            else:
                new_worker = pd.DataFrame([{"Worker ID": worker_id, "Department": department,
                    "PPE Compliance": ppe, "Safety Training Status": training,
                    "Fatigue Level": fatigue, "Risk level": risk}])
                updated = pd.concat([workers, new_worker], ignore_index=True)
                updated.to_csv(WORKER_FILE, index=False)
                st.success("Worker saved! The original Excel workbook is unchanged.")
                st.rerun()
    with tab3:
        warnings = worker_warnings(workers)
        st.metric("Warning items", len(warnings))
        if warnings.empty:
            st.success("No safety warnings detected.")
        else:
            show_table(warnings, "worker_warnings.csv")

# PART C: this is where we view recorded safety incidents.
def safety_incidents(data):
    st.header("Safety Incidents")
    incidents = data["Safety Incidents"]
    severity = st.selectbox("Filter severity", ["All"] + sorted(incidents["Severity"].dropna().unique().tolist()))
    if severity != "All":
        incidents = incidents[incidents["Severity"] == severity]
    show_table(incidents, "safety_incidents.csv")

# PART E: our temperature and vibration use the thresholds from our code.
def condition_check(equipment_id, temperature, vibration):
    st.write("Equipment ID:", equipment_id)
    if temperature < 80:
        st.success("Temperature: NORMAL")
    elif temperature <= 100:
        st.warning("Temperature: WARNING")
    else:
        st.error("Temperature: CRITICAL - inspection required")
    if vibration < 5:
        st.success("Vibration: NORMAL")
    elif vibration <= 8:
        st.warning("Vibration: WARNING")
    else:
        st.error("Vibration: CRITICAL - inspection required")

# PART E: this is where we view our equipment records and check readings.
def equipment_monitoring(data):
    st.header("Part E | Equipment Condition Monitoring")
    equipment = data["Equipment"]
    tab1, tab2 = st.tabs(["Equipment records", "Check condition"])
    with tab1:
        show_table(equipment, "equipment.csv")
    with tab2:
        equipment_id = st.selectbox("Equipment ID", equipment["Equipment ID"].astype(str).tolist())
        record = equipment[equipment["Equipment ID"].astype(str) == equipment_id].iloc[0]
        temperature = st.number_input("Temperature (°C)", min_value=0.0, value=float(record["Temperature (°C)"]))
        vibration = st.number_input("Vibration (mm/s)", min_value=0.0, value=float(record["Vibration (mm/s)"]))
        if st.button("Check equipment condition"):
            condition_check(equipment_id, temperature, vibration)

# PART F: this is for maintenance availability and warning checks.
def maintenance_monitoring(data):
    st.header("Part F | Maintenance Monitoring")
    tab1, tab2 = st.tabs(["Maintenance records", "Calculate maintenance status"])
    with tab1:
        show_table(data["Maintenance"], "maintenance.csv")
    with tab2:
        equipment_id = st.text_input("Equipment ID", "EQ-001")
        operating = st.number_input("Operating time (hours)", min_value=0.0, value=100.0)
        downtime = st.number_input("Downtime (hours)", min_value=0.0, value=10.0)
        since_service = st.number_input("Hours since last service", min_value=0.0, value=100.0)
        interval = st.number_input("Maintenance interval (hours)", min_value=0.01, value=200.0)
        number_alerts = st.number_input("Number of equipment alerts", min_value=0, step=1)
        under_maintenance = st.selectbox("Under maintenance?", ["No", "Yes"])
        if st.button("Calculate maintenance"):
            total_time = operating + downtime
            availability = (operating / total_time) * 100 if total_time > 0 else 0
            st.write("Equipment ID:", equipment_id)
            st.metric("Equipment availability", f"{availability:.2f}%")
            if since_service >= interval:
                st.warning("Maintenance is due.")
                if since_service > interval and under_maintenance == "No":
                    st.error("OVERDUE: Maintenance required.")
            else:
                st.success("Maintenance is not yet due.")
            if under_maintenance == "Yes":
                st.info("Equipment is under maintenance.")
            if total_time > 0 and downtime / total_time >= 0.20:
                st.warning("Excessive downtime (20% or more).")
            if number_alerts >= 3:
                st.warning("Repeated equipment alerts.")
            if availability < 85:
                st.warning("Low equipment availability.")

# PART G: Risk score = Likelihood x Consequence.
def risk_assessment(data):
    st.header("Part G | Risk Assessment")
    tab1, tab2 = st.tabs(["Recorded risks", "Calculate risk score"])
    with tab1:
        show_table(data["Risk Assessments"], "risk_assessments.csv")
    with tab2:
        likelihood = st.number_input("Likelihood (1-5)", min_value=1, max_value=5, value=1)
        consequence = st.number_input("Consequence (1-5)", min_value=1, max_value=5, value=1)
        if st.button("Calculate risk score"):
            score = likelihood * consequence
            if score <= 4:
                classification = "Low"
            elif score <= 9:
                classification = "Medium"
            elif score <= 16:
                classification = "High"
            else:
                classification = "Critical"
            st.metric("Risk score", score)
            st.write("Classification:", classification)
            if classification in ["High", "Critical"]:
                st.error("Immediate attention required.")
            else:
                st.success("Risk classification recorded.")

# PART H: this is where we check our equipment alerts and other safety records.
def alerts_monitoring(data):
    st.header("Part H | Alerts and Notifications")
    equipment = data["Equipment"]
    equipment_id = st.selectbox("Choose equipment", equipment["Equipment ID"].astype(str).tolist())
    row = equipment[equipment["Equipment ID"].astype(str) == equipment_id].iloc[0]
    if st.button("Run monitoring check"):
        st.write("Equipment type:", row["Equipment Type"])
        temperature = float(row["Temperature (°C)"])
        vibration = float(row["Vibration (mm/s)"])
        if temperature > 100:
            st.error("CRITICAL: High temperature!")
        elif temperature >= 80:
            st.warning("WARNING: High temperature!")
        if vibration > 8:
            st.error("CRITICAL: High vibration!")
        elif vibration >= 5:
            st.warning("WARNING: High vibration!")
        if float(row["Downtime (h)"]) > 24:
            st.warning("Excessive equipment downtime!")
        if str(row["Maintenance Status"]).lower() in ["due", "overdue"]:
            st.warning("Maintenance is due or overdue!")
        maintenance = data["Maintenance"]
        overdue = maintenance[(maintenance["Equipment ID"].astype(str) == equipment_id) &
                              (maintenance["Status"].astype(str).str.lower() == "overdue")]
        for _, task in overdue.iterrows():
            st.error("OVERDUE MAINTENANCE: " + str(task["Maintenance Type"]))
        alerts = data["Alerts"]
        linked = alerts[(alerts["Record ID"].astype(str) == equipment_id) &
                        (alerts["Source"].astype(str).str.lower() == "equipment")]
        st.write("Recorded alerts for this equipment:")
        st.dataframe(linked, use_container_width=True, hide_index=True)
        incidents = data["Safety Incidents"]
        observations = data["Safety Observations"]
        risks = data["Risk Assessments"]
        st.write("Critical safety incidents:", (incidents["Severity"].astype(str).str.lower() == "critical").sum())
        st.write("High-risk observations:", (observations["Risk Level"].astype(str).str.lower() == "high").sum())
        st.write("High/critical risk assessments:", risks["Risk Classification"].astype(str).str.lower().isin(["high", "critical"]).sum())
        st.success("Monitoring check complete.")
    st.subheader("All recorded alerts")
    show_table(data["Alerts"], "alerts.csv")


def reports(data):
    st.header("Reports")
    sheet = st.selectbox("Choose report", ["Worker Safety", "Safety Incidents", "Equipment", "Maintenance", "Risk Assessments", "Alerts", "Safety Observations"])
    show_table(data[sheet], sheet.lower().replace(" ", "_") + ".csv")


def manage_users(data):
    st.header("Manage Users")
    users = data["Users"].drop(columns=["Password"], errors="ignore")
    st.info("User accounts are read from the workbook. Passwords are not displayed.")
    st.dataframe(users, use_container_width=True, hide_index=True)

# this is for styling , where we see our appearance only, not the calculations.
st.markdown("""
<style>

/* Main background - Light grey-blue */
.stApp {
    background: #F0F3F9;
    color: #20344B;
}

/* Sidebar background - unchanged */
[data-testid="stSidebar"] {
    background: #182B42;
}

/* Sidebar words - white */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}
/* Main headings */
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3 {
    color: #20344B !important;
}

/* Main text */
[data-testid="stMain"] p,
[data-testid="stMain"] label {
    color: #20344B !important;
}

/* Metric cards - White with gold borders */
[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #E9B44C;
    border-left: 5px solid #E9B44C;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
}

/* Metric text - Dark navy */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #20344B !important;
}

</style>
""", unsafe_allow_html=True)
# Start the application.
data = load_data()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("⛏️ Khwezi Mining Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log in"):
        users = data["Users"]
        match = users[(users["Username"].astype(str) == username) &
                      (users["Password"].astype(str) == password)]
        if match.empty:
            st.error("Incorrect username or password.")
        else:
            role = str(match.iloc[0]["Role"])
            if role not in permissions:
                st.error("Unknown role.")
            else:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.rerun()
else:
    st.sidebar.title("⛏️ KHWEZI MINING")
    st.sidebar.write("User:", st.session_state.username)
    st.sidebar.write("Role:", st.session_state.role)
    page = st.sidebar.radio("Navigation", permissions[st.session_state.role])
    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()
    if page == "Dashboard":
        dashboard(data)
    elif page == "Worker Safety":
        worker_safety(data)
    elif page == "Safety Incidents":
        safety_incidents(data)
    elif page == "Equipment":
        equipment_monitoring(data)
    elif page == "Maintenance":
        maintenance_monitoring(data)
    elif page == "Risk Assessment":
        risk_assessment(data)
    elif page == "Alerts":
        alerts_monitoring(data)
    elif page == "Reports":
        reports(data)
    elif page == "Manage Users":
        manage_users(data)
