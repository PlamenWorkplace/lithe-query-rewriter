queries = [
    {
        "id": "Q1",
        "query": """
            SELECT p.name, AVG(g.test_grade) as avg_test_grade 
            FROM professors p 
            JOIN courses c ON p.id = c.professor_id 
            JOIN grades g ON c.code = g.course_code AND c.year = g.course_year 
            GROUP BY p.id, p.name 
            ORDER BY avg_test_grade DESC 
            LIMIT 3;
        """
    },
    {
        "id": "Q2",
        "query": """
            SELECT s.name, s.cohort 
            FROM students s 
            JOIN grades g ON s.id = g.student_id 
            GROUP BY s.id, s.name, s.cohort 
            HAVING COUNT(g.course_code) > 3 AND AVG(g.project_grade) > 8.0;
        """
    },
    {
        "id": "Q3",
        "query": """
            SELECT s.name 
            FROM students s 
            WHERE s.cohort = 2021 AND s.id NOT IN (
                SELECT g.student_id 
                FROM grades g 
                JOIN courses c ON g.course_code = c.code AND g.course_year = c.year 
                JOIN professors p ON c.professor_id = p.id 
                WHERE p.department = 'Computer Science'
            );
        """
    },
    {
        "id": "Q4",
        "query": """
            WITH DeptEcts AS (
                SELECT p.department, p.name, SUM(c.ects) as total_ects, 
                       RANK() OVER(PARTITION BY p.department ORDER BY SUM(c.ects) DESC) as rnk 
                FROM professors p 
                JOIN courses c ON p.id = c.professor_id 
                WHERE c.year = 2023 
                GROUP BY p.department, p.id, p.name
            ) 
            SELECT department, name, total_ects 
            FROM DeptEcts 
            WHERE rnk = 1;
        """
    },
    {
        "id": "Q5",
        "query": """
            SELECT course_code, course_year 
            FROM grades 
            GROUP BY course_code, course_year 
            HAVING AVG(test_grade) < (SELECT AVG(test_grade) FROM grades);
        """
    },
    {
        "id": "Q6",
        "query": """
            SELECT s.name 
            FROM students s 
            JOIN grades g ON s.id = g.student_id 
            GROUP BY s.id, s.name 
            HAVING MAX(g.project_grade) = 10.0 AND AVG(g.test_grade) < 6.0;
        """
    },
    {
        "id": "Q7",
        "query": """
            SELECT DISTINCT p.name 
            FROM professors p 
            JOIN courses c ON p.id = c.professor_id 
            WHERE c.year = 2022 AND p.id NOT IN (
                SELECT professor_id FROM courses WHERE year = 2023
            );
        """
    },
    {
        "id": "Q8",
        "query": """
            SELECT department 
            FROM (
                SELECT p.department, c.code 
                FROM professors p 
                JOIN courses c ON p.id = c.professor_id 
                JOIN grades g ON c.code = g.course_code AND c.year = g.course_year 
                WHERE c.year = 2023 
                GROUP BY p.department, c.code 
                HAVING AVG(g.project_grade) < 5.5
            ) as low_performing_courses 
            GROUP BY department 
            HAVING COUNT(code) > 5;
        """
    },
    {
        "id": "Q9",
        "query": """
            SELECT c.code, c.year, p.name as professor_name, 
                   COUNT(g.student_id) as student_count, AVG(g.test_grade) as avg_test 
            FROM courses c 
            JOIN professors p ON c.professor_id = p.id 
            JOIN grades g ON c.code = g.course_code AND c.year = g.course_year 
            GROUP BY c.code, c.year, p.id, p.name 
            HAVING COUNT(g.student_id) > 50 AND AVG(g.test_grade) > 7.5 
            ORDER BY avg_test DESC;
        """
    }
]