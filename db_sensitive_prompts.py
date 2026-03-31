from queries import queries
from prompts import RULES, RULE_EXAMPLES, get_redundancy_prompt, get_statistics_prompt
from lithe import engine, get_optimizer_cost
from sqlalchemy import text
from queries import queries
from prompts import (get_redundancy_prompt, get_statistics_prompt, RULES, RULE_EXAMPLES)
from lithe import (get_optimizer_cost, calculate_lithe_metrics, engine, evaluate_single_prompt, llm_model)
from sqlalchemy import text


def get_table_statistics() -> str:
    table_names = ['students', 'professors', 'courses', 'grades']
    stats_strings = []
    
    with engine.connect() as connection:
        for table in table_names:
            query = text("SELECT reltuples FROM pg_class WHERE relname = :tbl")
            result = connection.execute(query, {"tbl": table}).scalar()
            
            if result is not None:
                stats_strings.append(f"Table '{table}' has approximately {int(result)} rows.")
                
    return "\n".join(stats_strings)


if __name__ == "__main__":
    query_stats = get_table_statistics()

    rule_data = {rule_id: [] for rule_id in RULES.keys()}

    for query in queries:
        try:
            query_id = query["id"]
            query_str = query["query"]
            
            print(f"\nEvaluating Query ID: {query_id}")
            original_cost = get_optimizer_cost(query_str)
            print(f"Original Cost: {original_cost}")
                    
            for rule_id, rule_text in RULES.items():
                examples = RULE_EXAMPLES[rule_id]

                print(f"\n--- Testing Rule {rule_id} on {llm_model} ---")
                
                if rule_id in ["R1", "R2", "R3", "R4"]:
                    sys_r, usr_r = get_redundancy_prompt(
                        db_engine="PostgreSQL",
                        rule_text=rule_text,
                        example_orig=examples["orig"],
                        example_rewr=examples["rewr"],
                        query=query_str,
                        example_2_orig=examples.get("orig2"),
                        example_2_rewr=examples.get("rewr2")
                    )
                else:
                    sys_r, usr_r = get_statistics_prompt(
                        db_engine="PostgreSQL",
                        rule_text=rule_text,
                        example_orig=examples["orig"],
                        example_stats=examples.get("stats"),
                        example_rewr=examples["rewr"],
                        query=query_str,
                        query_stats=query_stats,
                        example_2_orig=examples.get("orig2"),
                        example_2_stats=examples.get("stats2"),
                        example_2_rewr=examples.get("rewr2")
                    )
                    
                cost_rewr = evaluate_single_prompt([{"role": "system", "content": sys_r}, {"role": "user", "content": usr_r}])
                print(f"Rewritten Cost ({rule_id}): {cost_rewr}")
                
                rule_data[rule_id].append({
                    "query_id": query_id, 
                    "original_cost": original_cost, 
                    "rewritten_cost": cost_rewr
                })
                
        except RuntimeError as e:
            print(f"Error evaluating query {query.get('id', 'Unknown')}: {e}")
            continue
        
    print("\n" + "="*40)
    print("FINAL SENSITIVE PROMPT STATISTICS (R1-R6)")
    print("="*40)

    for rule_id, dataset in rule_data.items():
        if not dataset:
            print(f"\n--- {rule_id} Results ---")
            print("No valid queries evaluated.")
            continue
            
        cpr, csgm = calculate_lithe_metrics(dataset)
        print(f"\n--- {rule_id} Results ---")
        print(f"Total Queries Evaluated: {len(dataset)}")
        print(f"Cost Productive Rewrites (CPR): {cpr}")
        print(f"Cost Speedup Geometric Mean (CSGM): {csgm:.2f}")