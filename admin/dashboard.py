import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Omendra AI CRM Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# LOGIN STATE
# =====================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "role" not in st.session_state:
    st.session_state.role = None

BASE_URL = "http://127.0.0.1:8000"

# =====================================================
# LOGIN SCREEN
# =====================================================

if st.session_state.token is None:

    st.title("🔐 Omendra AI Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        response = requests.post(
            f"{BASE_URL}/login",
            data={
                "username": username,
                "password": password
            }
        )

        if response.status_code == 200:

            result = response.json()

            st.session_state.token = result[
                "access_token"
            ]

            st.session_state.role = result[
                "role"
            ]

            st.rerun()

        else:

            st.error(
                "Invalid Username or Password"
            )

    st.stop()


# =====================================================
# AUTHORIZATION HEADER
# =====================================================

headers = {
    "Authorization":
    f"Bearer {st.session_state.token}"
}

# =====================================================
# SENIOR FRONTEND DESIGN SYSTEM & VISIBILITY OVERRIDES
# =====================================================
st.markdown("""
    <style>
    /* Global Background and Dark Theme Canvas */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
        color: #f8fafc;
    }
    
    /* Perfect Sidebar Visibility & Contrast Rules */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Targets all text items, labels, and titles in the sidebar safely */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }
    
    /* Forces the Active/Selected Radio Option text to be bright white */
    [data-testid="stSidebar"] [data-checked="true"] span {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Elegant Custom Linear Gradient Title Style */
    .dashboard-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Senior Dev Glassmorphic Metric & Detail Panels */
    .kpi-card, .profile-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.25);
        margin-bottom: 1rem;
    }
    .kpi-card {
        transition: transform 0.2s ease-in-out, border 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        border: 1px solid rgba(56, 189, 248, 0.4);
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    .kpi-val {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-top: 0.25rem;
    }
    
    /* Metadata grid elements for CRM Profile rendering */
    .meta-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .meta-label { color: #94a3b8; font-weight: 500; }
    .meta-value { color: #ffffff; font-weight: 600; }
    
    /* Interactive input box adjustments */
    div[data-baseweb="input"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border-radius: 8px !important;
    }
    
    /* Tab Header Text Styling fixes */
    button[data-baseweb="tab"] div p {
        color: #94a3b8 !important;
    }
    button[aria-selected="true"] div p {
        color: #38bdf8 !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# DATA EXTRACTION LAYER (With Intelligent Error Caching)
# =====================================================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_all_dashboard_data(token):

    headers = {
        "Authorization":
        f"Bearer {token}"
    }

    try:

        customers = requests.get(
            f"{BASE_URL}/customers",
            headers=headers,
            timeout=5
        ).json()

        leads = requests.get(
            f"{BASE_URL}/leads",
            headers=headers,
            timeout=5
        ).json()

        chats = requests.get(
            f"{BASE_URL}/all-chats",
            headers=headers,
            timeout=5
        ).json()

        analytics = requests.get(
            f"{BASE_URL}/analytics",
            headers=headers,
            timeout=5
        ).json()

        return (
            customers,
            leads,
            chats,
            analytics,
            None
        )

    except Exception as e:

        return (
            [],
            [],
            [],
            {},
            str(e)
        )

# Global execution of asynchronous data layer
with st.spinner("Synchronizing UI state with backend core services..."):
    customers, leads, chats, analytics, connection_error = fetch_all_dashboard_data(st.session_state.token)

# Handle Graceful Server Fault Fallback State
if connection_error:
    st.error(f"🚨 Network Architecture Disconnect: {connection_error}")
    st.info("Senior Dev Checklist: Please verify that your local FastAPI container or python server is exposed on port 8000.")
    st.stop()

# =====================================================
# SIDEBAR CONTROL DECK
# =====================================================
st.sidebar.markdown('<p style="font-size: 1.8rem; font-weight: 800; color:#fff; margin-bottom:0;">🚀 Omendra AI</p>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="font-size: 0.8rem; color:#64748b; margin-top:0;">Enterprise CRM Suite v3.0</p>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# Styled Sidebar Page Routing Matrix
role = st.session_state.role

if role == "admin":

    menu = st.sidebar.radio(
        "NAVIGATION MENU",
        [
            "📊 Dashboard Overview",
            "👤 Customer Management CRM",
            "🎯 Leads Management Hub",
            "💬 Conversation Hub",
            "📢 Broadcast Center",
            "👥 User Management"
        ]
    )

elif role == "manager":

    menu = st.sidebar.radio(
        "NAVIGATION MENU",
        [
            "📊 Dashboard Overview",
            "👤 Customer Management CRM",
            "🎯 Leads Management Hub",
            "💬 Conversation Hub"
        ]
    )

else:

    menu = st.sidebar.radio(
        "NAVIGATION MENU",
        [
            "📊 Dashboard Overview",
            "👤 Customer Management CRM"
        ]
    )

st.sidebar.markdown("---")

st.sidebar.success(
    f"Role: {st.session_state.role}"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.token = None
    st.session_state.role = None

    st.rerun()


# Force state invalidation trigger
if st.sidebar.button("🔄 Force Refresh Cache", use_container_width=True, type="secondary"):
    st.cache_data.clear()
    st.rerun()

# =====================================================
# SCREEN APPLICATION CONTROLLERS
# =====================================================

# --- SECTION 1: DASHBOARD OVERVIEW & ANALYTICS VISUALIZATIONS ---
if menu == "📊 Dashboard Overview":
    st.markdown('<h1 class="dashboard-title">Omendra AI Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Custom Card Render Components [cite: 52]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">👥 Total Customers</div><div class="kpi-val">{len(customers)}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">🎯 Active System Leads</div><div class="kpi-val">{len(leads)}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">💬 System Chats Logged</div><div class="kpi-val">{len(chats)}</div></div>', unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

    st.subheader("📊 System Analytics Insights")
    if analytics:
        col_left, col_right = st.columns([1, 1.2])
        
        with col_left:
            # Table layout adjustments for key metrics
            analytics_df = pd.DataFrame(list(analytics.items()), columns=["Metric Indicator", "Recorded Value"])
            st.dataframe(
                analytics_df.style.background_gradient(cmap="Blues", subset=["Recorded Value"]), 
                use_container_width=True,
                hide_index=True
            )
            
        with col_right:
            # Dynamic filtering of the analytics dictionary to pinpoint the services for the requested Pie Chart view
            service_keys = ['ai_solutions', 'data_analytics', 'software_development', 'whatsapp_automation']
            service_data = {k.replace('_', ' ').title(): pd.to_numeric(analytics[k]) for k in service_keys if k in analytics}
            
            if service_data and sum(service_data.values()) > 0:
                pie_df = pd.DataFrame(list(service_data.items()), columns=["Service Track", "Count"])
                
                # Plotly Premium Custom Render Architecture
                fig = px.pie(
                    pie_df, 
                    values='Count', 
                    names='Service Track', 
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Plotly3
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    margin=dict(t=10, b=10, l=10, r=10)
                )
                st.markdown("<p style='font-size:1.1rem; font-weight:600; text-align:center;'>Service Vertical Distribution Breakdowns</p>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ Service track counts are currently evaluated at zero. Visual metrics will populate as choices expand.")
    else:
        st.warning("No data returned from analytics stream pipelines.")


# --- SECTION 2: CUSTOMER MANAGEMENT CRM (NEW UPGRADED INTERACTIVE MASTER-DETAIL PAGE) ---
elif menu == "👤 Customer Management CRM":
    st.markdown('<h1 class="dashboard-title">Customer Relationship Management</h1>', unsafe_allow_html=True)

    if customers:
        customer_df = pd.DataFrame(customers)
        
        # Upper horizontal quick search toolbar
        text_search = st.text_input("🔍 Live-Filter Directory Database", placeholder="Search by name, status, phone number string patterns...")
        if text_search:
            mask = customer_df.astype(str).apply(lambda x: x.str.contains(text_search, case=False)).any(axis=1)
            customer_df = customer_df[mask]

        # Layout Allocation: Left-hand navigation list grid, right-hand rich details interface card panel
        col_list, col_profile = st.columns([1.1, 1.9])
        
        with col_list:
            st.subheader("📋 Client Roster")
            
            # Format rows nicely for user selection dropdown
            if not customer_df.empty:
                customer_df['dropdown_label'] = customer_df['name'] + " (" + customer_df['phone'].astype(str) + ")"
                selected_label = st.selectbox(
                    "Select Account Profile to Inspect:",
                    options=customer_df['dropdown_label'].tolist()
                )
                # Pull precise data map belonging to selected target entity row
                target_row = customer_df[customer_df['dropdown_label'] == selected_label].iloc[0]
                selected_phone = str(target_row.get("phone", ""))
            else:
                st.warning("No matches found for your filter input.")
                selected_phone = None

        with col_profile:
            st.subheader("👤 Live CRM Deep Dive")
            if selected_phone:
                with st.spinner("Querying transactional endpoints for customer context logs..."):
                    try:
                        # Fetch the Lead summary to extract details
                        profile_summary = requests.get(
                            f"{BASE_URL}/lead-summary/{selected_phone}",
                            headers=headers,
                            timeout=5
                        ).json()
                        # Fetch history array logs
                        profile_history = requests.get(
                            f"{BASE_URL}/chat-history/{selected_phone}",
                            headers=headers,
                            timeout=5
                        ).json()
                        
                        # Render Interactive Profile Sheet Card Layouts
                        st.markdown(f"""
                            <div class="profile-card">
                                <h3 style="margin-top:0; color:#38bdf8; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0.5rem;">👤 Customer Profile Sheet</h3>
                                <div class="meta-row"><span class="meta-label">Full Name</span><span class="meta-value">{profile_summary.get('name', 'Omendra')}</span></div>
                                <div class="meta-row"><span class="meta-label">Direct Phone Line</span><span class="meta-value">+{profile_summary.get('phone', selected_phone)}</span></div>
                                <div class="meta-row"><span class="meta-label">Gender Demographics</span><span class="meta-value">{profile_summary.get('gender', 'NA')}</span></div>
                                <div class="meta-row"><span class="meta-label">Age</span><span class="meta-value">{profile_summary.get('age', 'NA')}</span></div>
                                <div class="meta-row"><span class="meta-label">Geographic Location</span><span class="meta-value">{profile_summary.get('city', 'NA')}</span></div>
                                <div class="meta-row"><span class="meta-label">Selected Track Service</span><span class="meta-value" style="color:#a855f7;">{profile_summary.get('service', 'WhatsApp Automation')}</span></div>
                                <div class="meta-row"><span class="meta-label">Allocated Capital Budget</span><span class="meta-value" style="color:#22c55e;">{profile_summary.get('budget', 'Below 10000')}</span></div>
                                <div class="meta-row"><span class="meta-label">Lead Status Routing</span><span class="meta-value" style="background:#1e3a8a; padding:2px 8px; border-radius:4px; font-size:0.85rem;">{profile_summary.get('lead_status', 'Completed')}</span></div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Requirement block callout element
                        st.markdown("#### 📑 Explicit Structural Requirements")
                        st.info(profile_summary.get('requirement', 'I want to connect with your team'))
                        
                        # Intelligent Core Summary block formatting callout
                        st.markdown("#### ✨ AI-Generated Executive Summary Brief")
                        st.help(profile_summary.get('summary', 'AI generated context compilation summary description goes here.'))
                        
                        # Nested Recent Interaction History Frame
                        st.markdown("#### 💬 Recent Conversation Sequences")
                        if isinstance(profile_history, list) and len(profile_history) > 0:
                            for chat_packet in profile_history[:5]:  # Limit display scope to top 5 recent turns
                                user_msg = chat_packet.get("user_message", chat_packet.get("content", ""))
                                ai_reply = chat_packet.get("ai_reply", chat_packet.get("response", ""))
                                
                                if user_msg:
                                    with st.chat_message("user"):
                                        st.markdown(user_msg)
                                if ai_reply:
                                    with st.chat_message("assistant"):
                                        st.markdown(ai_reply)
                        else:
                            st.info("No recorded dialog interactions found for this profile selection.")
                    except Exception as e:
                        st.error(f"CRM Processing Disruption: Could not resolve client object sub-properties. {e}")
            else:
                st.info("Select a customer record tracking identity row on the left panel to browse detailed fields.")
    else:
        st.warning("No client entries populated in target collection database.")


# --- SECTION 3: LEAD CONVERSION MANAGEMENT HIERARCHY ---
elif menu == "🎯 Leads Management Hub":
    st.markdown('<h1 class="dashboard-title">Leads Management Hub</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Master Leads Ledger", "🔍 Precision Lead Query", "📝 Generative Lead Summary"])
    
    with tab1:
        if leads:
            lead_df = pd.DataFrame(leads)
            st.dataframe(lead_df, use_container_width=True, hide_index=True)

            csv = lead_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Leads CSV",
                data=csv,
                file_name="leads_data.csv",
                mime="text/csv"
            )
        else:
            st.warning("No active sales leads found.")
            
    with tab2:
        st.markdown("### 🔍 Precision Query Engine")
        
        col_input, col_type = st.columns([3, 1])
        with col_input:
            search_name = st.text_input("Search Argument", placeholder="Input explicit pattern parameter here...")
        with col_type:
            search_type = st.selectbox("Indexed Data Pillar", ["Phone", "Name"])

        if st.button("Query Pipeline", type="primary", use_container_width=True):
            if not search_name.strip():
                st.warning("Validation Prompt: Query parameters cannot evaluate empty character indexes.")
            else:
                try:
                    params = {"phone": search_name} if search_type == "Phone" else {"name": search_name}
                    result = requests.get(f"{BASE_URL}/search-leads", headers=headers, params=params).json()

                    if result:
                        st.success("Target Record Discovered inside Cluster State!")
                        st.dataframe(pd.DataFrame(result), use_container_width=True, hide_index=True)
                    else:
                        st.warning("No data rows matched your precise signature requirements.")
                except Exception as e:
                    st.error(f"Execution Error processing criteria: {e}")
                    
    with tab3:
        st.markdown("### 📝 GenAI Core Executive Brief Generator")
        summary_phone = st.text_input("Input Target Account Phone Signature", key="summary_phone_key")
        
        if st.button("Synthesize Executive Brief", type="primary"):
            if not summary_phone.strip():
                st.warning("Target parameter missing valid phone string key index.")
            else:
                with st.spinner("Querying LLM Engine nodes and synthesizing conversation context..."):
                    try:
                        summary = requests.get(
                            f"{BASE_URL}/lead-summary/{summary_phone}",
                            headers=headers,
                            timeout=5
                        ).json()
                        st.success("Brief Generation Complete!")
                        
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.subheader("👤 Lead Identity")
                            st.info(summary.get("name", "N/A"))
                        with col_info2:
                            st.subheader("📞 Direct Contact String")
                            st.info(summary.get("phone", "N/A"))
                            
                        st.subheader("✨ AI Generated Conversation Summary")
                        st.help(summary.get("summary", "N/A"))
                    except Exception as e:
                        st.error(f"Error compiling GenAI summary profiles: {e}")


# --- SECTION 4: LIVE AI INTERACTION STREAM HUB ---
elif menu == "💬 Conversation Hub":
    st.markdown('<h1 class="dashboard-title">AI Conversation Streams</h1>', unsafe_allow_html=True)
    
    col_chat_viewer, col_system_chats = st.columns([2, 1])
    
    with col_chat_viewer:
        st.markdown("### 🔍 Live Thread Inspection")
        phone = st.text_input("Enter Active Device Phone Key", key="chat_phone_lookup")
        
        if st.button("Pull Dialogue History Matrices", type="primary", use_container_width=True):
            if not phone.strip():
                st.warning("Provide target address verification number.")
            else:
                try:
                    history = requests.get(
                        f"{BASE_URL}/chat-history/{phone}",
                        headers=headers,
                        timeout=5
                    ).json()
                    
                    if isinstance(history, list) and len(history) > 0:
                        st.success(f"Stream Sync Established: Verified {len(history)} interaction sequences.")
                        
                        for chat_packet in history:
                            user_msg = chat_packet.get("user_message", chat_packet.get("content", ""))
                            ai_reply = chat_packet.get("ai_reply", chat_packet.get("response", ""))
                            
                            if user_msg:
                                with st.chat_message("user"):
                                    st.markdown(user_msg)
                            if ai_reply:
                                with st.chat_message("assistant"):
                                    st.markdown(ai_reply)
                    else:
                        st.info("System Notification: Stream execution completed but no history array logs exist here.")
                        st.json(history)
                except Exception as e:
                    st.error(f"Runtime Interface processing exception: {e}")
                    
    with col_system_chats:
        st.markdown("### 📦 System Architecture Telemetry")
        st.markdown(f'<div class="kpi-card" style="margin-bottom:1.5rem;"><div class="kpi-label">Synchronized Message Frames</div><div class="kpi-val">{len(chats)}</div></div>', unsafe_allow_html=True)
        
        with st.expander("Inspect Raw Object Schema"):
            st.json(chats)

# --- SECTION 5: BROADCAST MESSAGING CENTER ---
elif menu == "📢 Broadcast Center":

    st.markdown(
        '<h1 class="dashboard-title">Broadcast Center</h1>',
        unsafe_allow_html=True
    )

    st.info(
        "Send a WhatsApp message to all customers."
    )

    broadcast_message = st.text_area(
        "Broadcast Message",
        height=200,
        placeholder="Enter your message here..."
    )

    if st.button(
        "📤 Send Broadcast",
        type="primary",
        use_container_width=True
    ):

        if not broadcast_message.strip():

            st.warning(
                "Please enter a message."
            )

        else:

            try:

                response = requests.post(
                    f"{BASE_URL}/broadcast",
                    headers=headers,
                    json=broadcast_message
                )

                result = response.json()

                st.success(
                    f"Broadcast sent successfully to {result['message_sent_to']} customers."
                )

            except Exception as e:

                st.error(
                    f"Broadcast failed: {e}"
                )