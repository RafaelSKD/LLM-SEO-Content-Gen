import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Content Generator 🤖", page_icon="🤖")
st.title("Content Generator")

# Check if API key exists
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OPENAI_API_KEY not found in .env file")
    st.info("""
    **How to set it up:**
    1. Create a file called `.env` in the same folder as this script
    2. Add this line: `OPENAI_API_KEY=sk-proj-your-key-here`
    3. Restart the app
    """)
    st.stop()

# Show partial key info (for debugging)
with st.expander("🔍 Debug - Check Configuration"):
    st.success(f"✅ Key loaded: {api_key[:15]}...")
    st.info(f"📁 Current directory: {os.getcwd()}")
    st.info(f"🐍 Python: {sys.version}")

# Function to generate content using requests
def generate_content(api_key, prompt):
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a digital marketing expert specializing in SEO and persuasive writing. Always respond in the requested language."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=60)
    response.raise_for_status()
    
    result = response.json()
    return result['choices'][0]['message']['content']

# UI
st.markdown("---")

topic = st.text_input("📝 Topic:", placeholder="e.g., mental health, healthy eating, prevention")
platform = st.selectbox("📱 Platform:", ['Instagram', 'Facebook', 'LinkedIn', 'Blog', 'Email'])
tone = st.selectbox("🎭 Tone:", ['Neutral', 'Informative', 'Inspirational', 'Urgent', 'Casual'])
length = st.selectbox("📏 Length:", ['Short', 'Medium', 'Long'])
audience = st.selectbox("👥 Target Audience:", ['General', 'Young Adults', 'Families', 'Seniors', 'Teens'])
language = st.selectbox("🌐 Language / Língua:", ['English', 'Portuguese', 'Spanish', 'French', 'German'])

col1, col2 = st.columns(2)
with col1:
    cta = st.checkbox("📣 Include Call-to-Action (CTA)")
with col2:
    hashtags = st.checkbox("# Include Hashtags")

keywords = st.text_area("🔑 Keywords (SEO):", placeholder="e.g., wellness, preventive medicine...")

if st.button("✨ Generate Content", type="primary"):
    if not topic:
        st.warning("⚠️ Please enter a topic.")
    else:
        prompt = f"""
Write an SEO-optimized text about the topic '{topic}'.
Return only the final text, without quotes.

- Platform: {platform}
- Tone: {tone}
- Target Audience: {audience}
- Length: {length}
- Language: {language}
- {"Include a clear call-to-action." if cta else "Do not include a call-to-action."}
- {"Include relevant hashtags at the end." if hashtags else "Do not include hashtags."}
{"- Mandatory keywords: " + keywords if keywords else ""}
        """
        
        try:
            with st.spinner("🤖 Generating content..."):
                result = generate_content(api_key, prompt)
            
            st.markdown("---")
            st.subheader("📄 Generated Content:")
            st.write(result)
            
            # Download button
            st.download_button(
                label="💾 Download Text",
                data=result,
                file_name=f"content_{topic.replace(' ', '_')}.txt",
                mime="text/plain"
            )
            
            # Statistics
            with st.expander("📊 Statistics"):
                words = len(result.split())
                chars = len(result)
                lines = len(result.split('\n'))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Words", words)
                with col2:
                    st.metric("Characters", chars)
                with col3:
                    st.metric("Lines", lines)
            
            st.success("✅ Content generated successfully!")
            
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout - The API took too long to respond. Try again.")
            
        except requests.exceptions.ConnectionError as e:
            st.error("❌ Connection error")
            st.warning("""
            **Possible solutions:**
            1. Check your internet connection
            2. Update your CA certificates: `sudo dnf update ca-certificates && sudo update-ca-trust`
            3. Check if any antivirus/firewall is blocking Python
            """)
            with st.expander("🔧 Technical error"):
                st.code(str(e))
                
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ HTTP Error: {e.response.status_code}")
            
            if e.response.status_code == 401:
                st.warning("🔑 Invalid API key")
            elif e.response.status_code == 429:
                st.warning("⏱️ Rate limit reached. Please wait and try again.")
            else:
                st.warning(f"API response: {e.response.text}")
                
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            with st.expander("🔧 Technical details"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())

# Sidebar info
with st.sidebar:
    st.header("ℹ️ Information")
    st.markdown("""
    ### How to use:
    1. Choose a content topic
    2. Select the platform
    3. Define the tone and target audience
    4. Add SEO keywords
    5. Select the language
    6. Click "Generate Content"
    
    ### Tips:
    - 🔑 Keywords improve SEO
    - 📣 A clear CTA increases engagement
    - # Hashtags help with discovery
    """)
    
    st.markdown("---")
    
    # Quick API test
    if st.button("🧪 Test API"):
        with st.spinner("Testing..."):
            try:
                test_result = generate_content(api_key, "Say only 'OK'")
                st.success(f"✅ API working! Response: {test_result}")
            except Exception as e:
                st.error(f"❌ Test failed: {str(e)}")
    
    st.markdown("---")
    st.caption("Powered by OpenAI GPT-4o-mini")
    st.caption("Using requests (same library as curl)")
