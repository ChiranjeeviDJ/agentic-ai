import streamlit as st
from datetime import datetime, timedelta
import time
from langgraph_code import run_agent
from utils import get_user_conversation
import utils
from langchain_core.messages import messages_to_dict

# Set page config
st.set_page_config(page_title="Movie Booking Chat", page_icon="🎬", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "login"
if "booking_data" not in st.session_state:
    st.session_state.booking_data = {}
if "selected_seats" not in st.session_state:
    st.session_state.selected_seats = []
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def reset_to_chat():
    st.session_state.page = "chat"
    st.session_state.selected_seats = []

# ==================== LOGIN PAGE ====================
def login_page():
    # Custom CSS for login page
    st.markdown("""
    <style>
    .login-container {
        max-width: 500px;
        margin: 100px auto;
        padding: 40px;
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.95), rgba(240, 240, 255, 0.95));
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    
    .login-header {
        text-align: center;
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    .login-subheader {
        text-align: center;
        color: #666;
        font-size: 18px;
        margin-bottom: 40px;
    }
    
    .welcome-icon {
        text-align: center;
        font-size: 80px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Center column for login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="welcome-icon">🎬</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-header">Movie Booking</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subheader">Welcome! Please enter your username to continue</div>', unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form"):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                help="Enter any username to get started"
            )
            
            submit = st.form_submit_button("🚀 Get Started", use_container_width=True, type="primary")
            
            if submit:
                if username and username.strip():
                    st.session_state.user_name = username.strip()
                    st.session_state.logged_in = True
                    st.session_state.page = "chat"
                    st.success(f"Welcome, {username}! 🎉")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Please enter a valid username")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 Tip: Your username will be used to save your conversation history")

# ==================== CHAT PAGE ====================
# def chat_page():
#     st.title("🎬 Movie Booking Assistant")
    
#     # Custom CSS for chat alignment
#     st.markdown("""
#     <style>
#     /* User messages (right aligned) */
#     div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
#         flex-direction: row-reverse !important;
#     }

#     div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) div[data-testid="stChatMessageContent"] {
#         background-color: transparent !important;
#         border: none !important;
#         padding: 4px 5px !important;
#         margin-left: auto !important;
#         margin-right: 10px !important;
#         max-width: 100% !important;
#     }

#     div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) p {
#         text-align: right !important;
#         color: #000 !important;
#     }

#     /* Assistant messages (left aligned) */
#     div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) div[data-testid="stChatMessageContent"] {
#         background-color: transparent !important;
#         border: none !important;
#         padding: 4x 5px !important;
#         max-width: 100% !important;
#     }

#     div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) p {
#         text-align: left !important;
#         color: #000 !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

    
#     # Display chat messages
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"], unsafe_allow_html=True)
            
#             # If message has booking button
#             if message["role"] == "assistant" and "show_button" in message and message["show_button"]:
#                 col1, col2, col3 = st.columns([1, 1, 2])
#                 with col1:
#                     if st.button("🎟️ Book Tickets", key=f"book_{message['id']}"):
#                         st.session_state.page = "booking"
#                         st.rerun()
    
#     # Chat input
#     if prompt := st.chat_input("Ask about movies or book tickets..."):
#         # Add user message
#         st.session_state.messages.append({"role": "user", "content": prompt})
        
#         with st.chat_message("user"):
#             st.markdown(prompt, unsafe_allow_html=True)
        
#         request_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         start = time.time()
#         user_message = prompt
#         user_id = st.session_state.user_name

#         # Get conversation history
#         conversation_history = get_user_conversation(user_id)

#         # Get response from agent
#         output_json, response = run_agent(conversation_history, prompt)
#         print("time taken:", time.time() - start)
#         response_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         history = messages_to_dict(output_json['messages'])

#         utils.update_conversation(user_id, user_message, request_timestamp, response, response_timestamp, history)
        
#         # Display assistant response
#         with st.chat_message("assistant"):
#             st.markdown(response)
            
#             # If movie is found, show book button
#             if output_json['booking_response']["movie"] is not None:
#                 st.session_state.booking_data = output_json['booking_response']
#                 msg_id = len(st.session_state.messages)
                
#                 col1, col2, col3 = st.columns([1, 1, 2])
#                 with col1:
#                     if st.button("🎟️ Book Tickets", key=f"book_new"):
#                         st.session_state.page = "booking"
#                         st.rerun()
                
#                 # Save message with button flag
#                 st.session_state.messages.append({
#                     "role": "assistant",
#                     "content": response,
#                     "show_button": True,
#                     "id": msg_id
#                 })
#             else:
#                 st.session_state.messages.append({
#                     "role": "assistant",
#                     "content": response,
#                     "show_button": False
#                 })
    
#     # Sidebar
#     with st.sidebar:
#         st.header("Chat Options")
#         if st.button("🗑️ Clear Chat"):
#             st.session_state.messages = []
#             st.session_state.booking_data = {}
#             st.rerun()
        
#         st.divider()
#         st.write(f"**Messages:** {len(st.session_state.messages)}")
def chat_page():
    st.title("🎬 Movie Booking Assistant")
    
    # Custom CSS for better UI
    st.markdown("""
    <style>
    /* User messages (right aligned) */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse !important;
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) div[data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        border: none !important;
        padding: 4px 5px !important;
        margin-left: auto !important;
        margin-right: 10px !important;
        max-width: 100% !important;
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) p {
        text-align: right !important;
        color: #000 !important;
    }

    /* Assistant messages (left aligned) */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) div[data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        border: none !important;
        padding: 4px 5px !important;
        max-width: 100% !important;
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) p {
        text-align: left !important;
        color: #000 !important;
    }
    
    /* Welcome card styling */
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .welcome-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .welcome-subtitle {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Quick action buttons */
    .quick-action-btn {
        background-color: #f0f2f6;
        border: 2px solid #e0e2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: left;
    }
    
    .quick-action-btn:hover {
        background-color: #667eea;
        border-color: #667eea;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Features list */
    .feature-item {
        display: flex;
        align-items: center;
        padding: 0.5rem 0;
        font-size: 0.95rem;
    }
    
    .feature-icon {
        margin-right: 0.5rem;
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

    # Show welcome message and instructions if no messages
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-title">👋 Welcome to Movie Booking Assistant!</div>
            <div class="welcome-subtitle">Your personal AI concierge for seamless movie bookings</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Start Guide
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚀 Quick Start")
            st.markdown("""
            <div class="feature-item">
                <span class="feature-icon">💬</span>
                <span>Chat naturally about movies you want to watch</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">🎯</span>
                <span>Get personalized movie recommendations</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">🎟️</span>
                <span>Book tickets in just a few clicks</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">📍</span>
                <span>Find showtimes at nearby theaters</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 💡 Example Queries")
            
            example_queries = [
                "🎬 Show me action movies playing today",
                "🌟 What are the top-rated movies this week?",
                "🎭 I want to watch a comedy with friends",
                "📅 Book tickets for Avatar this Friday"
            ]
            
            for query in example_queries:
                if st.button(query, key=query, use_container_width=True):
                    # Simulate user clicking on example
                    st.session_state.example_query = query.split(" ", 1)[1]  # Remove emoji
                    st.rerun()
        
        # How it works section
        st.markdown("### 📖 How It Works")
        steps_col1, steps_col2, steps_col3 = st.columns(3)
        
        with steps_col1:
            st.info("**Step 1: Tell Me**\n\nDescribe what movie you're interested in or ask for recommendations")
        
        with steps_col2:
            st.success("**Step 2: Choose**\n\nBrowse options and select your preferred movie and showtime")
        
        with steps_col3:
            st.warning("**Step 3: Book**\n\nClick the booking button to complete your reservation")
        
        st.divider()
        st.markdown("**✨ Tip:** Just start typing in the chat box below to begin your movie journey!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
            
            # If message has booking button
            if message["role"] == "assistant" and "show_button" in message and message["show_button"]:
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("🎟️ Book Tickets", key=f"book_{message['id']}", type="primary"):
                        st.session_state.page = "booking"
                        st.rerun()
    
    # Handle example query if set
    prompt_input = None
    if hasattr(st.session_state, 'example_query'):
        prompt_input = st.session_state.example_query
        delattr(st.session_state, 'example_query')
    
    # Chat input
    if prompt := st.chat_input("Ask about movies or book tickets...", key="chat_input"):
        prompt_input = prompt
    
    if prompt_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt_input})
        
        with st.chat_message("user"):
            st.markdown(prompt_input, unsafe_allow_html=True)
        
        request_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start = time.time()
        user_message = prompt_input
        user_id = st.session_state.user_name

        # Get conversation history
        conversation_history = get_user_conversation(user_id)

        # Get response from agent with loading indicator
        with st.spinner("🎬 Agent is Thinking ..."):
            output_json, response = run_agent(conversation_history, prompt_input)
        
        print("time taken:", time.time() - start)
        response_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        history = messages_to_dict(output_json['messages'])

        utils.update_conversation(user_id, user_message, request_timestamp, response, response_timestamp, history)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
            
            # If movie is found, show book button
            if output_json['booking_response']["movie"] is not None:
                st.session_state.booking_data = output_json['booking_response']
                msg_id = len(st.session_state.messages)
                
                st.success("✅ Movie found! Ready to book your tickets?")
                
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("🎟️ Book Tickets", key=f"book_new", type="primary"):
                        st.session_state.page = "booking"
                        st.rerun()
                
                # Save message with button flag
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "show_button": True,
                    "id": msg_id
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "show_button": False
                })
        
        st.rerun()
    
    # Enhanced Sidebar
    with st.sidebar:
        st.header("💬 Chat Options")
        
        # Stats display
        st.metric(label="Messages", value=len(st.session_state.messages))
        
        if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            st.session_state.booking_data = {}
            st.rerun()
        
        st.divider()
        
        # Help section
        with st.expander("❓ Need Help?"):
            st.markdown("""
            **Common Questions:**
            - "What movies are playing today?"
            - "Show me comedy movies"
            - "Book tickets for [Movie Name]"
            - "What's the rating of [Movie]?"
            
            **Features:**
            - Natural language understanding
            - Real-time availability
            - Instant booking
            - Personalized recommendations
            """)
        
        # User info
        if 'user_name' in st.session_state:
            st.divider()
            st.caption(f"👤 Logged in as: **{st.session_state.user_name}**")

# ==================== BOOKING PAGE ====================
def booking_page():
    st.title("🎟️ Book Your Tickets")
    
    if st.button("← Back to Chat"):
        reset_to_chat()
        st.rerun()
    
    booking = st.session_state.booking_data
    
    # Movie details
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if "image_url" in booking:
            st.image(booking["image_url"], use_container_width=True)
    
    with col2:  
        st.header(booking.get("movie", ""))
        st.write(f"🏛️ **Theatre:** {booking.get('theatre', '')}")
        st.write(f"💰 **Price per ticket:** ₹{booking.get('price', '')}")
        
        
        # Booking details
        show_date = booking.get('showtime', '')
        date_obj = datetime.strptime(show_date, "%Y-%m-%d %H:%M:%S")
        show_date = date_obj.strftime("%d %B %Y")

        st.write(f"📅 **Show Date:** {show_date}")
        
        show_time = booking.get('showtime', '')
        date_obj = datetime.strptime(show_time, "%Y-%m-%d %H:%M:%S")
        show_time = date_obj.strftime("%I:%M %p")

        st.write(f"⏰ **Show Time:** {show_time}")

        st.divider()
        

        num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=10, value=1)
    
    st.divider()
    
    # Seat selection
    st.subheader("Select Your Seats")
    
    # Create seat layout
    rows = ['A', 'B', 'C', 'D', 'E', 'F']
    seats_per_row = 10
    
    st.write("🟩 Available  🟥 Booked  🟦 Selected")
    
    # Some pre-booked seats for demo
    booked_seats = ['A5', 'A6', 'B3', 'C7', 'D5']
    
    for row in rows:
        cols = st.columns(seats_per_row)
        for i, col in enumerate(cols):
            seat_id = f"{row}{i+1}"
            with col:
                if seat_id in booked_seats:
                    st.button("🟥", key=seat_id, disabled=True, use_container_width=True)
                elif seat_id in st.session_state.selected_seats:
                    if st.button("🟦", key=seat_id, use_container_width=True):
                        st.session_state.selected_seats.remove(seat_id)
                        st.rerun()
                else:
                    if st.button("🟩", key=seat_id, use_container_width=True):
                        if len(st.session_state.selected_seats) < num_tickets:
                            st.session_state.selected_seats.append(seat_id)
                            st.rerun()
                        else:
                            st.warning(f"You can only select {num_tickets} seats")
    
    st.divider()
    
    # Show selected seats
    if st.session_state.selected_seats:
        st.write(f"**Selected Seats:** {', '.join(st.session_state.selected_seats)}")
        total_price = int(booking.get('price', 0)) * len(st.session_state.selected_seats)
        st.write(f"**Total Price:** ₹{total_price}")
        
        if len(st.session_state.selected_seats) == num_tickets:
            if st.button("✅ Proceed to Payment", use_container_width=True, type="primary"):
                st.session_state.booking_data.update({
                    "show_date": show_date,
                    "show_time": show_time,
                    "seats": st.session_state.selected_seats,
                    "total_price": total_price
                })
                st.session_state.page = "payment"
                st.rerun()
        else:
            st.info(f"Please select {num_tickets} seats to continue")
    else:
        st.info("Please select your seats from the layout above")

# ==================== PAYMENT PAGE ====================
def payment_page():
    st.title("💳 Payment & Ticket Confirmation")
    
    if st.button("← Back to Booking"):
        st.session_state.page = "booking"
        st.rerun()
    
    booking = st.session_state.booking_data
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎫 Ticket Summary")
        
        # Display movie poster if available
        if "image_url" in booking:
            st.image(booking["image_url"], width=300)
        
        st.write("---")
        st.write(f"**Movie:** {booking.get('movie', '')}")
        st.write(f"**Theatre:** {booking.get('theatre', '')}")
        st.write(f"**Date:** {booking.get('show_date', '')}")
        st.write(f"**Time:** {booking.get('show_time', '')}")
        st.write(f"**Seats:** {', '.join(booking.get('seats', []))}")
        st.write(f"**Number of Tickets:** {len(booking.get('seats', []))}")
        st.write("---")
        st.write(f"### Total Amount: ₹{booking.get('total_price', 0)}")
    
    with col2:
        st.subheader("💳 Payment Details")
        
        payment_method = st.radio("Select Payment Method", 
                                  ["Credit/Debit Card", "UPI", "Net Banking", "Wallet"])
        
        if payment_method == "Credit/Debit Card":
            card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456")
            col_a, col_b = st.columns(2)
            with col_a:
                expiry = st.text_input("Expiry (MM/YY)", placeholder="12/25")
            with col_b:
                cvv = st.text_input("CVV", type="password", placeholder="123")
            
        elif payment_method == "UPI":
            upi_id = st.text_input("UPI ID", placeholder="username@upi")
            
        elif payment_method == "Net Banking":
            bank = st.selectbox("Select Bank", 
                               ["SBI", "HDFC", "ICICI", "Axis", "Other"])
            
        else:  # Wallet
            wallet = st.selectbox("Select Wallet", 
                                 ["Paytm", "PhonePe", "Google Pay", "Amazon Pay"])
        
        st.divider()
        
        agree = st.checkbox("I agree to the terms and conditions")
        
        if st.button("🎉 Confirm & Pay", use_container_width=True, type="primary", disabled=not agree):
            with st.spinner("Processing payment..."):
                time.sleep(2)
            
            # Generate booking ID and save to session
            st.session_state.booking_data['booking_id'] = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
            st.session_state.page = "ticket"
            st.rerun()

# ==================== TICKET CONFIRMATION PAGE ====================
def ticket_page():
    # Custom CSS for ultra-stylish background and ticket design
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            font-family: 'Montserrat', sans-serif;
            overflow-x: hidden;
        }
        
        /* Animated background particles */
        .stApp::before {
            content: '';
            position: fixed;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(255, 215, 0, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(138, 43, 226, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(255, 105, 180, 0.1) 0%, transparent 50%);
            animation: float 15s ease-in-out infinite;
            z-index: 0;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) scale(1); }
            50% { transform: translateY(-20px) scale(1.05); }
        }
        
        .ticket-wrapper {
            position: relative;
            z-index: 1;
            padding: 40px 20px;
        }
        
        .ticket-container {
            background: linear-gradient(145deg, rgba(30, 30, 46, 0.95), rgba(20, 20, 35, 0.98));
            border-radius: 30px;
            padding: 50px 40px;
            box-shadow: 
                0 30px 90px rgba(0, 0, 0, 0.6),
                0 0 0 1px rgba(255, 215, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            margin: 20px auto;
            max-width: 900px;
            position: relative;
            backdrop-filter: blur(20px);
            border: 2px solid transparent;
            background-clip: padding-box;
            animation: slideUp 0.8s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Glowing border effect */
        .ticket-container::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #ffd700, #ff6b6b, #4ecdc4, #ffd700);
            border-radius: 30px;
            z-index: -1;
            animation: borderGlow 3s linear infinite;
            background-size: 300% 300%;
        }
        
        @keyframes borderGlow {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .ticket-header {
            text-align: center;
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 50%, #ffd700 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 56px;
            font-weight: 800;
            margin-bottom: 20px;
            text-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
            animation: shimmer 3s ease-in-out infinite;
            letter-spacing: 3px;
        }
        
        @keyframes shimmer {
            0%, 100% { filter: brightness(1); }
            50% { filter: brightness(1.3); }
        }
        
        .success-icon {
            text-align: center;
            font-size: 100px;
            margin: 20px 0;
            animation: popIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            filter: drop-shadow(0 0 20px rgba(76, 175, 80, 0.8));
        }
        
        @keyframes popIn {
            0% { transform: scale(0); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .booking-id-container {
            text-align: center;
            margin: 35px 0;
            animation: fadeInUp 1s ease-out 0.3s both;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .booking-id {
            display: inline-block;
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            color: #1a1a2e;
            padding: 18px 40px;
            border-radius: 50px;
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 4px;
            box-shadow: 
                0 10px 30px rgba(255, 215, 0, 0.4),
                inset 0 -2px 10px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .booking-id::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                45deg,
                transparent,
                rgba(255, 255, 255, 0.3),
                transparent
            );
            animation: shine 3s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        .ticket-content {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 40px;
            margin: 40px 0;
            animation: fadeInUp 1s ease-out 0.5s both;
        }
        
        .poster-container {
            position: relative;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            border: 3px solid rgba(255, 215, 0, 0.3);
        }
        
        .poster-container::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                135deg,
                rgba(255, 215, 0, 0.1) 0%,
                transparent 50%
            );
            pointer-events: none;
        }
        
        .ticket-info {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
            padding: 30px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 215, 0, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .ticket-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 0;
            border-bottom: 1px dashed rgba(255, 215, 0, 0.2);
            transition: all 0.3s ease;
        }
        
        .ticket-row:hover {
            padding-left: 10px;
            border-bottom-color: rgba(255, 215, 0, 0.5);
        }
        
        .ticket-row:last-child {
            border-bottom: none;
            margin-top: 20px;
            padding-top: 25px;
            border-top: 2px solid rgba(255, 215, 0, 0.3);
        }
        
        .ticket-label {
            font-weight: 600;
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 18px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .ticket-value {
            color: #ffffff;
            font-size: 18px;
            font-weight: 600;
            text-align: right;
        }
        
        .divider {
            height: 3px;
            background: linear-gradient(to right, transparent, #ffd700 20%, #ff6b6b 50%, #4ecdc4 80%, transparent);
            margin: 40px 0;
            border-radius: 10px;
            animation: pulse 2s ease-in-out infinite;
        }
        
        .additional-info {
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
            margin: 30px 0;
            font-size: 16px;
            line-height: 1.8;
            animation: fadeInUp 1s ease-out 0.7s both;
        }
        
        .enjoy-message {
            text-align: center;
            background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 50%, #4ecdc4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 52px;
            font-weight: 800;
            margin: 50px 0 30px 0;
            animation: rainbow 3s ease-in-out infinite, bounce 2s ease-in-out infinite;
            text-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
            letter-spacing: 2px;
        }
        
        @keyframes rainbow {
            0%, 100% { filter: hue-rotate(0deg) brightness(1.2); }
            50% { filter: hue-rotate(20deg) brightness(1.5); }
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-10px) scale(1.05); }
        }
        
        .icon-float {
            display: inline-block;
            animation: floatIcon 3s ease-in-out infinite;
        }
        
        @keyframes floatIcon {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }
        </style>
    """, unsafe_allow_html=True)
    
    booking = st.session_state.booking_data
    
    # Success animation
    st.balloons()
    
    # Ticket wrapper
    st.markdown('<div class="ticket-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="ticket-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="ticket-header">BOOKING CONFIRMED</div>', unsafe_allow_html=True)
    
    # Success icon
    st.markdown('<div class="success-icon">✨🎉✨</div>', unsafe_allow_html=True)
    
    # Booking ID
    st.markdown(f'''
        <div class="booking-id-container">
            <div style="color: rgba(255,255,255,0.6); font-size: 14px; margin-bottom: 10px; letter-spacing: 2px;">BOOKING ID</div>
            <div class="booking-id">{booking.get("booking_id", "")}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Divider
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Ticket Content Grid
    st.markdown('<div class="ticket-content">', unsafe_allow_html=True)
    
    # Using columns for layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if "image_url" in booking:
            st.markdown('<div class="poster-container">', unsafe_allow_html=True)
            st.image(booking["image_url"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="ticket-info">', unsafe_allow_html=True)
        
        ticket_html = f"""
        <div class="ticket-row">
            <span class="ticket-label"><span class="icon-float">🎬</span> Movie</span>
            <span class="ticket-value">{booking.get('movie', '')}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label"><span class="icon-float">🏛️</span> Theatre</span>
            <span class="ticket-value">{booking.get('theatre', '')}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label"><span class="icon-float">📅</span> Date</span>
            <span class="ticket-value">{booking.get('show_date', '')}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label"><span class="icon-float">🕐</span> Show Time</span>
            <span class="ticket-value">{booking.get('show_time', '')}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label"><span class="icon-float">💺</span> Seats</span>
            <span class="ticket-value">{', '.join(booking.get('seats', []))}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label"><span class="icon-float">🎟️</span> Number of Tickets</span>
            <span class="ticket-value">{len(booking.get('seats', []))}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label" style="font-size: 22px;"><span class="icon-float">💰</span> Total Amount</span>
            <span class="ticket-value" style="font-size: 26px; font-weight: 800;">₹{booking.get('total_price', 0)}</span>
        </div>
        """
        st.markdown(ticket_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close ticket-content
    
    # Divider
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Additional info
    st.markdown("""
        <div class="additional-info">
            <div style="margin: 10px 0;">📧 A confirmation email has been sent to your registered email address</div>
            <div style="margin: 10px 0;">📱 Please show this booking ID at the theatre counter</div>
            <div style="margin: 10px 0;">🎫 Arrive 15 minutes before showtime for entry</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Final message with icons
    st.markdown('<div class="enjoy-message">🍿 ENJOY THE SHOW 🎬</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close ticket-container
    st.markdown('</div>', unsafe_allow_html=True)  # Close ticket-wrapper
    
    # Back to home button
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True, type="primary"):
            st.session_state.messages = []
            st.session_state.selected_seats = []
            st.session_state.booking_data = {}
            reset_to_chat()
            st.rerun()


# ==================== MAIN APP ====================
def main():
    if st.session_state.page == "chat":
        chat_page()
    elif st.session_state.page == "booking":
        booking_page()
    elif st.session_state.page == "payment":
        payment_page()
    elif st.session_state.page == "ticket":
        ticket_page()
    elif st.session_state.page == "login":
        login_page()

if __name__ == "__main__":
    main()