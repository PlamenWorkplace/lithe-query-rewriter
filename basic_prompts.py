from queries import queries
from prompts import get_prompt_1, get_prompt_2, get_prompt_3
from lithe import get_optimizer_cost, calculate_lithe_metrics, llm_model, evaluate_single_prompt, evaluate_prompt_4


if __name__ == "__main__":
    data_p1 = []
    data_p2 = []
    data_p3 = []
    data_p4 = []

    for query in queries:
        try:
            query_id = query.get("id")
            query_orig = query.get("query")

            print(f"\nEvaluating Query ID: {query_id}")
            cost_orig = get_optimizer_cost(query_orig)
            print(f"Original Cost: {cost_orig}")

            print(f"\n--- Testing Basic Prompt 1 on {llm_model} ---")
            system_1, user_1 = get_prompt_1(query_orig)
            cost_rewr_1 = evaluate_single_prompt([{"role": "system", "content": system_1}, {"role": "user", "content": user_1}])
            print(f"Rewritten Cost (Prompt 1): {cost_rewr_1}")

            print(f"\n--- Testing Basic Prompt 2 on {llm_model} ---")
            system_2, user_2 = get_prompt_2(query_orig)
            cost_rewr_2 = evaluate_single_prompt([{"role": "system", "content": system_2}, {"role": "user", "content": user_2}])
            print(f"Rewritten Cost (Prompt 2): {cost_rewr_2}")

            print(f"\n--- Testing Basic Prompt 3 on {llm_model} ---")
            system_3, user_3 = get_prompt_3(query_orig)
            cost_rewr_3 = evaluate_single_prompt([{"role": "system", "content": system_3}, {"role": "user", "content": user_3}])
            print(f"Rewritten Cost (Prompt 3): {cost_rewr_3}")

            print(f"\n--- Testing Basic Prompt 4 on {llm_model} ---")
            cost_rewr_4 = evaluate_prompt_4(query_orig)
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