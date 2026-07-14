from dotenv import load_dotenv
import sqlite3
import json
from datetime import datetime
from typing import TypedDict, Annotated, Sequence, Literal
from rapidfuzz import process
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import messages_to_dict
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import operator
import Initialize_db as db
import time

load_dotenv()

# Database configuration
DB_PATH = "movie_booking_details.db"

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)

# ============================================================================
# State Definition
# ============================================================================

class AgentState(TypedDict):
    """State for the movie booking agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    booking_response: dict
    requires_tools: bool
    tool_outputs: dict
    current_step: int


# ============================================================================
# Database Functions
# ============================================================================

# def execute_query(sql: str) -> list:
#     """Execute SQL query and return results."""
#     try:
#         print(sql)
#         conn = sqlite3.connect(DB_PATH)
#         cur = conn.cursor()
#         cur.execute(sql)
#         results = [i for i in cur.fetchall()]
#         if len(results) == 1 and len(results[0]) == 1:
#             results = results[0][0]
#         conn.close()
#         return results
#     except Exception as e:
#         print(f"[SQL Error] {e}")
#         return []

def fuzzy_search(user_input: str, data_list: dict) -> str:
    """Perform fuzzy matching on input."""
    match, score, _ = process.extractOne(user_input.lower(), data_list.keys())
    if score > 80:
        return data_list[match]
    else:
        print(f"{user_input} matched {match} with score {score}")
        return None

# ============================================================================
# Tool Definitions
# ============================================================================

# @tool
# def movie_entity_correction(movie_name: str) -> str:
#     """Corrects fuzzy or misspelled movie names.
    
#     Args:
#         movie_name: The movie name to correct
    
#     Returns:
#         Corrected movie name or None if not found
#     """
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
#     cur.execute("SELECT DISTINCT name FROM movies")
#     results = {i[0].lower(): i[0] for i in cur.fetchall()}
#     conn.close()
#     result = fuzzy_search(movie_name, results)
#     return result if result else f"Movie '{movie_name}' not found"

@tool
def movie_entity_correction(movie_name: str) -> str:
    """Corrects fuzzy or misspelled movie names.
    
    Args:
        movie_name: The movie name to correct
    Returns:
        Corrected movie name or None if not found
    """
    results = db.get_results_as_dframe("SELECT DISTINCT name FROM movies")
    results = {i.lower(): i for i in results['name']}
    print(results)
    result = fuzzy_search(movie_name, results)
    return result if result else f"Movie '{movie_name}' not found"

# @tool
# def theatre_entity_correction(theatre_name: str) -> str:
#     """Corrects fuzzy or misspelled theatre names.
    
#     Args:
#         theatre_name: The theatre name to correct
    
#     Returns:
#         Corrected theatre name or None if not found
#     """
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
#     cur.execute("SELECT DISTINCT name FROM theatres")
#     results = {i[0].lower(): i[0] for i in cur.fetchall()}
#     conn.close()
#     result = fuzzy_search(theatre_name, results)
#     return result if result else f"Theatre '{theatre_name}' not found"
@tool
def theatre_entity_correction(theatre_name: str) -> str:
    """Corrects fuzzy or misspelled theatre names.
    
    Args:
        theatre_name: The theatre name to correct           
    Returns:
        Corrected theatre name or None if not found
    """
    results = db.get_results_as_dframe("SELECT DISTINCT name FROM theatres")
    results = {i.lower(): i for i in results['name']}
    result = fuzzy_search(theatre_name, results)
    return result if result else f"Theatre '{theatre_name}' not found"

@tool
def query_database(query: str) -> str:
    """Executes a SQL query and returns results.
    
    Args:
        query: SQL query to execute
    
    Returns:
        Query results as string
    """
    result = db.get_results_as_dframe(query)
    return str(result) if not result.empty else "No results found"


def verify_show(movie: str, theatre: str, showtime: str) -> str:
    """Verifies if a show exists at the specified time.
    
    Args:
        movie: Movie name
        theatre: Theatre name
        showtime: Showtime in format 'YYYY-MM-DD HH:MM:SS'
    
    Returns:
        Verification status
    """
    sql = f"""SELECT showtime FROM showtimes 
            WHERE movie_id = (SELECT id FROM movies WHERE name = '{movie}')
            AND theatre_id = (SELECT id FROM theatres WHERE name = '{theatre}')
            AND showtime = '{showtime}'"""
    results = db.get_results_as_dframe(sql)
    return "verified_exist" if len(results) == 1 else "not_exists"


@tool
def book_ticket(movie: str, theatre: str, showtime: str) -> str:
    """Books a ticket for the specified show.
    
    Args:
        movie: Movie name
        theatre: Theatre name
        showtime: Showtime in format 'YYYY-MM-DD HH:MM:SS'
    
    Returns:
        Booking confirmation or error message
    """
    verification = verify_show( movie,  theatre, showtime)


    if verification == "verified_exist":
        price = db.get_results_as_dframe(f"""SELECT showtime,price FROM showtimes 
            WHERE movie_id = (SELECT id FROM movies WHERE name = '{movie}')
            AND theatre_id = (SELECT id FROM theatres WHERE name = '{theatre}')
            AND showtime = '{showtime}'""")['price'][0]
    
        # Extract image URL from movie_data (handles both old and new format)
        image_url = ""
        if movie in db.movie_data:
            movie_info = db.movie_data[movie]
            if isinstance(movie_info, dict):
                image_url = movie_info.get('image_url', '')
            else:
                image_url = movie_info
    
        return json.dumps({
            "status": "success",
            "movie": movie,
            "theatre": theatre,
            "showtime": showtime,
            "price":price,
            "image_url": image_url,
            "message": f"Book the ticket and enjoy the show!\n\nMovie: {movie}\nTheatre: {theatre}\nTime: {showtime}"
        })
    else:
        return json.dumps({
            "status": "failed",
            "message": "Show details do not exist"
        })

# Collect all tools
tools = [
    movie_entity_correction,
    theatre_entity_correction,
    query_database,
    book_ticket
]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

# ============================================================================
# Graph Nodes
# ============================================================================

def analyze_query(state: AgentState) -> AgentState:
    """Analyze user query and decide if tools are needed."""
    start = time.time()
    system_prompt = f"""You are a helpful movie booking assistant with access to tools.

Current date: {datetime.now()}

Database schema(SQL):
- movies(id: int, name: str, genre: str)
- theatres(id: int, name: str)
- showtimes(id: int, movie_id: int, theatre_id: int, showtime: timestamp, price: float)

You have access to these tools:
- movie_entity_correction: Correct movie names
- theatre_entity_correction: Correct theatre names
- query_database: Execute SQL queries
- book_ticket: Helping user to provide a movie details for booking

For queries that need information from the database, use the appropriate tools.
For casual conversation or when you can answer directly, respond naturally without tools.

Important instructions:
- Use **descriptive variable names** for values returned by previous steps (e.g., `corrected_theatre_name`, `corrected_movie_name`).
- **Do not hardcode** resolved values into later steps — always use the variable name (e.g., use `corrected_theatre_name`).
- While fetching the show times please also show the theatre names
- correct the entities names like theatre, movie before quering in sql db
- always keep in mind about the current date while showing movie details because no one wants to book ticket before current time

Examples of when to use tools:
- "Show me theatres playing Avatar" → Use movie_entity_correction, then query_database
- "Book Avatar at PVR at 7 PM" → Use movie_entity_correction, theatre_entity_correction, then for help book_ticket
- "What movies are available?" → Use query_database

Examples of when NOT to use tools:
- "Hello" → Respond directly
- "Thank you" → Respond directly
"""
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)

    end = time.time()
    print(response.content,'\n', "Time Taken - ", end-start)
    
    return {
        "messages": [response],
        "requires_tools": bool(response.tool_calls)
    }

def execute_tools(state: AgentState) -> AgentState:
    """Execute tool calls from the LLM."""
    tool_node = ToolNode(tools)
    result = tool_node.invoke(state)
    return result

def generate_response(state: AgentState) -> AgentState:
    """Generate final natural language response."""
    
    last_message = state["messages"][-1]
    
    # Check if this is a tool result
    if hasattr(last_message, 'tool_calls'):
        # Get tool results
#         system_prompt = f"""You are a friendly movie booking assistant. 
        
# Based on the tool results, provide a natural, helpful response to the user.
# If a booking was successful, congratulate them and provide the details.
# If information was found, present it clearly.
# If nothing was found, politely inform the user and offer to help in another way.

# Current date: {datetime.now()}
# """
#         messages = [SystemMessage(content=system_prompt)] + state["messages"]
#         response = llm.invoke(messages)
        
        # Check for booking success
        booking_response = {"movie": None}
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'content') and 'status' in str(msg.content):
                try:
                    booking_data = json.loads(msg.content)
                    if booking_data.get("status") == "success":
                        booking_response = {
                            "movie": booking_data.get("movie"),
                            "theatre": booking_data.get("theatre"),
                            "showtime": booking_data.get("showtime"),
                            "price": booking_data.get("price"),
                            "image_url": booking_data.get("image_url")
                        }
                        break
                except:
                    pass
                    
        return { 
            "booking_response": booking_response
        }
    
    return {"booking_response": {"movie": None}}

def should_continue(state: AgentState) -> Literal["tools", "respond"]:
    """Decide whether to use tools or respond directly."""
    last_message = state["messages"][-1]
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return "respond"

# ============================================================================
# Build Graph
# ============================================================================

def create_movie_booking_graph():
    """Create and compile the LangGraph workflow."""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_query)
    workflow.add_node("tools", execute_tools)
    workflow.add_node("respond", generate_response)
    
    # Set entry point
    workflow.set_entry_point("analyze")
    
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "analyze",
        should_continue,
        {
            "tools": "tools",
            "respond": "respond"
        }
    )
    
    # Tools go back to analyze for potential follow-up
    workflow.add_edge("tools", "analyze")
    
    # End after responding
    workflow.add_edge("respond", END)
    
    return workflow.compile()

# ============================================================================
# Main Execution
# ============================================================================

app = create_movie_booking_graph()

def check_book_ticket_success(messages):
    """Check if booking was successful in the messages."""
    messages_dict = messages_to_dict(messages)

    for i in messages_dict:
        if i['type']=='tool':
            if i['data']['name']=="book_ticket":
                return False
    return True

def run_agent(conversation_history, user_input):
    """Run the movie booking agent."""
    
    if conversation_history is None:
        conversation_history = []

    history_length = len(conversation_history)
    
    conversation_history.append(HumanMessage(content=user_input))
        
        # Run the graph
    initial_state = {
        "messages": conversation_history.copy(),
        "booking_response": {"movie": None},
        "requires_tools": False,
        "tool_outputs": {},
        "current_step": 0
    }
    
    result = app.invoke(initial_state)
    result['messages'] = result['messages'][history_length:]
    
    if check_book_ticket_success(result['messages']):
        result["booking_response"]["movie"] = None
    

    # Get final response
    final_message = result["messages"][-1]
    assistant_response = final_message.content
    
    conversation_history.append(AIMessage(content=assistant_response))
    
    print(f"\n🤖 Bot: {assistant_response}\n")
    
    # Show booking confirmation if successful
    if result["booking_response"]["movie"] is not None:
        print("✅ Booking confirmed!")
        print(f"   Movie: {result['booking_response']['movie']}")
        print(f"   Theatre: {result['booking_response']['theatre']}")
        print(f"   Time: {result['booking_response']['showtime']}")
        print(f"   Price: {result['booking_response']['price']}")
        print(f"   Image URL: {result['booking_response']['image_url']}\n")
    return result, assistant_response

if __name__ == "__main__":
    user_input = input("User: ")
    result = run_agent(conversation_history=None, user_input=user_input)