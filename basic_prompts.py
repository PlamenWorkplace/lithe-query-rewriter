from queries import queries
from prompts import get_prompt_1, get_prompt_2, get_prompt_3
from lithe import get_optimizer_cost, rewrite_query, calculate_lithe_metrics, llm_model

if __name__ == "__main__":
    data_p1 = []
    data_p2 = []
    data_p3 = []
    data_p4 = []

    for info in queries:
        try:
            query_id = info.get("id")
            query_orig = info.get("query")

            print(f"\nEvaluating Query ID: {query_id}")
            cost_orig = get_optimizer_cost(query_orig)
            print(f"Original Cost: {cost_orig}")

            print(f"\n--- Testing Basic Prompt 1 on {llm_model} ---")
            system_1, user_1 = get_prompt_1(query_orig)
            query_rewr_1, cost_rewr_1 = rewrite_query(system_1, user_1)
            print(f"Rewritten Cost (Prompt 1): {cost_rewr_1}")

            print(f"\n--- Testing Basic Prompt 2 on {llm_model} ---")
            system_2, user_2 = get_prompt_2(query_orig)
            query_rewr_2, cost_rewr_2 = rewrite_query(system_2, user_2)
            print(f"Rewritten Cost (Prompt 2): {cost_rewr_2}")

            print(f"\n--- Testing Basic Prompt 3 on {llm_model} ---")
            system_3, user_3 = get_prompt_3(query_orig)
            query_rewr_3, cost_rewr_3 = rewrite_query(system_3, user_3)
            print(f"Rewritten Cost (Prompt 3): {cost_rewr_3}")

            print(f"\n--- Testing Basic Prompt 4 on {llm_model} ---")
            query_rewr_4, cost_rewr_4 = rewrite_query(system_3, user_3, prompts_id=4)
            print(f"Rewritten Cost (Prompt 4): {cost_rewr_4}")

            data_p1.append({"query_id": query_id, "original_cost": cost_orig, "rewritten_cost": cost_rewr_1})
            data_p2.append({"query_id": query_id, "original_cost": cost_orig, "rewritten_cost": cost_rewr_2})
            data_p3.append({"query_id": query_id, "original_cost": cost_orig, "rewritten_cost": cost_rewr_3})
            data_p4.append({"query_id": query_id, "original_cost": cost_orig, "rewritten_cost": cost_rewr_4})

        except RuntimeError as e:
            print(e)
            continue


    print("\n" + "="*40)
    print("FINAL LITHE STATISTICS")
    print("="*40)

    datasets = [
        ("Prompt 1", data_p1), 
        ("Prompt 2", data_p2), 
        ("Prompt 3", data_p3), 
        ("Prompt 4", data_p4)
    ]
    
    for name, dataset in datasets:
        cpr, csgm = calculate_lithe_metrics(dataset)
        print(f"\n--- {name} Results ---")
        print(f"Total Queries Evaluated: {len(dataset)}")
        print(f"Cost Productive Rewrites (CPR): {cpr}")
        print(f"Cost Speedup Geometric Mean (CSGM): {csgm:.2f}")