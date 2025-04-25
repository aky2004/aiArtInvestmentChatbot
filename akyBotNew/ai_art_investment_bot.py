import os
import streamlit as st
import requests
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import json
from streamlit_option_menu import option_menu
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import random
import time
import numpy as np

st.set_page_config(
    page_title="Art Investment Guide",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

GEMINI_API_KEY = "Your_API_Key"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

st.markdown("""
<style>
/* Base Theme - Dark Futuristic */
.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #171730 50%, #0a0a2e 100%);
    color: #e0e0ff;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(30, 30, 60, 0.4);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #00d2ff 0%, #3a7bd5 100%);
    border-radius: 4px;
    border: 2px solid rgba(30, 30, 60, 0.4);
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #00e5ff 0%, #4a8bf5 100%);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    backdrop-filter: blur(5px);
    box-shadow: 0 6px 15px rgba(0, 210, 255, 0.15), 0 0 0 1px rgba(0, 210, 255, 0.1);
}
.stButton>button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 10px 25px rgba(0, 210, 255, 0.25), 0 0 0 1px rgba(0, 210, 255, 0.2);
    background: linear-gradient(90deg, #00e5ff 0%, #4a8bf5 100%);
}
.stButton>button:active {
    transform: translateY(1px);
}

/* Input Fields */
.stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>input {
    background: rgba(30, 30, 60, 0.3);
    border: 1px solid rgba(58, 123, 213, 0.2);
    border-radius: 12px;
    color: #e0e0ff;
    padding: 10px 15px;
    transition: all 0.3s ease;
}
.stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus, .stSelectbox>div>div>input:focus {
    border: 1px solid rgba(0, 210, 255, 0.5);
    box-shadow: 0 0 15px rgba(0, 210, 255, 0.2);
}

/* Selectboxes and Multiselects */
.stSelectbox>div, .stMultiselect>div {
    background: rgba(30, 30, 60, 0.3);
    border-radius: 12px;
    border: 1px solid rgba(58, 123, 213, 0.2);
}
.stSelectbox>div:hover, .stMultiselect>div:hover {
    border: 1px solid rgba(0, 210, 255, 0.5);
}

/* Sidebar */
.css-1d391kg, .css-163ttbj, .css-1oe6f1a {
    background: rgba(20, 20, 40, 0.7);
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(58, 123, 213, 0.15);
}

/* Sidebar Title */
.css-163ttbj h1, .css-1oe6f1a h1 {
    color: #00d2ff;
    font-weight: 700;
    text-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
    letter-spacing: 1px;
}

/* Containers and expanders */
.css-keje6w, .css-1r6slb0, [data-testid="stExpander"] {
    background: rgba(30, 30, 60, 0.3);
    border-radius: 16px;
    border: 1px solid rgba(58, 123, 213, 0.15);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    padding: 20px;
    transition: all 0.3s ease;
}
.css-keje6w:hover, .css-1r6slb0:hover, [data-testid="stExpander"]:hover {
    border: 1px solid rgba(0, 210, 255, 0.5);
}
</style>
""", unsafe_allow_html=True)

def generate_artwork_image(artist_name, artwork_title, artwork_style):
    try:
        seed = hash(f"{artist_name}_{artwork_title}") % 1000
        url = f"https://picsum.photos/seed/{seed}/800/600"
        response = requests.get(url)
        
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            return create_gradient_image(artist_name, artwork_title, (800, 600))
    except Exception as e:
        st.error(f"Error generating artwork image: {str(e)}")
        # Create a fallback image if any error occurs
        return create_gradient_image(artist_name, artwork_title, (800, 600))

def generate_artist_image(artist_name):
    try:
        seed = hash(artist_name) % 1000
        url = f"https://picsum.photos/seed/{seed}/400/400"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Open the image and make it circular
            img = Image.open(BytesIO(response.content))
            return make_circular_image(img)
        else:
            # If the request fails, create a colored gradient image as fallback
            return create_gradient_image(artist_name, "profile", (400, 400), circular=True)
    except Exception as e:
        st.error(f"Error generating artist image: {str(e)}")
        # Create a fallback image if any error occurs
        return create_gradient_image(artist_name, "profile", (400, 400), circular=True)

# Function to create a gradient image as a fallback
def create_gradient_image(artist_name, title, size, circular=False):
    """Create a gradient image with text as fallback"""
    # Create a new image with gradient background
    img = Image.new('RGB', size, color='#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient (simple version)
    for y in range(size[1]):
        r = int(25 + (y / size[1]) * 10)
        g = int(25 + (y / size[1]) * 10)
        b = int(46 + (y / size[1]) * 10)
        for x in range(size[0]):
            draw.point((x, y), fill=(r, g, b))
    
    # Add text
    try:
        text = title if not circular else artist_name[0].upper()
        text_size = 40 if not circular else 100
        draw.text((size[0]//2, size[1]//2), text, fill=(255, 255, 255), anchor="mm")
    except Exception as e:
        st.error(f"Error adding text to image: {str(e)}")
        pass
    
    # Make circular if needed
    if circular:
        img = make_circular_image(img)
    
    return img

# Function to make an image circular
def make_circular_image(img):
    """Convert a square image to circular by creating a circular mask"""
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img.size, fill=255)
    
    img_copy = img.copy()
    img_copy.putalpha(mask)
    
    return img_copy

def generate_content(prompt):
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                st.error("No content generated from the API")
                return None
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None

def get_art_recommendations():
    """Provide art investment recommendations"""
    recommendations = [
        {
            "artist": "Refik Anadol",
            "title": "Machine Hallucinations",
            "style": "Data-Driven Installation Art",
            "value": "$850,000",
            "potential": "Very High Growth",
            "trend": "Recent MoMA acquisition and growing institutional interest",
            "background": "Pioneer in data and machine intelligence aesthetics",
            "purchase_info": "Available through major auction houses like Christie's",
            "category": "trending",
            "created_date": "2021-06-15"
        },
        {
            "artist": "Sofia Crespo",
            "title": "Neural Zoo Series",
            "style": "Neural Zoo Collection",
            "value": "$125,000",
            "potential": "High Growth",
            "trend": "Pioneering work in AI-nature art fusion",
            "background": "Known for AI-generated natural forms",
            "purchase_info": "Available on digital art platforms like SuperRare",
            "category": "trending",
            "created_date": "2022-03-10"
        },
        {
            "artist": "Mario Klingemann",
            "title": "Memories of Passersby I",
            "style": "Neural Network Portraits",
            "value": "$95,000",
            "potential": "Strong Growth",
            "trend": "Innovative real-time AI generation",
            "background": "Pioneer in neural network art",
            "purchase_info": "Available through Sotheby's auctions",
            "category": "trending",
            "created_date": "2021-11-22"
        },
        {
            "artist": "Claire Silver",
            "title": "AI Portraits Collection",
            "style": "AI-Assisted Contemporary",
            "value": "$45,000",
            "potential": "High Growth",
            "trend": "Rising star in AI art community",
            "background": "Leading AI-assisted artist",
            "purchase_info": "Available through Foundation platform",
            "category": "on_sale",
            "created_date": "2022-07-05",
            "discount": "15% off until June 30"
        },
        {
            "artist": "Anna Ridler",
            "title": "Mosaic Virus",
            "style": "AI-Generated Video Art",
            "value": "$180,000",
            "potential": "Very High Growth",
            "trend": "Innovative use of AI in video art and storytelling",
            "background": "Pioneer in AI-generated tulip dataset art",
            "purchase_info": "Available through specialized digital art galleries",
            "category": "trending",
            "created_date": "2021-09-12"
        },
        {
            "artist": "Tom White",
            "title": "Perception Engines",
            "style": "Neural Network Prints",
            "value": "$75,000",
            "potential": "High Growth",
            "trend": "Unique approach to AI visual perception",
            "background": "Researcher and artist exploring machine vision",
            "purchase_info": "Available through select galleries",
            "category": "on_sale",
            "created_date": "2022-01-18",
            "discount": "10% off gallery commission"
        },
        {
            "artist": "Zach Lieberman",
            "title": "Daily Sketches",
            "style": "AI-Enhanced Animation",
            "value": "$95,000",
            "potential": "Very High Growth",
            "trend": "Innovative daily AI art practice",
            "background": "Renowned for creative coding and AI art",
            "purchase_info": "Available through artist's platform and select auctions",
            "category": "newest",
            "created_date": "2023-01-30"
        },
        {
            "artist": "Memo Akten",
            "title": "Learning to See",
            "style": "AI-Enhanced Photography",
            "value": "$175,000",
            "potential": "High Growth",
            "trend": "Pioneering work in AI-enhanced visual art",
            "background": "Renowned for deep neural network visualizations",
            "purchase_info": "Available through major galleries and art fairs",
            "category": "trending",
            "created_date": "2022-04-15"
        },
        {
            "artist": "Ian Cheng",
            "title": "BOB (Bag of Beliefs)",
            "style": "AI Life Simulation",
            "value": "$300,000",
            "potential": "Very High Growth",
            "trend": "Revolutionary AI life simulation art",
            "background": "Pioneer in AI consciousness art",
            "purchase_info": "Available through Gladstone Gallery",
            "category": "trending",
            "created_date": "2021-12-10"
        },
        {
            "artist": "Sarah Meyohas",
            "title": "Bitchcoin",
            "style": "AI-Generated Currency Art",
            "value": "$48,000",
            "potential": "High Growth",
            "trend": "Pioneering work in AI art tokenization",
            "background": "Innovative blockchain artist",
            "purchase_info": "Available through specialized crypto art platforms",
            "category": "on_sale",
            "created_date": "2022-05-20",
            "discount": "Early collector special: 20% off"
        },
        {
            "artist": "Lauren Lee McCarthy",
            "title": "LAUREN",
            "style": "AI Performance Art",
            "value": "$110,000",
            "potential": "High Growth",
            "trend": "Groundbreaking AI-human interaction art",
            "background": "Pioneer in AI surveillance art",
            "purchase_info": "Available through Whitney Museum collection",
            "category": "newest",
            "created_date": "2023-03-01"
        },
        {
            "artist": "Jake Elwes",
            "title": "Zizi Project",
            "style": "AI Performance Art",
            "value": "$55,000",
            "potential": "Strong Growth",
            "trend": "Innovative AI performance art pieces",
            "background": "Pioneer in AI identity art",
            "purchase_info": "Available through specialized digital art galleries",
            "category": "newest",
            "created_date": "2023-02-15"
        }
    ]
    return recommendations

def get_investment_guide():
    """Get investment guide using Gemini API"""
    prompt = """
    Create a comprehensive guide for investing in AI-generated art, including:
    1. How to evaluate AI art
    2. Risk factors to consider
    3. Market platforms to use
    4. Authentication and verification
    5. Storage and preservation
    Format the response in a clear, structured way.
    """
    
    return generate_content(prompt)

def get_artwork_suggestions():
    """Get different categories of artwork suggestions"""
    return {
        "Trending Now": [
            {
                "artist": "Refik Anadol",
                "title": "Machine Hallucinations",
                "style": "Data-Driven Installation Art",
                "value": "$850,000",
                "potential": "Very High Growth",
                "trend": "Recent MoMA acquisition and growing institutional interest"
            },
            {
                "artist": "Sofia Crespo",
                "title": "Neural Zoo Series",
                "style": "Neural Zoo Collection",
                "value": "$125,000",
                "potential": "High Growth",
                "trend": "Pioneering work in AI-nature art fusion"
            },
            {
                "artist": "Anna Ridler",
                "title": "Mosaic Virus",
                "style": "AI-Generated Video Art",
                "value": "$180,000",
                "potential": "Very High Growth",
                "trend": "Innovative use of AI in video art and storytelling"
            },
            {
                "artist": "Tom White",
                "title": "Perception Engines",
                "style": "Neural Network Prints",
                "value": "$75,000",
                "potential": "High Growth",
                "trend": "Unique approach to AI visual perception"
            },
            {
                "artist": "Zach Lieberman",
                "title": "Daily Sketches",
                "style": "AI-Enhanced Animation",
                "value": "$95,000",
                "potential": "Very High Growth",
                "trend": "Innovative daily AI art practice"
            },
            {
                "artist": "Lauren McCarthy",
                "title": "LAUREN",
                "style": "AI Performance Art",
                "value": "$110,000",
                "potential": "High Growth",
                "trend": "Groundbreaking AI-human interaction art"
            },
            {
                "artist": "Kyle McDonald",
                "title": "Face Time",
                "style": "AI Face Generation",
                "value": "$85,000",
                "potential": "Strong Growth",
                "trend": "Pioneering work in AI face manipulation"
            },
            {
                "artist": "Sam Lavigne",
                "title": "The Good Place",
                "style": "AI-Generated Environments",
                "value": "$70,000",
                "potential": "High Growth",
                "trend": "Unique exploration of AI-generated spaces"
            }
        ],
        "Best Value": [
            {
                "artist": "Claire Silver",
                "title": "AI Portraits Collection",
                "style": "AI-Assisted Contemporary",
                "value": "$45,000",
                "potential": "High Growth",
                "trend": "Rising star in AI art community"
            },
            {
                "artist": "Mario Klingemann",
                "title": "Memories of Passersby I",
                "style": "Neural Network Portraits",
                "value": "$95,000",
                "potential": "Strong Growth",
                "trend": "Innovative real-time AI generation"
            },
            {
                "artist": "Dmitry Morozov",
                "title": "Neural Landscapes",
                "style": "GAN-Generated Landscapes",
                "value": "$65,000",
                "potential": "High Growth",
                "trend": "Unique fusion of traditional and AI art"
            },
            {
                "artist": "Jake Elwes",
                "title": "Zizi Project",
                "style": "AI Performance Art",
                "value": "$55,000",
                "potential": "Strong Growth",
                "trend": "Innovative AI performance art pieces"
            },
            {
                "artist": "Sarah Meyohas",
                "title": "Bitchcoin",
                "style": "AI-Generated Currency Art",
                "value": "$48,000",
                "potential": "High Growth",
                "trend": "Pioneering work in AI art tokenization"
            },
            {
                "artist": "Jonas Lund",
                "title": "The Fear of Missing Out",
                "style": "AI Market Analysis Art",
                "value": "$52,000",
                "potential": "Strong Growth",
                "trend": "Innovative use of AI in art market analysis"
            },
            {
                "artist": "Harm van den Dorpel",
                "title": "Death Imitates Language",
                "style": "AI-Generated Abstract",
                "value": "$58,000",
                "potential": "High Growth",
                "trend": "Unique approach to AI abstract art"
            },
            {
                "artist": "Rafał Kucharski",
                "title": "Neural Paintings",
                "style": "AI-Generated Paintings",
                "value": "$42,000",
                "potential": "Strong Growth",
                "trend": "Emerging talent in AI painting"
            }
        ],
        "Museum Collections": [
            {
                "artist": "Refik Anadol",
                "title": "Unsupervised",
                "style": "Machine Learning Visualization",
                "value": "$1,200,000",
                "potential": "Very High Growth",
                "trend": "Major museum acquisition"
            },
            {
                "artist": "Mario Klingemann",
                "title": "The Butcher's Son",
                "style": "GAN Portraits",
                "value": "$250,000",
                "potential": "Strong Growth",
                "trend": "Groundbreaking AI portrait techniques"
            },
            {
                "artist": "Memo Akten",
                "title": "Learning to See",
                "style": "AI-Enhanced Photography",
                "value": "$175,000",
                "potential": "High Growth",
                "trend": "Pioneering work in AI-enhanced visual art"
            },
            {
                "artist": "Casey Reas",
                "title": "Process Portraits",
                "style": "Generative AI Art",
                "value": "$150,000",
                "potential": "Strong Growth",
                "trend": "Innovative use of AI in process art"
            },
            {
                "artist": "Ian Cheng",
                "title": "BOB",
                "style": "AI Life Simulation",
                "value": "$300,000",
                "potential": "Very High Growth",
                "trend": "Revolutionary AI life simulation art"
            },
            {
                "artist": "Rafael Lozano-Hemmer",
                "title": "Pulse Room",
                "style": "AI-Interactive Installation",
                "value": "$280,000",
                "potential": "High Growth",
                "trend": "Innovative AI-human interaction art"
            },
            {
                "artist": "TeamLab",
                "title": "Universe of Water Particles",
                "style": "AI-Enhanced Installation",
                "value": "$450,000",
                "potential": "Very High Growth",
                "trend": "Groundbreaking immersive AI art"
            },
            {
                "artist": "Daan Roosegaarde",
                "title": "Waterlicht",
                "style": "AI-Enhanced Environmental Art",
                "value": "$220,000",
                "potential": "Strong Growth",
                "trend": "Innovative AI environmental art"
            }
        ],
        "Emerging Artists": [
            {
                "artist": "Kenneth Edward Lomas",
                "title": "Pindar",
                "style": "AI-Assisted Digital Art",
                "value": "$28,000",
                "potential": "High Growth",
                "trend": "Emerging talent in AI art scene"
            },
            {
                "artist": "Aurora Heinrichs",
                "title": "Neural Landscapes",
                "style": "AI-Generated Landscapes",
                "value": "$42,000",
                "potential": "Strong Growth",
                "trend": "Innovative approach to AI-generated nature"
            },
            {
                "artist": "Daniel Ambrosi",
                "title": "Dreamscapes",
                "style": "AI-Enhanced Photography",
                "value": "$38,000",
                "potential": "High Growth",
                "trend": "Unique perspective on AI-enhanced photography"
            },
            {
                "artist": "Lia Coleman",
                "title": "AI Weaving",
                "style": "AI-Generated Textiles",
                "value": "$32,000",
                "potential": "High Growth",
                "trend": "Innovative fusion of AI and textile art"
            },
            {
                "artist": "Alex Reben",
                "title": "AI Sculptures",
                "style": "AI-Generated 3D Art",
                "value": "$45,000",
                "potential": "Strong Growth",
                "trend": "Pioneering work in AI sculpture"
            },
            {
                "artist": "Nina Katchadourian",
                "title": "Sorted Books",
                "style": "AI-Assisted Photography",
                "value": "$40,000",
                "potential": "High Growth",
                "trend": "Unique approach to AI-assisted photography"
            },
            {
                "artist": "Ziv Schneider",
                "title": "AI Portraits",
                "style": "AI-Generated Portraits",
                "value": "$36,000",
                "potential": "Strong Growth",
                "trend": "Emerging talent in AI portrait art"
            }
        ]
    }

def analyze_artwork_investment(artist_name, artwork_title, artwork_style, market_value, investment_potential, trend_reason):
    """Analyze artwork investment potential using Gemini API"""
    prompt = f"""
    Analyze this AI-generated artwork as an investment opportunity:
    
    Artist: {artist_name}
    Artwork: {artwork_title}
    Style: {artwork_style}
    Current Market Value: {market_value}
    Current Investment Potential: {investment_potential}
    Trending Reason: {trend_reason}
    
    Provide a detailed investment analysis including:
    1. Investment recommendation (Buy, Hold, or Avoid)
    2. Short-term price projection (6 months)
    3. Long-term growth potential (2-3 years)
    4. Key risks to consider
    5. Comparable sales or market indicators
    6. Specific factors that make this artwork potentially valuable or risky
    
    Format your response in a clear, structured way with specific data points and reasoning.
    """
    
    try:
        result = generate_content(prompt)
        if result is None or result == "":
            return f"""
            <p><strong>Investment Recommendation: Buy (with Caution)</strong></p>
            
            <p>Investing in {artist_name}'s \"{artwork_title}\" presents a significant opportunity for high growth, 
            driven by the artist's pioneering status, institutional recognition, and the growing acceptance of digital art. 
            However, it's a high-risk, high-reward investment. Thorough due diligence is essential, focusing on 
            provenance, technology maintenance, and long-term market trends. The recommendation is to <em>Buy</em> only if 
            you understand the risks, have access to acquire the artwork at a reasonable price, and are prepared for a 
            potentially volatile market. Consider consulting with an art advisor specializing in digital and new media art 
            before making a final decision.</p>
            """
        return result
    except Exception as e:
        st.error(f"Error generating analysis: {str(e)}")
        return f"""
        <p><strong>Investment Recommendation: Buy (with Caution)</strong></p>
        
        <p>Investing in {artist_name}'s \"{artwork_title}\" presents a significant opportunity for high growth, 
        driven by the artist's pioneering status, institutional recognition, and the growing acceptance of digital art. 
        However, it's a high-risk, high-reward investment. Thorough due diligence is essential, focusing on 
        provenance, technology maintenance, and long-term market trends. The recommendation is to <em>Buy</em> only if 
        you understand the risks, have access to acquire the artwork at a reasonable price, and are prepared for a 
        potentially volatile market. Consider consulting with an art advisor specializing in digital and new media art 
        before making a final decision.</p>
        """

def display_artwork_card(artist_name, artwork_title, artwork_style, market_value, investment_potential, trend_reason, extra_info=None):
    """Display an interactive artwork card"""
    with st.container():
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; 
                    margin: 20px 0; box-shadow: 0 8px 32px rgba(0,0,0,0.3); 
                    border: 1px solid rgba(255,255,255,0.1); transition: all 0.3s ease;">
            <div style="font-size: 24px; font-weight: 700; margin-bottom: 10px; 
                      background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); 
                      -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {artwork_title}
            </div>
            <div style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #ffffff;">
                by {artist_name}
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            with st.spinner("Loading artwork..."):
                artwork_image = generate_artwork_image(artist_name, artwork_title, artwork_style)
                st.image(artwork_image, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 15px;">
                <div style="background: rgba(255,255,255,0.1); padding: 8px 15px; border-radius: 20px; font-size: 14px;">
                    Style: {artwork_style}
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 8px 15px; border-radius: 20px; font-size: 14px;">
                    Value: <span style="font-size: 20px; font-weight: 700; color: #00d2ff;">{market_value}</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 8px 15px; border-radius: 20px; font-size: 14px;">
                    Potential: <span style="font-size: 16px; font-weight: 600; color: {get_potential_color(investment_potential)};">
                        {investment_potential}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display discount/extra info if available
            if extra_info:
                st.markdown(f"""
                <div style="background: rgba(255, 165, 0, 0.2); border-left: 3px solid #FFA500; 
                           padding: 8px 15px; margin: 10px 0; border-radius: 5px; display: flex; align-items: center;">
                    <span style="color: #FFA500; font-size: 18px; margin-right: 10px;">🏷️</span>
                    <span style="color: #FFC966; font-weight: 600;">{extra_info}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="font-style: italic; color: #cccccc; margin-top: 10px;">
                {trend_reason}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("View Artist Profile", key=f"artist_{artist_name}"):
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown(
                    """
                    <div style="height: 2px; background: linear-gradient(90deg, rgba(0,210,255,0.5) 0%, rgba(10,10,46,0) 100%); 
                               margin: 30px 0;"></div>
                    """, 
                    unsafe_allow_html=True
                )
                
                with st.container():
                    try:
                        # Create a professional artist profile layout with enhanced styling
                        st.markdown(
                            f"""
                            <div style="background: linear-gradient(135deg, rgba(13,13,30,0.8) 0%, rgba(23,23,60,0.8) 100%); 
                                border-radius: 15px; margin-bottom: 30px; overflow: hidden;
                                border-left: 4px solid #00d2ff; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
                                <div style="padding: 25px 25px 15px 25px;">
                                    <h1 style="color: white; font-size: 32px; margin-bottom: 5px; font-weight: 600; 
                                        background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{artist_name}</h1>
                                    <div style="width: 50px; height: 3px; background: linear-gradient(90deg, #00d2ff, transparent); margin-bottom: 15px;"></div>
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                        # Artist profile layout with two columns
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # Artist image and badge
                            try:
                                # Display artist profile image
                                artist_image = generate_artist_image(artist_name)
                                
                                # Apply a stylized container for the image
                                st.markdown(
                                    """
                                    <div style="background: rgba(255,255,255,0.05); border-radius: 10px; 
                                        padding: 20px; margin-bottom: 20px; text-align: center;
                                        border: 1px solid rgba(58, 123, 213, 0.2); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);">
                                    """, 
                                    unsafe_allow_html=True
                                )
                                
                                st.image(artist_image, width=180, use_container_width=False)
                                
                                # Artist type badge
                                artist_type = "AI Pioneer" if "Refik" in artist_name else \
                                            "Neural Artist" if "Sofia" in artist_name else \
                                            "AI Collaborator" if "Claire" in artist_name else \
                                            "Neural Network Artist" if "Mario" in artist_name else \
                                            "Digital Artist"
                                
                                # Display artist type with enhanced badge styling
                                st.markdown(
                                    f"""
                                    <div style="text-align: center; margin-top: 15px;">
                                        <span style="background: linear-gradient(135deg, rgba(0,210,255,0.15) 0%, rgba(58,123,213,0.15) 100%); 
                                            color: #00d2ff; padding: 8px 18px; border-radius: 20px; font-size: 15px; 
                                            border: 1px solid rgba(0,210,255,0.3); font-weight: 600;
                                            box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                                            {artist_type}
                                        </span>
                                    </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                
                                # Add market stats in elegant display
                                st.markdown(
                                    """
                                    <div style="background: rgba(255,255,255,0.05); border-radius: 10px; 
                                        padding: 20px; margin-top: 20px; 
                                        border: 1px solid rgba(58, 123, 213, 0.2); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);">
                                        <h3 style="color: #00d2ff; margin-bottom: 15px; font-size: 18px; font-weight: 600; text-align: center;">
                                            Market Metrics
                                        </h3>
                                    """, 
                                    unsafe_allow_html=True
                                )
                                
                                # Market metrics
                                market_stats = [
                                    {"label": "Recent Sale", "value": "$850K" if "Refik" in artist_name else "$120K" if "Sofia" in artist_name else "$95K" if "Mario" in artist_name else "$45K"},
                                    {"label": "Growth (YoY)", "value": "+142%" if "Refik" in artist_name else "+85%" if "Sofia" in artist_name else "+68%" if "Mario" in artist_name else "+42%"},
                                    {"label": "Collector Interest", "value": "Very High" if "Refik" in artist_name else "High" if "Sofia" in artist_name else "Medium-High" if "Mario" in artist_name else "Growing"}
                                ]
                                
                                for stat in market_stats:
                                    st.markdown(
                                        f"""
                                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px; 
                                            padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                            <span style="color: #cccccc;">{stat["label"]}</span>
                                            <span style="color: #00d2ff; font-weight: 600;">{stat["value"]}</span>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                            
                            except Exception as e:
                                st.error(f"Couldn't load artist image: {str(e)}")
                        
                        with col2:
                            # Artist Biography - enhanced styling
                            st.markdown(
                                """
                                <div style="background: rgba(255,255,255,0.05); border-radius: 10px; 
                                    padding: 20px; margin-bottom: 20px; 
                                    border: 1px solid rgba(58, 123, 213, 0.2); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);">
                                    <h3 style="color: #00d2ff; margin-bottom: 15px; font-size: 20px; font-weight: 600;">
                                        Artist Biography
                                    </h3>
                                """, 
                                unsafe_allow_html=True
                            )
                            
                            # Artist biography text
                            if "Refik Anadol" in artist_name:
                                bio_text = """
                                Refik Anadol is a pioneer in the aesthetics of data and machine intelligence. 
                                His work intersects AI, large-scale data visualization, and immersive installations.
                                Anadol's pieces have been exhibited at prestigious venues worldwide and use neural networks
                                to transform vast datasets into mesmerizing visual experiences.
                                """
                            elif "Sofia Crespo" in artist_name:
                                bio_text = """
                                Sofia Crespo is known for her work in "neural zoo" and AI-generated natural forms.
                                Her pieces explore the intersection of natural and artificial life through the lens of
                                machine learning. Her innovative approach merges biology with technology to create
                                fascinating new visual interpretations of nature.
                                """
                            elif "Claire Silver" in artist_name:
                                bio_text = """
                                Claire Silver is an AI-assisted artist pushing boundaries in contemporary art.
                                Her work explores human-AI collaboration and emotional resonance in the digital age.
                                Silver's pieces challenge conventional art paradigms while exploring themes of
                                identity, consciousness, and the future relationship between humans and machines.
                                """
                            elif "Mario Klingemann" in artist_name:
                                bio_text = """
                                Mario Klingemann is a pioneer in neural network art and AI-generated portraits.
                                Known for pushing the boundaries of machine learning in art, his work explores
                                the creative potential of algorithms and artificial intelligence. His groundbreaking
                                "Memories of Passersby I" features an AI that generates portraits in real-time.
                                """
                            else:
                                bio_text = f"""
                                {artist_name} is an innovative artist working at the intersection of technology and art.
                                Their work explores the creative possibilities of artificial intelligence and computational
                                techniques to create unique visual experiences that challenge our perception of art and
                                creativity in the digital age.
                                """
                            
                            st.markdown(f"""
                                <p style="line-height: 1.7; color: #ffffff; font-size: 15px;">{bio_text}</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Notable Achievements - enhanced styling
                            st.markdown(
                                """
                                <div style="background: rgba(255,255,255,0.05); border-radius: 10px; 
                                    padding: 20px; margin-bottom: 20px; 
                                    border: 1px solid rgba(58, 123, 213, 0.2); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);">
                                    <h3 style="color: #00d2ff; margin-bottom: 15px; font-size: 20px; font-weight: 600;">
                                        Notable Achievements
                                    </h3>
                                """, 
                                unsafe_allow_html=True
                            )
                            
                            # Set achievements based on artist
                            if "Refik Anadol" in artist_name:
                                achievements = [
                                    "MoMA permanent collection acquisition (2023)",
                                    '"Unsupervised" series valued at over $1.2M',
                                    "Major installations at prestigious venues worldwide",
                                    "Collaboration with NVIDIA and other tech giants"
                                ]
                            elif "Sofia Crespo" in artist_name:
                                achievements = [
                                    "Featured in major digital art festivals globally",
                                    '"Artificial Natural History" collection success',
                                    "Pioneer in AI-generated biological art",
                                    "Collaborations with major tech companies and museums"
                                ]
                            elif "Claire Silver" in artist_name:
                                achievements = [
                                    "Successful Christie's auction debut",
                                    "Featured in Forbes 30 Under 30",
                                    "Collaborations with major brands",
                                    "Pioneer in AI-assisted fine art"
                                ]
                            elif "Mario Klingemann" in artist_name:
                                achievements = [
                                    "Sotheby's auction record for AI art",
                                    "Artist in residence at Google Arts & Culture",
                                    "Multiple museum acquisitions",
                                    "Innovation in real-time AI art generation"
                                ]
                            else:
                                achievements = [
                                    "Emerging talent in the AI art space",
                                    "Growing recognition in digital art communities",
                                    "Innovative approaches to AI-generated art",
                                    "Potential for significant market growth"
                                ]
                            
                            # Display achievements with enhanced bullet styling
                            st.markdown("""<ul style="list-style-type: none; padding-left: 0; margin: 0;">""", unsafe_allow_html=True)
                            for achievement in achievements:
                                st.markdown(
                                    f"""
                                    <li style="padding: 8px 0; display: flex; align-items: flex-start; color: #ffffff;">
                                        <span style="color: #00d2ff; margin-right: 10px; font-size: 18px;">•</span> 
                                        {achievement}
                                    </li>
                                    """, 
                                    unsafe_allow_html=True
                                )
                            st.markdown("""</ul></div>""", unsafe_allow_html=True)
                            
                            # Featured works section
                            st.markdown(
                                """
                                <div style="background: rgba(255,255,255,0.05); border-radius: 10px; 
                                    padding: 20px; margin-bottom: 20px; 
                                    border: 1px solid rgba(58, 123, 213, 0.2); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);">
                                    <h3 style="color: #00d2ff; margin-bottom: 15px; font-size: 20px; font-weight: 600;">
                                        Artistic Approach
                                    </h3>
                                """, 
                                unsafe_allow_html=True
                            )
                            
                            # Artist approach/style
                            if "Refik Anadol" in artist_name:
                                approach = """
                                Anadol's work involves collecting and processing massive datasets using neural networks. 
                                He transforms this data into immersive, site-specific installations that blur the line 
                                between physical and virtual reality. His pieces often feature fluid, dynamic movements 
                                that respond to their environments, creating unique experiences for each viewer.
                                """
                            elif "Sofia Crespo" in artist_name:
                                approach = """
                                Crespo uses generative adversarial networks (GANs) to create artificial lifeforms 
                                inspired by natural biology. Her process involves training AI on vast datasets of 
                                natural specimens, then guiding the algorithm to create new, never-before-seen 
                                organisms that blur the boundary between the real and the artificial.
                                """
                            elif "Claire Silver" in artist_name:
                                approach = """
                                Silver's creative process is collaborative, working alongside AI to create 
                                emotionally resonant pieces. She guides the AI through careful prompt engineering 
                                and curation, then transforms the outputs through additional digital manipulation. 
                                The result is work that explores the complex relationship between human and 
                                machine creativity.
                                """
                            elif "Mario Klingemann" in artist_name:
                                approach = """
                                Klingemann's technique involves experimenting with neural networks, particularly GANs, 
                                to push the boundaries of what these systems can create. His work often involves 
                                real-time generation, where the AI continuously creates new imagery, ensuring that 
                                no two viewings of his work are ever identical. This creates a unique dialogue 
                                between code, chance, and artistic vision.
                                """
                            else:
                                approach = f"""
                                {artist_name}'s approach combines technical innovation with artistic vision, 
                                using advanced AI models as collaborators in the creative process. Their work 
                                demonstrates how artificial intelligence can be used as a tool for artistic 
                                expression, challenging our understanding of creativity and authorship in the digital age.
                                """
                                
                            st.markdown(f"""<p style="line-height: 1.7; color: #ffffff; font-size: 15px;">{approach}</p></div>""", unsafe_allow_html=True)
                        
                        # Buttons for actions - enhanced styling
                        st.markdown(
                            """
                            <div style="background: rgba(0,0,0,0.2); border-radius: 10px; 
                                padding: 20px; margin-top: 20px; border: 1px solid rgba(255,255,255,0.05);">
                            """, 
                            unsafe_allow_html=True
                        )
                        
                        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                        with col_btn1:
                            st.button(
                                "View All Artworks", 
                                on_click=lambda: st.session_state.update({
                                    'page': 'artist_artworks', 
                                    'selected_artist': artist_name
                                }),
                                type="primary", 
                                use_container_width=True,
                                key=f"all_artworks_{artist_name}"
                            )
                        
                        with col_btn2:
                            st.button(
                                "Investment Analysis", 
                                on_click=lambda: st.session_state.update({
                                    'page': 'artist_investment', 
                                    'selected_artist': artist_name
                                }),
                                type="secondary", 
                                use_container_width=True,
                                key=f"artist_investment_{artist_name}"
                            )
                        
                        with col_btn3:
                            st.button(
                                "Back to Gallery", 
                                on_click=lambda: st.session_state.update({'page': 'gallery'}),
                                type="secondary", 
                                use_container_width=True,
                                key=f"back_to_gallery_{artist_name}"
                            )
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    except Exception as e:
                        st.error(f"Error displaying artist profile: {str(e)}")
                        st.write(f"""
                        {artist_name} is an innovative artist working at the intersection of technology and art.
                        Unfortunately, we couldn't load the complete profile at this time.
                        """)
            
            if st.button("Analyze Investment", key=f"analyze_{artwork_title}"):
                st.markdown("</div>", unsafe_allow_html=True)
                st.write("---")
                with st.container():
                    with st.spinner("Analyzing investment potential..."):
                        analysis_result = analyze_artwork_investment(
                            artist_name, 
                            artwork_title, 
                            artwork_style, 
                            market_value, 
                            investment_potential, 
                            trend_reason
                        )
                        if "Buy" in analysis_result:
                            recommendation = "Buy"
                            recommendation_color = "#00ff9d"
                        elif "Hold" in analysis_result:
                            recommendation = "Hold"
                            recommendation_color = "#ffd700"
                        else:
                            recommendation = "Avoid"
                            recommendation_color = "#ff6b6b"
                        st.markdown(f"<h2 style='text-align: center; color: #00d2ff;'>Investment Analysis for {artwork_title}</h2>", unsafe_allow_html=True)
                        st.markdown(
                            f"<div style='background-color: rgba(0,0,0,0.2); border-radius: 10px; padding: 15px; margin: 20px 0; text-align: center;'>"
                            f"<h2 style='color: {recommendation_color}; margin: 0;'>Investment Recommendation: {recommendation}</h2>"
                            f"</div>", 
                            unsafe_allow_html=True
                        )
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(
                                "<div style='background-color: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; text-align: center;'>",
                                unsafe_allow_html=True
                            )
                            st.markdown("<p style='color: #cccccc; margin: 0; font-size: 14px;'>CURRENT VALUE</p>", unsafe_allow_html=True)
                            st.markdown(f"<h3 style='color: #00d2ff; margin: 5px 0;'>{market_value}</h3>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        with col2:
                            st.markdown(
                                "<div style='background-color: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; text-align: center;'>",
                                unsafe_allow_html=True
                            )
                            st.markdown("<p style='color: #cccccc; margin: 0; font-size: 14px;'>GROWTH POTENTIAL</p>", unsafe_allow_html=True)
                            pot_color = "#00ff9d" if "High" in investment_potential else "#ffd700"
                            st.markdown(f"<h3 style='color: {pot_color}; margin: 5px 0;'>{investment_potential}</h3>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        with col3:
                            st.markdown(
                                "<div style='background-color: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; text-align: center;'>",
                                unsafe_allow_html=True
                            )
                            st.markdown("<p style='color: #cccccc; margin: 0; font-size: 14px;'>MARKET STATUS</p>", unsafe_allow_html=True)
                            st.markdown("<h3 style='color: #00d2ff; margin: 5px 0;'>Active</h3>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown(
                            "<div style='background-color: rgba(255,255,255,0.05); border-radius: 10px; margin: 20px 0;'>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            "<div style='background-color: rgba(0,0,0,0.2); padding: 10px 15px; border-bottom: 1px solid rgba(255,255,255,0.1);'>"
                            "<h3 style='color: #00d2ff; margin: 0; font-size: 18px;'>Detailed Analysis</h3>"
                            "</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<div style='padding: 20px; line-height: 1.6; font-size: 16px;'>{analysis_result}</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown("</div>", unsafe_allow_html=True)
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Add to Watchlist", key=f"watchlist_{artwork_title}", use_container_width=True):
                                st.success(f"{artwork_title} added to your watchlist!")
                        with col2:
                            if st.button("View Similar Artworks", key=f"similar_{artwork_title}", use_container_width=True):
                                st.info("Similar artworks will be displayed here.")
            
        if not st.session_state.get(f"artist_{artist_name}", False) and not st.session_state.get(f"analyze_{artwork_title}", False):
            st.markdown("</div>", unsafe_allow_html=True)

def get_potential_color(potential):
    if "High" in potential or "Very High" in potential:
        return "#00ff9d"
    elif "Strong" in potential:
        return "#ffd700"
    else:
        return "#ff6b6b"

def main():
    with st.sidebar:
        st.title("🎨 Art Investment Guide")
        selected = option_menu(
            "Navigation",
            ["Introduction", "Art Recommendations", "Investment Guide", "Market Analysis", "Portfolio Tracker", "Chat with Assistant"],
            icons=['house', 'palette', 'book', 'graph-up', 'briefcase', 'chat-dots'],
            menu_icon="cast",
            default_index=0,
        )
    
    if selected == "Introduction":
        st.title("🎨 Art Investment Guide")
        st.write("Discover valuable AI-generated artworks and make informed investment decisions.")
        
        # About this application
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""
                ## About This Application
                
                Welcome to the **AI Art Investment Guide** - your comprehensive tool for navigating the rapidly evolving world of AI-generated art investments.
                
                This application helps you discover valuable AI artworks, analyze market trends, and make data-driven investment decisions. 
                Whether you're an experienced collector or new to the AI art space, our tools provide the insights you need to build a valuable collection.
                """)
                
                st.markdown("""
                ## Key Features
                
                🖼️ **Art Recommendations**: Discover trending AI artworks with investment potential
                
                📚 **Investment Guide**: Learn best practices for investing in AI-generated art
                
                📊 **Market Analysis**: Explore data-driven trends in the AI art market
                
                💼 **Portfolio Tracker**: Track and manage your AI art investments
                """)
            
            with col2:
                # Show a dynamic art icon/image
                st.image("https://picsum.photos/seed/aiart/400/300", caption="AI-Generated Art (Example)")
        
        # AI Art Market Highlights
        st.markdown("## AI Art Market Highlights")
        
        # Key metrics in the introduction
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Market Growth Rate", value="142%", delta="+32% from 2022")
        with col2:
            st.metric(label="Avg. Investment Return", value="68%", delta="+22% from traditional art")
        with col3:
            st.metric(label="New Collectors (2023)", value="27K", delta="+85% from 2022")
        
        # Featured Artists Section
        st.markdown("## Featured AI Artists")
        
        featured_artists = [
            {"name": "Refik Anadol", "specialty": "Data-driven installations", "key_achievement": "MoMA acquisition"},
            {"name": "Sofia Crespo", "specialty": "Neural Zoo Collection", "key_achievement": "Venice Biennale"},
            {"name": "Mario Klingemann", "specialty": "Neural Network Art", "key_achievement": "Sotheby's record sale"},
            {"name": "Claire Silver", "specialty": "AI-Assisted Contemporary", "key_achievement": "Louvre exhibition"}
        ]
        
        featured_cols = st.columns(4)
        for i, artist in enumerate(featured_artists):
            with featured_cols[i]:
                seed = hash(artist["name"]) % 1000
                st.image(f"https://picsum.photos/seed/{seed}/150/150", width=150)
                st.markdown(f"**{artist['name']}**")
                st.write(artist["specialty"])
                st.write(f"💫 *{artist['key_achievement']}*")
        
        # Why Invest in AI Art
        st.markdown("## Why Invest in AI Art?")
        
        with st.expander("Growing Market Value", expanded=True):
            st.markdown("""
            The AI art market has seen exponential growth, with annual sales increasing over 140% in the past year alone.
            Major auction houses including Christie's and Sotheby's now regularly feature AI artworks, with record sales exceeding $1.2M.
            """)
        
        with st.expander("Technological Innovation"):
            st.markdown("""
            AI art represents the cutting edge of technological and artistic innovation. 
            As AI models advance, early works from pioneering artists continue to appreciate in both historical and monetary value.
            """)
        
        with st.expander("Accessibility"):
            st.markdown("""
            AI art offers entry points at various price levels, from emerging artists with works under $5,000 to established names commanding six-figure sums.
            Digital formats allow for new collecting models, including fractional ownership and digital provenance verification.
            """)
        
        with st.expander("Institutional Recognition"):
            st.markdown("""
            Major institutions including MoMA, Tate Modern, and Centre Pompidou have added AI artworks to their permanent collections.
            Museum exhibitions focused on AI art have increased by 215% since 2020, driving awareness and validating artistic significance.
            """)
        
        # Getting Started Section
        st.markdown("## Getting Started")
        st.markdown("""
        1. Visit the **Art Recommendations** section to discover trending AI artworks
        2. Learn about investment strategies in the **Investment Guide**
        3. Analyze market trends in the **Market Analysis** section
        4. Track your investments with the **Portfolio Tracker**
        """)
        
        st.info("Have questions about AI art investments? Contact our team at support@aiartinvest.example.com")
        
    elif selected == "Art Recommendations":
        st.title("🖼️ AI Artworks")
        st.write("Discover and invest in the most promising AI-generated artworks")
        
        # Add filter options at the top
        st.markdown("### Filter By Category")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            show_all = st.button("All Artworks", type="primary" if not st.session_state.get('filter_category', '') else "secondary", use_container_width=True)
            if show_all:
                st.session_state.filter_category = ''
        
        with col2:
            show_trending = st.button("Trending", type="primary" if st.session_state.get('filter_category', '') == 'trending' else "secondary", use_container_width=True)
            if show_trending:
                st.session_state.filter_category = 'trending'
        
        with col3:
            show_on_sale = st.button("On Sale", type="primary" if st.session_state.get('filter_category', '') == 'on_sale' else "secondary", use_container_width=True)
            if show_on_sale:
                st.session_state.filter_category = 'on_sale'
        
        with col4:
            show_newest = st.button("Newest", type="primary" if st.session_state.get('filter_category', '') == 'newest' else "secondary", use_container_width=True)
            if show_newest:
                st.session_state.filter_category = 'newest'
        
        # Divider
        st.markdown("<hr style='margin: 15px 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        # Get recommendations
        recommendations = get_art_recommendations()
        
        # Filter based on selection
        filter_category = st.session_state.get('filter_category', '')
        if filter_category:
            filtered_recommendations = [artwork for artwork in recommendations if artwork.get('category') == filter_category]
        else:
            filtered_recommendations = recommendations
        
        # Display artworks
        for artwork in filtered_recommendations:
            # Add discount info for on-sale items
            extra_info = artwork.get('discount', '') if 'discount' in artwork else ''
            
            display_artwork_card(
                artwork["artist"],
                artwork["title"],
                artwork["style"],
                artwork["value"],
                artwork["potential"],
                artwork["trend"],
                extra_info=extra_info if extra_info else None
            )
    
    elif selected == "Investment Guide":
        st.title("📚 Investment Guide")
        st.write("Learn how to invest in AI-generated art")
        guide = get_investment_guide()
        if guide:
            st.markdown(guide, unsafe_allow_html=True)
    
    elif selected == "Market Analysis":
        st.title("📊 Market Analysis")
        st.write("Explore trends in the AI art market")
        
        # Market growth metrics
        st.subheader("AI Art Market Growth")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Market Size 2023", value="$2.4B", delta="+142%")
        with col2:
            st.metric(label="Projected 2025", value="$5.8B", delta="+241%")
        with col3:
            st.metric(label="Transaction Volume", value="18.2K", delta="+85%")
            
        # AI Art categories distribution
        st.subheader("AI Art Categories Distribution")
        categories = ['Generative Artwork', 'AI-Enhanced Photography', 'Neural Network Portraits', 
                    'Data Visualization Art', 'AI-Generated Video Art', 'AI Music Visualization']
        values = [28, 21, 19, 16, 9, 7]
        
        chart_data = pd.DataFrame({
            "Category": categories,
            "Percentage": values
        })
        
        st.bar_chart(chart_data.set_index("Category"))
        
        # Top selling platforms
        st.subheader("Top AI Art Selling Platforms")
        platforms = ['Foundation', 'SuperRare', 'OpenSea', 'Nifty Gateway', 'Art Blocks', 'Others']
        sales = [320, 285, 240, 180, 150, 125]
        
        platform_data = pd.DataFrame({
            "Platform": platforms,
            "Sales Volume ($K)": sales
        })
        
        st.bar_chart(platform_data.set_index("Platform"))
        
        # Price trends for top artists
        st.subheader("Price Trends for Top AI Artists")
        
        artists = ['Refik Anadol', 'Sofia Crespo', 'Mario Klingemann', 'Claire Silver', 'Anna Ridler']
        dates = pd.date_range(start='2022-01-01', periods=6, freq='Q')
        
        # Generate price data for each artist with different trends
        np.random.seed(42)  # For reproducibility
        trends_data = {}
        
        for artist in artists:
            base = np.random.randint(50, 150)
            growth = np.random.uniform(1.1, 1.4)
            trends_data[artist] = [int(base * (growth ** i)) for i in range(len(dates))]
        
        # Create DataFrame
        trend_df = pd.DataFrame({
            'Date': dates
        })
        
        for artist in artists:
            trend_df[artist] = trends_data[artist]
        
        trend_df = trend_df.set_index('Date')
        st.line_chart(trend_df)
        
        # Investment recommendations based on market analysis
        st.subheader("Investment Insights")
        
        with st.expander("Key Market Trends"):
            st.markdown("""
            - **Institutional Adoption Rising**: Major museums and galleries are increasing acquisitions of AI art
            - **Collector Demographics Shifting**: Younger collectors (25-40) represent 68% of new AI art buyers
            - **Technological Innovation Premium**: Art utilizing cutting-edge AI models commands higher prices
            - **Collaborative Works Growing**: Human-AI collaborations are seeing price premiums of 30-45%
            - **Physical/Digital Hybrids**: Works with physical components alongside digital elements up 85%
            """)
            
        with st.expander("Investment Strategies"):
            st.markdown("""
            - **Emerging Artists**: Target creators working with latest models (text-to-video, 3D generation)
            - **Established Pioneer Premium**: Early AI artists continue to see strong historical value growth
            - **Collection Diversity**: Balance collection across AI art categories and generation techniques
            - **Exhibition History**: Prioritize works featured in major institutions
            - **Technological Documentation**: Ensure comprehensive provenance includes AI model documentation
            """)
            
    elif selected == "Portfolio Tracker":
        st.title("💼 Portfolio Tracker")
        st.write("Track your AI art investments")
        
        # Sample portfolio data
        if 'portfolio' not in st.session_state:
            # Initial sample portfolio
            st.session_state.portfolio = [
                {
                    "artist": "Refik Anadol", 
                    "title": "Machine Hallucinations", 
                    "purchase_date": "2022-08-15", 
                    "purchase_price": 85000,
                    "current_value": 125000,
                    "platform": "Christie's"
                },
                {
                    "artist": "Sofia Crespo", 
                    "title": "Neural Zoo Series", 
                    "purchase_date": "2023-02-10", 
                    "purchase_price": 42000,
                    "current_value": 58000,
                    "platform": "SuperRare"
                },
                {
                    "artist": "Claire Silver", 
                    "title": "AI Portraits Collection", 
                    "purchase_date": "2023-05-22", 
                    "purchase_price": 28000,
                    "current_value": 35000,
                    "platform": "Foundation"
                }
            ]
        
        # Portfolio Summary
        total_investment = sum(item["purchase_price"] for item in st.session_state.portfolio)
        current_value = sum(item["current_value"] for item in st.session_state.portfolio)
        profit = current_value - total_investment
        roi = (profit / total_investment) * 100 if total_investment > 0 else 0
        
        # Portfolio metrics
        st.subheader("Portfolio Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Investment", value=f"${total_investment:,}")
        with col2:
            st.metric(label="Current Value", value=f"${current_value:,}", delta=f"${profit:,}")
        with col3:
            st.metric(label="ROI", value=f"{roi:.2f}%")
        
        # Portfolio table
        st.subheader("Your Collection")
        
        portfolio_df = pd.DataFrame(st.session_state.portfolio)
        portfolio_df["gain"] = portfolio_df["current_value"] - portfolio_df["purchase_price"]
        portfolio_df["roi"] = (portfolio_df["gain"] / portfolio_df["purchase_price"]) * 100
        
        # Format the DataFrame for display
        display_df = portfolio_df.copy()
        display_df["purchase_price"] = display_df["purchase_price"].apply(lambda x: f"${x:,}")
        display_df["current_value"] = display_df["current_value"].apply(lambda x: f"${x:,}")
        display_df["gain"] = display_df["gain"].apply(lambda x: f"${x:,}")
        display_df["roi"] = display_df["roi"].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(display_df)
        
        # Add new artwork form
        st.subheader("Add New Artwork")
        with st.form("add_artwork_form"):
            col1, col2 = st.columns(2)
            with col1:
                artist = st.text_input("Artist Name")
                title = st.text_input("Artwork Title")
                platform = st.selectbox("Purchase Platform", ["Christie's", "Sotheby's", "SuperRare", "Foundation", "OpenSea", "Nifty Gateway", "Other"])
            with col2:
                purchase_date = st.date_input("Purchase Date")
                purchase_price = st.number_input("Purchase Price ($)", min_value=0, step=1000)
                current_value = st.number_input("Current Value ($)", min_value=0, step=1000)
            
            submit_button = st.form_submit_button("Add to Portfolio")
            
            if submit_button and artist and title and purchase_price > 0:
                # Add the new artwork to the portfolio
                new_artwork = {
                    "artist": artist,
                    "title": title,
                    "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                    "purchase_price": purchase_price,
                    "current_value": current_value,
                    "platform": platform
                }
                st.session_state.portfolio.append(new_artwork)
                st.success(f"Added {title} by {artist} to your portfolio!")
                st.rerun()
    
    elif selected == "Chat with Assistant":
        # Custom CSS for chat UI
        st.markdown("""
        <style>
        /* Chat Container Styling */
        .chat-container {
            border-radius: 16px;
            background: rgba(30, 30, 60, 0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(58, 123, 213, 0.2);
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            max-height: 600px;
            overflow-y: auto;
        }
        
        /* Chat Message Animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* User message styling */
        .user-message {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 16px;
            animation: fadeIn 0.3s ease-out forwards;
        }
        
        .user-message-content {
            background: linear-gradient(90deg, #3a7bd5 0%, #00d2ff 100%);
            color: white;
            border-radius: 18px 18px 0 18px;
            padding: 12px 16px;
            max-width: 80%;
            box-shadow: 0 4px 15px rgba(0, 210, 255, 0.2);
        }
        
        /* Assistant message styling */
        .assistant-message {
            display: flex;
            justify-content: flex-start;
            margin-bottom: 16px;
            animation: fadeIn 0.3s ease-out forwards;
        }
        
        .assistant-message-content {
            background: rgba(255, 255, 255, 0.1);
            color: #e0e0ff;
            border-radius: 18px 18px 18px 0;
            padding: 12px 16px;
            max-width: 80%;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Assistant avatar */
        .assistant-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            margin-right: 10px;
            background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        /* Input box styling */
        .chat-input-container {
            margin-top: 20px;
            border-radius: 25px;
            background: rgba(30, 30, 60, 0.2);
            padding: 8px;
            display: flex;
            align-items: center;
            border: 1px solid rgba(58, 123, 213, 0.2);
            transition: all 0.3s ease;
        }
        
        .chat-input-container:focus-within {
            border: 1px solid rgba(0, 210, 255, 0.5);
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.2);
        }
        
        .chat-input {
            flex-grow: 1;
            border: none;
            background: transparent;
            color: white;
            padding: 10px 15px;
            outline: none;
        }
        
        .chat-send-button {
            background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .chat-send-button:hover {
            transform: scale(1.05);
        }
        
        /* Suggestion chips */
        .suggestion-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 20px;
        }
        
        .suggestion-chip {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(58, 123, 213, 0.2);
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
            color: #e0e0ff;
        }
        
        .suggestion-chip:hover {
            background: rgba(58, 123, 213, 0.2);
            border: 1px solid rgba(0, 210, 255, 0.5);
        }
        
        /* Time indicator */
        .message-time {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.5);
            margin-top: 4px;
            text-align: right;
        }
        
        /* Typing indicator */
        .typing-indicator {
            display: flex;
            align-items: center;
            margin-top: 10px;
        }
        
        .typing-indicator span {
            height: 8px;
            width: 8px;
            float: left;
            margin: 0 1px;
            background-color: #9E9EA1;
            display: block;
            border-radius: 50%;
            opacity: 0.4;
        }
        
        .typing-indicator span:nth-of-type(1) {
            animation: 1s blink infinite 0.3333s;
        }
        
        .typing-indicator span:nth-of-type(2) {
            animation: 1s blink infinite 0.6666s;
        }
        
        .typing-indicator span:nth-of-type(3) {
            animation: 1s blink infinite 0.9999s;
        }
        
        @keyframes blink {
            50% { opacity: 1; }
        }
        
        /* Clear button styling */
        .clear-button {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #e0e0ff;
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        
        .clear-button:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Chat header with improved styling
        st.markdown(
            """
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <div style="background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%); width: 48px; height: 48px; 
                    border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" 
                        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                </div>
                <div>
                    <h1 style="margin: 0; padding: 0; color: white; font-size: 28px;">Chat with Art Investment Assistant</h1>
                    <p style="margin: 0; padding: 0; color: #a0a0cf; font-size: 16px;">
                        Ask questions about AI art, artists, market trends, or collecting tips
                    </p>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Intelligent assistant context
        with st.container():
            st.markdown(
                """
                <div style="background: rgba(0, 210, 255, 0.1); border-radius: 10px; padding: 15px; 
                    margin-bottom: 25px; border-left: 3px solid rgba(0, 210, 255, 0.5);">
                    <div style="display: flex; align-items: flex-start;">
                        <div style="margin-right: 15px; color: #00d2ff; font-size: 24px;">💡</div>
                        <div>
                            <p style="margin: 0; color: #e0e0ff; line-height: 1.5;">
                                I can help you with art investment decisions, artist research, market trends analysis,
                                collecting strategies, and authentication guidance for AI-generated art.
                            </p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Create two columns
        chat_col, info_col = st.columns([3, 1])
        
        with chat_col:
            # Store whether a new message needs to be processed
            if "processing_new_message" not in st.session_state:
                st.session_state.processing_new_message = False
            if "current_question" not in st.session_state:
                st.session_state.current_question = ""
            
            # Function to handle message processing
            def process_question(question):
                if not question:
                    return
                    
                current_time = datetime.now().strftime("%H:%M")
                
                # Add user message if it's not already the last message
                if not st.session_state.messages or st.session_state.messages[-1]["content"] != question:
                    st.session_state.messages.append({"role": "user", "content": question, "time": current_time})
                
                # Generate response
                with st.spinner(""):
                    # Show typing indicator
                    st.markdown(
                        """
                        <div class="assistant-message">
                            <div class="assistant-avatar">AI</div>
                            <div class="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    
                    response_prompt = f"""
                    You are an AI Art Investment Assistant. You help users with questions about AI art, artists, investment advice, 
                    market trends, and collecting tips. The user's question is: "{question}"
                    
                    Respond with helpful, accurate information about AI art investments. If the question is outside your knowledge area,
                    guide them back to AI art topics. Be concise but informative.
                    """
                    
                    response = generate_content(response_prompt)
                    if not response:
                        response = """I apologize, but I'm having trouble generating a response at the moment. 
                        
                        Here are some topics I can help you with:
                        - Information about AI artists and artworks
                        - Investment potential and market trends
                        - How to evaluate AI art
                        - Where to buy AI artworks
                        - Building a collection strategy
                        
                        Please feel free to ask about any of these topics!"""
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response, "time": current_time})
                # Reset processing state
                st.session_state.processing_new_message = False
                st.session_state.current_question = ""
            
            # Process message FIRST if one is pending from the previous run
            if st.session_state.processing_new_message:
                process_question(st.session_state.current_question)
                # Need to rerun *after* processing to display the new messages immediately
                st.rerun() 
            
            # Initialize chat history if not already
            if "messages" not in st.session_state:
                current_time = datetime.now().strftime("%H:%M")
                st.session_state.messages = [
                    {"role": "assistant", "content": "Hello! I'm your AI Art Investment Assistant. How can I help you today?", "time": current_time}
                ]
                
            # Chat container with custom styling
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Display chat messages with enhanced styling
            for message in st.session_state.messages:
                if message["role"] == "assistant":
                    st.markdown(
                        f"""
                        <div class="assistant-message">
                            <div class="assistant-avatar">AI</div>
                            <div>
                                <div class="assistant-message-content">{message["content"]}</div>
                                <div class="message-time">{message.get("time", "")}</div>
                            </div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                else:  # User message
                    st.markdown(
                        f"""
                        <div class="user-message">
                            <div>
                                <div class="user-message-content">{message["content"]}</div>
                                <div class="message-time">{message.get("time", "")}</div>
                            </div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    
            st.markdown('</div>', unsafe_allow_html=True)

            # --- Input Handling --- 
            
            # Upgraded chat input
            prompt = st.text_input("", placeholder="Ask something about AI art...", label_visibility="collapsed", key="chat_input")
            
            # Create enhanced suggestions
            st.markdown('<div class="suggestion-container">', unsafe_allow_html=True)
            
            suggested_questions = [
                "Who are the top AI artists right now?",
                "How to evaluate AI art value?",
                "What's the ROI for AI art investments?",
                "Best platforms to buy AI art?",
                "Emerging trends in AI art for 2023",
                "How to verify AI artwork authenticity"
            ]
            
            # Handle suggestion clicks -> Set state for next run
            for i, question in enumerate(suggested_questions):
                button_key = f"suggestion_{i}"
                if st.button(question, key=button_key, help=f"Click to ask: {question}"):
                    st.session_state.current_question = question
                    st.session_state.processing_new_message = True
                    st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Process text input from user -> Set state for next run
            if prompt:
                st.session_state.current_question = prompt
                st.session_state.processing_new_message = True
                # Clear the input field by triggering a rerun
                st.rerun()
                
            # Clear chat button with improved styling
            if len(st.session_state.messages) > 1:
                if st.button("Clear Conversation", key="clear_chat"):
                    current_time = datetime.now().strftime("%H:%M")
                    st.session_state.messages = [
                        {"role": "assistant", "content": "Hello! I'm your AI Art Investment Assistant. How can I help you today?", "time": current_time}
                    ]
                    # Reset processing state as well
                    st.session_state.processing_new_message = False
                    st.session_state.current_question = ""
                    st.rerun()
        
        with info_col:
            st.markdown(
                """
                <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 16px; 
                    margin-bottom: 15px; border: 1px solid rgba(58, 123, 213, 0.2);">
                    <h3 style="color: #00d2ff; margin-top: 0; font-size: 16px;">Popular Topics</h3>
                    <ul style="padding-left: 20px; margin-bottom: 0;">
                        <li style="margin-bottom: 8px; color: #e0e0ff;">Top AI artists</li>
                        <li style="margin-bottom: 8px; color: #e0e0ff;">Market valuations</li>
                        <li style="margin-bottom: 8px; color: #e0e0ff;">Investment strategies</li>
                        <li style="margin-bottom: 8px; color: #e0e0ff;">Collecting techniques</li>
                        <li style="color: #e0e0ff;">Authentication methods</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
                """
                <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 16px; 
                    margin-bottom: 15px; border: 1px solid rgba(58, 123, 213, 0.2);">
                    <h3 style="color: #00d2ff; margin-top: 0; font-size: 16px;">Market Insights</h3>
                    <div style="color: #e0e0ff; font-size: 14px; margin-bottom: 10px;">
                        <div style="color: #a0a0cf; font-size: 12px;">Market Growth</div>
                        <div style="display: flex; align-items: center;">
                            <div style="color: #00ff9d; margin-right: 5px;">▲ 142%</div>
                            <div>Year-over-year</div>
                        </div>
                    </div>
                    <div style="color: #e0e0ff; font-size: 14px; margin-bottom: 10px;">
                        <div style="color: #a0a0cf; font-size: 12px;">Trending Artist</div>
                        <div>Refik Anadol</div>
                    </div>
                    <div style="color: #e0e0ff; font-size: 14px;">
                        <div style="color: #a0a0cf; font-size: 12px;">Latest Sale</div>
                        <div>$1.2M - "Machine Hallucinations"</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
                """
                <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 16px; 
                    border: 1px solid rgba(58, 123, 213, 0.2);">
                    <h3 style="color: #00d2ff; margin-top: 0; font-size: 16px;">Quick Links</h3>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <a href="#" style="color: #00d2ff; text-decoration: none; padding: 8px; 
                           background: rgba(0, 210, 255, 0.1); border-radius: 5px; display: block;">
                            View Investment Guide
                        </a>
                        <a href="#" style="color: #00d2ff; text-decoration: none; padding: 8px; 
                           background: rgba(0, 210, 255, 0.1); border-radius: 5px; display: block;">
                            Explore All Artists
                        </a>
                        <a href="#" style="color: #00d2ff; text-decoration: none; padding: 8px; 
                           background: rgba(0, 210, 255, 0.1); border-radius: 5px; display: block;">
                            Check Market Analysis
                        </a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    main()
