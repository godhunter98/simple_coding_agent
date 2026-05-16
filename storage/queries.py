import pathlib
import sqlite3

conn = sqlite3.connect(pathlib.Path(__file__).parent/"agent_persistence.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


def log_conversation(summary:str,model:str,total_tokens:int,cost_per_token:dict = None) -> int | None:
    """
    Create a new conversation and return its ID
    """
    if cost_per_token is None:
        cost_per_token = {"deepseek-v4-flash": 0.25, "deepseek-v4-pro": 0.70}
    approx_cost = cost_per_token.get(model,0.0)*total_tokens
    
    cursor.execute(
        '''
        INSERT INTO conversations 
        (summary,model,total_tokens,approx_cost)
        VALUES (?, ?, ?, ?)
        ''',
        (summary,model,total_tokens,approx_cost),
    )
    conn.commit()
    return cursor.lastrowid 

def add_message(conversation_id:int, role:str, content:str) -> int | None:
    """
    Add message to a converation
    """
    cursor.execute(
        '''
        INSERT INTO messages 
        (conversation_id, role, content)
        VALUES (?, ?, ?)
        ''',
        (conversation_id,role,content),
    )
    conn.commit()
    return cursor.lastrowid

def add_tool_call(message_id: int, tool_name: str, tool_args: str, tool_output: str) -> int | None:
    """Log a tool invocation."""
    cursor.execute(
        """
        INSERT INTO tool_calls (message_id, tool_name, tool_args, tool_output)
        VALUES (?, ?, ?, ?)
        """,
        (message_id, tool_name, tool_args, tool_output),
    )
    conn.commit()
    return cursor.lastrowid

def mark_conversation_completed(conversation_id: int, final_summary: str = None):
    """Mark a conversation as completed."""
    cursor.execute(
        """
        UPDATE conversations 
        SET status = 'completed', ended_at = CURRENT_TIMESTAMP, summary = COALESCE(?, summary)
        WHERE conversation_id = ?
        """,
        (final_summary, conversation_id),
    )
    conn.commit()

def get_all_conversations():
    """Retrieve all conversations."""
    cursor.execute(
        '''
        SELECT * FROM conversations ORDER BY started_at DESC
        '''
    )
    return cursor.fetchall()

def get_conversation_messages(conversation_id: int):
    """Retrieve all messages in a conversations."""
    cursor.execute(
        '''
        SELECT * FROM messages WHERE conversation_id = ?
        ''',
        (conversation_id,),        
    )
    return cursor.fetchall()