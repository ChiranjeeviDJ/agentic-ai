import Initialize_db as db
import json
from langchain_core.messages import messages_from_dict


def get_user_conversation(user_name: str):
    query = f"""
    SELECT * FROM (
        SELECT *
        FROM u816628190_booking.MovieLogs   
        WHERE user_id = '{user_name}'
        ORDER BY response_timestamp DESC LIMIT 5
    ) AS tmp
    ORDER BY response_timestamp
    """
    df = db.get_results_as_dframe(query)
    messages = []
    if len(df) > 0:
        for ind, val in df.iterrows():
            if val['history']:
                messages.extend(messages_from_dict(json.loads(val['history'])))
    return messages

def update_conversation(user_id, user_message, request_timestamp, ai_message, response_timestamp, history):
    """
    Updates conversation in database with serialized history
    
    Args:
        user_id (str): User identifier
        user_message (str): Message from user
        request_timestamp (datetime): Time of user message
        ai_message (str): Response from AI
        response_timestamp (datetime): Time of AI response
        history (list): Conversation history
    """

    
    insert_query = """
    INSERT INTO u816628190_booking.MovieLogs 
    (user_id, user_message, request_timestamp, ai_message, response_timestamp, history)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    db.update_record_in_db(
        insert_query, 
        (user_id, user_message, request_timestamp, ai_message, response_timestamp, history)
    )

if __name__ == "__main__":
    df = get_user_conversation("Yash")
    print(df)
