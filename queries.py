queries = [
    {
        "id": "Q1",
        "query": """
            SELECT c.code, c.year, p.name, g.student_id, g.test_grade
            FROM courses c
            JOIN professors p ON c.professor_id = p.id
            JOIN grades g ON c.code = g.course_code AND c.year = g.course_year
            WHERE g.test_grade = (
                SELECT MAX(g2.test_grade)
                FROM grades g2
                WHERE g2.course_code = c.code AND g2.course_year = c.year
            );
        """
    },
    {
        "id": "Q2",
        "query": """
            SELECT s.id, s.name, s.email
            FROM students s
            JOIN grades g ON s.id = g.student_id
            JOIN courses c ON g.course_code = c.code AND g.course_year = c.year
            JOIN professors p ON c.professor_id = p.id
            WHERE p.department = 'Physics' AND g.test_grade > 9.0
            UNION
            SELECT s.id, s.name, s.email
            FROM students s
            JOIN grades g ON s.id = g.student_id
            JOIN courses c ON g.course_code = c.code AND g.course_year = c.year
            JOIN professors p ON c.professor_id = p.id
            WHERE p.department = 'Physics' AND g.project_grade > 9.0;
        """
    },
    {
        "id": "Q3",
        "query": """
            SELECT p.name, p.department
            FROM professors p
            WHERE p.id IN (
                SELECT c.professor_id 
                FROM courses c 
                JOIN grades g ON c.code = g.course_code AND c.year = g.course_year 
                WHERE g.test_grade < 5.0
            )
            AND p.id IN (
                SELECT c.professor_id 
                FROM courses c 
                JOIN grades g ON c.code = g.course_code AND c.year = g.course_year 
                WHERE g.project_grade < 5.0
            );
        """
    },
    {
        "id": "Q4",
        "query": """
            SELECT p.name, p.department
            FROM professors p
            WHERE p.id IN (
                SELECT c.professor_id
                FROM courses c
                WHERE c.code IN (
                    SELECT g.course_code
                    FROM grades g
                    JOIN students s ON g.student_id = s.id
                    WHERE s.cohort = 2020
                ) AND c.year IN (
                    SELECT g.course_year
                    FROM grades g
                    JOIN students s ON g.student_id = s.id
                    WHERE s.cohort = 2020
                )
            );
        """
    },
    {
        "id": "Q5",
        "query": """
            SELECT 
                CAST((SELECT COUNT(*) 
                      FROM grades g 
                      JOIN courses c ON g.course_code = c.code AND g.course_year = c.year 
                      JOIN professors p ON c.professor_id = p.id 
                      WHERE p.department = 'Computer Science' AND g.test_grade >= 8.0) AS DECIMAL(15, 4))
                / 
                CAST((SELECT COUNT(*) 
                      FROM grades g 
                      JOIN courses c ON g.course_code = c.code AND g.course_year = c.year 
                      JOIN professors p ON c.professor_id = p.id 
                      WHERE p.department = 'Computer Science' AND g.test_grade < 5.5) AS DECIMAL(15, 4)) AS excellence_ratio;
        """
    },
    {
        "id": "Q6",
        "query": """
            SELECT g.course_code, g.course_year, SUM(g.test_grade) as total_test_score
            FROM grades g
            JOIN courses c ON g.course_code = c.code AND g.course_year = c.year
            JOIN professors p ON c.professor_id = p.id
            WHERE p.department = 'Mathematics' AND g.test_grade > 8.0
            GROUP BY g.course_code, g.course_year
            HAVING SUM(g.test_grade) > (
                SELECT SUM(g2.test_grade) 
                FROM grades g2 
                JOIN courses c2 ON g2.course_code = c2.code AND g2.course_year = c2.year 
                JOIN professors p2 ON c2.professor_id = p2.id 
                WHERE p2.department = 'Mathematics' AND g2.test_grade > 8.0 AND g2.course_year = 2022
            );
        """
    },
    {
        "id": "Q7",
        "query": """
            SELECT c.code, c.year, c.ects
            FROM courses c
            WHERE (c.code, c.year) NOT IN (
                SELECT course_code, course_year 
                FROM grades
            );
        """
    },
    {
        "id": "Q8",
        "query": """
            SELECT g1.student_id, g1.course_code, g1.test_grade as grade_2022, g2.test_grade as grade_2023
            FROM grades g1
            JOIN grades g2 ON g1.student_id = g2.student_id AND g1.course_code = g2.course_code
            WHERE g1.course_year = 2022 AND g2.course_year = 2023 
            AND g1.test_grade > 9.0 AND g2.test_grade > 9.0;
        """
    },
    {
        "id": "Q9",
        "query": """
            SELECT t.department, SUM(t.project_grade) as DeptProjectRating
            FROM (
                SELECT p.department, c.code, c.year, g.project_grade
                FROM professors p
                JOIN courses c ON p.id = c.professor_id
                JOIN grades g ON c.code = g.course_code AND c.year = g.course_year
                WHERE g.test_grade > 8.0
            ) t
            JOIN (
                SELECT p.department, COUNT(*) as num_courses
                FROM professors p
                JOIN courses c ON p.id = c.professor_id
                GROUP BY p.department
                HAVING COUNT(*) > 10
            ) t2 ON t.department = t2.department
            GROUP BY t.department;
        """
    }
]