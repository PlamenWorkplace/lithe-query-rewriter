import os
from dotenv import load_dotenv
from litellm import completion
import math
import json
from sqlalchemy import text, create_engine
from sqlalchemy.exc import DatabaseError
import time

load_dotenv()

llm_model = os.getenv("LLM_MODEL")
DATABASE_URI = os.getenv("DATABASE_URI")
engine = create_engine(DATABASE_URI)


def extract_sql_with_llm(raw_text: str) -> str:
    messages = [
        {
            "role": "system", 
            "content": (
                "You are an automated SQL extraction tool. Your job is to extract the optimized "
                "SQL query from the provided text. "
                "CRITICAL INSTRUCTIONS: "
                "1. Return ONLY ONE raw SQL SELECT statement (including any WITH/CTE clauses). "
                "2. If the input text contains multiple omptimized queries, choose and return ONLY the most optimized one that doesn't have CREATE INDEX, ALTER, or other DDL/DML statements."
                "3. Do NOT include any CREATE INDEX, ALTER, or other DDL/DML statements. "
                "4. Do NOT include markdown formatting (like ```sql or ```). "
                "5. Do NOT include any explanations, prefixes, or suffixes."
            )
        },
        {"role": "user", "content": raw_text}
    ]
    
    extracted_sql = prompt_llm(messages)
    
    if extracted_sql:
        return extracted_sql.strip().strip("`").strip()
    return ""


def prompt_llm(messages: list, max_retries: int = 5) -> str:
    retries = 0

    while retries < max_retries:        
        try:
            response = completion(
                model=llm_model, 
                temperature=0,
                messages=messages
            )
            
            raw_output = response.choices[0].message.content
            return raw_output
            
        except Exception as e:
            print(f"Error communicating with {llm_model}: {e}")
            retries += 1
            time.sleep(5)
            
    raise RuntimeError(f"Failed to get response from {llm_model} after {max_retries} attempts.")


def calculate_lithe_metrics(query_results):
    cpr_count = 0
    cpr_speedups = []
    
    for result in query_results:
        original_cost = result.get('original_cost')
        rewritten_cost = result.get('rewritten_cost')
        
        if rewritten_cost <= 0:
            continue
            
        speedup = original_cost / rewritten_cost
        
        # A Cost Productive Rewrite (CPR) requires an estimated speedup >= 1.5x
        if speedup >= 1.5:
            cpr_count += 1
            cpr_speedups.append(speedup)
            
    csgm = 0.0
    if cpr_count > 0:
        # CSGM is calculated using the exponential of the mean of logarithms
        log_sum = sum(math.log(s) for s in cpr_speedups)
        csgm = math.exp(log_sum / cpr_count)
        
    return cpr_count, csgm


def get_optimizer_cost(query: str, execute: bool = False) -> float:
    command = "EXPLAIN (ANALYZE, FORMAT JSON)" if execute else "EXPLAIN (FORMAT JSON)"
    explain_sql = text(f"{command} {query}")

    with engine.connect() as connection:
        result = connection.execute(explain_sql).scalar()
        plan_data = json.loads(result) if isinstance(result, str) else result

        if execute:
            return plan_data[0]["Plan"]["Actual Total Time"]
        else:
            return plan_data[0]["Plan"]["Total Cost"]


def rewrite_query_prompt_4(system_prompt: str, user_prompt: str):
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    part1, sep2, rest = user_prompt.partition("2. ")
    part2, sep3, part3 = rest.partition("3. ")

    step_1_prompt = part1.strip()
    step_2_prompt = (sep2 + part2).strip()
    step_3_prompt = (sep3 + part3).strip()

    for prompt in [step_1_prompt, step_2_prompt, step_3_prompt]:
        messages.append({"role": "user", "content": prompt})
        llm_response = prompt_llm(messages)
        messages.append({"role": "assistant", "content": llm_response})
    
    return llm_response, messages
    

def rewrite_query(system_prompt: str, user_prompt: str, prompts_id: int = -1, max_retries: int = 5):
    if prompts_id == 4:
        llm_response, messages = rewrite_query_prompt_4(system_prompt, user_prompt)
    else:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        llm_response = prompt_llm(messages)

    print("\n" + "="*50)
    print("🤖 LLM RAW RESPONSE:")
    print("="*50)
    print(llm_response)
    print("="*50)

    print("\n[MANUAL INPUT REQUIRED]")
    print("Please copy and paste the extracted SQL query from the response above.")
    print("When you are finished, type 'END' on a new line and press Enter:\n")
    
    user_lines = []
    while True:
        try:
            line = input()
            # Stop recording if you type 'END' (case-insensitive)
            if line.strip().upper() == 'END':
                break
            if line.strip().upper() == 'SKIP':
                raise RuntimeError(f"Skipping this query as per user request.")
            user_lines.append(line)
        except EOFError:
            break

    query_rewr = "\n".join(user_lines).strip()

    # Alternatively automate the SQL extraction using the LLM itself if the sql is expected in the [REWRITTEN] section of the prompt
    # query_rewr = extract_sql_with_llm(llm_response)    
    # print(f"\n\n{query_rewr}\n\n")
    
    if not query_rewr:
        return None, 0.0
    
    for attempt in range(max_retries):
        try:
            cost = get_optimizer_cost(query_rewr)
            
            print(f"  [Success] Valid SQL obtained on attempt {attempt + 1}.")
            
            return query_rewr, cost
            
        except DatabaseError as e:
            raw_db_error = str(e.orig).strip()
            
            print(f"  [Attempt {attempt + 1} Failed] Database Error: {raw_db_error}")
            
            messages.append({"role": "assistant", "content": llm_response})
            messages.append({
                "role": "user", 
                "content": f"The query you provided resulted in a database syntax error:\n{raw_db_error}\n\nPlease analyze this error and provide a corrected SQL query. Output only the SQL."
            })

            llm_response = prompt_llm(messages)
            
            print(llm_response)
            query_rewr = extract_sql_with_llm(llm_response)
            print(f"\n\n{query_rewr}\n\n")
            
        except Exception as e:
            print(f"  [Attempt {attempt + 1} Failed] Unexpected System Error: {e}")
            break
            
    print("Maximum retries reached. Could not produce a valid SQL rewrite.")
    return None, 0.0