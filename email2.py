import streamlit as st
import smtplib
import time
import os
import threading
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from groq import Groq
from streamlit_quill import st_quill
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="AI Mail Generator", 
    layout="wide",
    page_icon="📧"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1.5rem;
        padding: 0.5rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 8px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .block-container {
        padding-top: 2rem;
    }
    .email-preview {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .feature-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        text-align: center;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .generated-content {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        font-family: monospace;
        white-space: pre-wrap;
        max-height: 300px;
        overflow-y: auto;
    }
    .html-preview-container {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 0;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 400px;
        overflow: auto;
    }
    .tab-header {
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📧 AI-Powered Mail Generator</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Email Settings")
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Content")
        topic = st.text_input("Email Topic", placeholder="What is your email about?")
        category = st.selectbox(
            "Category",
            ["Marketing", "Sales", "Business", "Newsletter", "Follow-up", "Custom"]
        )
        tone = st.selectbox(
            "Tone",
            ["Formal", "Casual", "Persuasive", "Friendly", "Professional"]
        )
        variations = st.slider("Number of variations", 1, 3, 1)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    with st.container():
        if st.button("✉️ Generate Email", use_container_width=True, type="primary"):
            if not topic.strip():
                st.warning("⚠️ Please enter a topic first")
            else:
                with st.spinner("Generating email(s)..."):
                    prompt = f"""
                    Write {variations} {tone.lower()} {category.lower()} email(s) about: {topic}.
                    Provide subject, preview text, a plain text body (paragraphs only), and a clean HTML version.
                    Format the response with clear sections for Subject, Preview, and Body.
                    """

                    try:
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": "You are an expert email copywriter. Format your response with clear sections for Subject, Preview, and Body."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7,
                            max_tokens=1200
                        )

                        st.session_state.generated_email = response.choices[0].message.content
                        st.success("Email generated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating email: {str(e)}")


if "generated_email" in st.session_state:
    tab1, tab2, tab3 = st.tabs(["📩 Generated Content", "📝 Edit & Preview", "📤 Send Email"])

    with tab1:
        st.markdown('<div class="tab-header">', unsafe_allow_html=True)
        st.markdown("### AI-Generated Email Content")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="generated-content">', unsafe_allow_html=True)
        st.markdown(st.session_state.generated_email)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Use This Content", key="use_content_btn", type="primary"):
            st.session_state.plain_text_body = st.session_state.generated_email
            st.success("Content loaded into editor!")
            st.rerun()

    with tab2:
        st.markdown('<div class="tab-header">', unsafe_allow_html=True)
        st.markdown("### ✏️ Edit & Preview Your Email")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if "html_email" not in st.session_state:
            st.session_state.html_email = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Email Template</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        background-color: #f9f9f9;
                        margin: 0;
                        padding: 20px;
                    }}
                    .email-container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: #ffffff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .email-header {{
                        border-bottom: 1px solid #eee;
                        padding-bottom: 15px;
                        margin-bottom: 20px;
                    }}
                    .email-footer {{
                        border-top: 1px solid #eee;
                        padding-top: 15px;
                        margin-top: 20px;
                        font-size: 12px;
                        color: #777;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-header">
                        <h2>Email Template</h2>
                    </div>
                    <div class="email-content">
                        {st.session_state.generated_email}
                    </div>
                    <div class="email-footer">
                        <p>This email was generated using AI Mail Generator</p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("#### 📝 Rich Text Editor")
            default_text = st.session_state.get("plain_text_body", st.session_state.generated_email)

            edited_html = st_quill(
                value=default_text,
                html=True,
                key="editor",
                placeholder="Start editing your email here...",
                toolbar=[
                    ["bold", "italic", "underline", "strike"],
                    ["blockquote", "code-block"],
                    [{"header": 1}, {"header": 2}],
                    [{"list": "ordered"}, {"list": "bullet"}],
                    [{"script": "sub"}, {"script": "super"}],
                    [{"indent": "-1"}, {"indent": "+1"}],
                    [{"direction": "rtl"}],
                    [{"size": ["small", False, "large", "huge"]}],
                    [{"header": [1, 2, 3, 4, 5, 6, False]}],
                    [{"color": []}, {"background": []}],
                    [{"font": []}],
                    [{"align": []}],
                    ["clean"],
                    ["link", "image"]
                ]
            )

            if edited_html:
                st.session_state.html_email = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Email Template</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                            background-color: #f9f9f9;
                            margin: 0;
                            padding: 20px;
                        }}
                        .email-container {{
                            max-width: 600px;
                            margin: 0 auto;
                            background: #ffffff;
                            padding: 20px;
                            border-radius: 8px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }}
                        .email-header {{
                            border-bottom: 1px solid #eee;
                            padding-bottom: 15px;
                            margin-bottom: 20px;
                        }}
                        .email-footer {{
                            border-top: 1px solid #eee;
                            padding-top: 15px;
                            margin-top: 20px;
                            font-size: 12px;
                            color: #777;
                        }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <div class="email-header">
                            <h2>Email Template</h2>
                        </div>
                        <div class="email-content">
                            {edited_html}
                        </div>
                        <div class="email-footer">
                            <p>This email was generated using AI Mail Generator</p>
                        </div>
                    </div>
                </body>
                </html>
                """

        with col2:
            st.markdown("#### 👀 Live Preview")
            if "html_email" in st.session_state:
                st.markdown("**HTML Email Preview:**")
                st.markdown('<div class="html-preview-container">', unsafe_allow_html=True)
                st.components.v1.html(st.session_state.html_email, height=400, scrolling=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.download_button(
                    "⬇️ Download HTML",
                    data=st.session_state.html_email,
                    file_name="email_template.html",
                    mime="text/html",
                    key="download_html_editor",
                    use_container_width=True
                )

    with tab3:
        st.markdown('<div class="tab-header">', unsafe_allow_html=True)
        st.markdown("### 📤 Send Your Email")
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("send_email_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Sender Details")
                sender = st.text_input("Your Email (Sender)", placeholder="your.email@example.com")
                password = st.text_input("Your Email Password / App Password", type="password", placeholder="Enter your password")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Recipient Details")
                recipients = st.text_area("Recipient Emails (comma-separated)", placeholder="recipient1@example.com, recipient2@example.com")
                subject = st.text_input("Email Subject", value="AI Generated Email")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Attachments & Scheduling")
            col3, col4 = st.columns(2)
            
            with col3:
                uploaded_file = st.file_uploader("Attach a file (optional)")
            
            with col4:
                schedule_date = st.date_input("📅 Pick a Date", value=datetime.today())
                schedule_time = st.time_input("⏰ Pick a Time", value=datetime.now().time())
            st.markdown('</div>', unsafe_allow_html=True)
            
            send_button = st.form_submit_button("📤 Send Now / Schedule", type="primary", use_container_width=True)
            
            if send_button:
                if not all([sender, password, recipients, subject]):
                    st.error("⚠️ Please fill all required fields before sending.")
                else:
                    recipient_list = [r.strip() for r in recipients.split(",") if r.strip()]
                    if not recipient_list:
                        st.error("⚠️ Please enter at least one valid recipient email.")
                    else:
                        def send_email():
                            failed = []
                            for recipient in recipient_list:
                                try:
                                    msg = MIMEMultipart("alternative")
                                    msg["From"] = sender
                                    msg["To"] = recipient
                                    msg["Subject"] = subject

                                    msg.attach(MIMEText("This email requires HTML view for best experience.", "plain"))
                                    msg.attach(MIMEText(st.session_state.html_email, "html"))

                                    if uploaded_file is not None:
                                        part = MIMEBase("application", "octet-stream")
                                        part.set_payload(uploaded_file.read())
                                        encoders.encode_base64(part)
                                        part.add_header("Content-Disposition", f"attachment; filename={uploaded_file.name}")
                                        msg.attach(part)

                                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                                        server.login(sender, password)
                                        server.sendmail(sender, recipient, msg.as_string())
                                except Exception as e:
                                    failed.append((recipient, str(e)))

                            if not failed:
                                st.success(f"✅ Email sent to {len(recipient_list)} recipient(s)!")
                            else:
                                st.error(f"❌ Failed for {len(failed)} recipients: {failed}")

                        scheduled_datetime = datetime.combine(schedule_date, schedule_time)
                        now = datetime.now()
                        delay_seconds = (scheduled_datetime - now).total_seconds()

                        if delay_seconds <= 0:
                            send_email()
                        else:
                            threading.Timer(delay_seconds, send_email).start()
                            st.success(f"⏳ Email scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

else:
    st.markdown("""
    <div style='text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 2rem;'>
        <h2 style='color: white;'>Welcome to AI Mail Generator</h2>
        <p style='font-size: 1.2rem;'>Create professional emails in seconds with AI assistance</p>
        <p style='font-size: 1.1rem;'>👈 Use the sidebar to configure your email and generate content</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🤖 AI-Powered")
        st.markdown("Generate high-quality email content using advanced AI models")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### ✏️ Easy Editing")
        st.markdown("Use our rich text editor to customize your emails")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### ⏰ Scheduling")
        st.markdown("Send immediately or schedule emails for later delivery")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📋 How to Use")
    
    instructions = """
    1. **Configure Settings**: Use the sidebar to set your email topic, category, tone, and variations
    2. **Generate Email**: Click the 'Generate Email' button to create AI-powered content
    3. **Edit & Preview**: Customize your email using the rich text editor
    4. **Send Email**: Enter your credentials and send immediately or schedule for later
    """
    
    st.markdown(f'<div class="card">{instructions}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🔒 Security Notes")
    
    security = """
    - This app does not store your email credentials
    - For Gmail, enable 2-factor authentication and use an App Password
    - Be cautious when sending emails to multiple recipients
    """
    

    st.markdown(f'<div class="card">{security}</div>', unsafe_allow_html=True)
