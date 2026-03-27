# --- BASIC PROMPTS (Figure 4) ---

def get_prompt_1(query: str) -> tuple[str, str]:
    """Baseline prompt. No system persona defined in the paper for this one."""
    system = ""
    user = f"""{query}\n\nRewrite this query to improve performance."""
    return system, user

def get_prompt_2(query: str, db_engine: str = "PostgreSQL") -> tuple[str, str]:
    """Explicit instructions for semantic equivalence."""
    system = f"You are a database expert and SQL optimizer. Your role involves identifying inefficient SQL queries and transforming them into optimized, functionally equivalent {db_engine} versions."
    user = f"""{query}\n\nRewrite this query to improve performance of query while maintaining semantic equivalence."""
    return system, user

def get_prompt_3(query: str, db_engine: str = "PostgreSQL") -> tuple[str, str]:
    """Verbose instructions providing step-by-step guidance."""
    system = f"You are a database expert and SQL optimizer. Your role involves identifying inefficient SQL queries and transforming them into optimized, functionally equivalent {db_engine} versions. Your tone is analytical and instructional."
    user = f"""A user has provided the following {db_engine} query that is potentially inefficient:

{query}

The task is to first identify whether the query is inefficient or not. If it is inefficient, you must rewrite the query to make it more efficient while maintaining semantic equivalence. Here are a few steps that can help you complete the task:
1. Start by identifying specific inefficiencies in the provided query. If you feel the original query is already efficient, skip the next two steps, and simply return the query as-is.
2. Next, provide guidelines for optimizations, and explain the rationale behind the recommended optimizations. Correspond how these changes would map onto the original query to maintain syntactic and semantic equivalence.
3. Finally craft the new, optimized {db_engine} query which includes all the enhancements discussed. Give complete rewritten query with no manual involvement by user."""
    return system, user

# --- REWRITE RULES (Table 2) ---

RULES = {
    "R1": "Use CTEs (Common Table Expressions) to avoid repeated computation of a given expression.",
    "R2": "When multiple subqueries use the same base table, rewrite to scan the base table only once.",
    "R3": "Remove redundant conjunctive filter predicates.",
    "R4": "Remove redundant key (PK-FK) joins.",
    "R5": "Choose EXIST or IN from subquery selectivity (high/low).",
    "R6": "Pre-filter tables involved in self-joins and with low selectivities on their filter and/or join predicates. Remove any redundant filters from the main query. Do not create explicit join statements."
}

# --- ADVANCED PROMPT TEMPLATES (Figure 5) ---

def get_redundancy_prompt(db_engine: str, rule_text: str, example_orig: str, example_rewr: str, query: str, example_2_orig: str = None, example_2_rewr: str = None) -> tuple[str, str]:
    """Template for redundancy-removal prompts (a) with an optional second example."""
    system = f"You are a database expert and SQL optimizer. Your role involves identifying inefficient SQL queries and transforming them into optimized, functionally equivalent {db_engine} versions. Your tone is analytical and instructional."
    
    examples_block = f"""[ORIGINAL]
{example_orig}
[REWRITTEN]
{example_rewr}"""

    if example_2_orig and example_2_rewr:
        examples_block += f"""

[ORIGINAL]
{example_2_orig}
[REWRITTEN]
{example_2_rewr}"""

    user = f"""This is a task to rewrite queries to improve performance using the following rewrite rule:
{rule_text}

{examples_block}

Now consider the query below and try to rewrite it to improve the performance.
[ORIGINAL]
{query}
[REWRITTEN]"""
    return system, user

def get_statistics_prompt(db_engine: str, rule_text: str, example_orig: str, example_stats: str, example_rewr: str, query: str, query_stats: str, example_2_orig: str = None, example_2_stats: str = None, example_2_rewr: str = None) -> tuple[str, str]:
    """Template for statistics-guidance prompts (b) with an optional second example."""
    system = f"You are a database optimizer and your task is to analyze the given {db_engine} query using database schema and statistical information available to you. Find inefficiency in the query. If query is already efficient then return the original query. Otherwise, rewrite the query in a more efficient way to improve its performance, and explain your rewrites."
    
    examples_block = f"""[ORIGINAL]
{example_orig}
[STATISTICS]
{example_stats}
[REWRITTEN]
{example_rewr}"""

    if example_2_orig and example_2_stats and example_2_rewr:
        examples_block += f"""

[ORIGINAL]
{example_2_orig}
[STATISTICS]
{example_2_stats}
[REWRITTEN]
{example_2_rewr}"""

    user = f"""This is a task to improve query performance using the following rewrite rule:
{rule_text}

Here is an example to help you:
{examples_block}

Now consider the query and statistics given below and try to rewrite the query to improve performance.
[ORIGINAL]
{query}
[STATISTICS]
{query_stats}
[REWRITTEN]"""
    return system, user