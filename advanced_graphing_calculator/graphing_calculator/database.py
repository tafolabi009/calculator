# database.py
import sqlite3

class AdvancedDatabase:
    def __init__(self):
        self.db_file = "calculator.db"
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create graphs table
        c.execute('''
            CREATE TABLE IF NOT EXISTS graphs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                expression TEXT NOT NULL,
                variable TEXT NOT NULL,
                x_min REAL,
                x_max REAL,
                y_min REAL,
                y_max REAL,
                scale_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Create comments table
        c.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                graph_id INTEGER,
                teacher_id INTEGER,
                comment_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (graph_id) REFERENCES graphs(id),
                FOREIGN KEY (teacher_id) REFERENCES users(id)
            )
        ''')

        # Add default teacher account if not exists
        c.execute('''
            INSERT OR IGNORE INTO users (username, password, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('teacher1', 'teacher123', 'teacher', 'Default Teacher', 'teacher@example.com'))

        conn.commit()
        conn.close()

    def add_user(self, username, password, role, full_name, email):
        """Add a new user to the database"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute('''
                INSERT INTO users (username, password, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password, role, full_name, email))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username, password):
        """Verify user credentials and return user data"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            SELECT id, username, role, full_name, email 
            FROM users 
            WHERE username = ? AND password = ?
        ''', (username, password))
        user_data = c.fetchone()
        conn.close()

        if user_data:
            return {
                'id': user_data[0],
                'username': user_data[1],
                'role': user_data[2],
                'full_name': user_data[3],
                'email': user_data[4]
            }
        return None

    def get_all_students(self):
        """Get list of all students"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            SELECT id, username, full_name 
            FROM users 
            WHERE role = 'student'
        ''')
        students = c.fetchall()
        conn.close()
        return students

    def save_graph(self, user_id, graph_data):
        """Save a graph with all its properties"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO graphs (
                    user_id, name, expression, variable,
                    x_min, x_max, y_min, y_max, scale_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                graph_data['name'],
                graph_data['expression'],
                graph_data['variable'],
                graph_data['x_min'],
                graph_data['x_max'],
                graph_data['y_min'],
                graph_data['y_max'],
                graph_data['scale_type']
            ))
            graph_id = c.lastrowid
            conn.commit()
            return graph_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


    def get_user_graphs(self, user_id):
        """Get all graphs for a specific user"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            SELECT id, name, expression, variable, x_min, x_max, y_min, y_max, scale_type
            FROM graphs
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        graphs = c.fetchall()
        conn.close()

        return [
            {
                'id': g[0],
                'name': g[1],
                'expression': g[2],
                'variable': g[3],
                'x_min': g[4],
                'x_max': g[5],
                'y_min': g[6],
                'y_max': g[7],
                'scale_type': g[8]
            }
            for g in graphs
        ]

    def add_comment(self, graph_id, teacher_id, comment_text):
        """Add a comment to a graph"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            INSERT INTO comments (graph_id, teacher_id, comment_text)
            VALUES (?, ?, ?)
        ''', (graph_id, teacher_id, comment_text))
        conn.commit()
        conn.close()

    def get_graph_comments(self, graph_id):
        """Get all comments for a specific graph"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            SELECT c.comment_text, u.full_name, c.created_at
            FROM comments c
            JOIN users u ON c.teacher_id = u.id
            WHERE c.graph_id = ?
            ORDER BY c.created_at DESC
        ''', (graph_id,))
        comments = c.fetchall()
        conn.close()

        return [
            {
                'comment': c[0],
                'teacher_name': c[1],
                'timestamp': c[2]
            }
            for c in comments
        ]


    def get_user_graph_history(self, user_id):
        """Get all graphs for a user with their comments"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            SELECT g.id, g.name, g.expression, g.variable,
                   g.x_min, g.x_max, g.y_min, g.y_max, g.scale_type,
                   g.created_at
            FROM graphs g
            WHERE g.user_id = ?
            ORDER BY g.created_at DESC
        ''', (user_id,))
        graphs = c.fetchall()

        result = []
        for g in graphs:
            # Get comments for each graph
            c.execute('''
                SELECT c.comment_text, u.username, c.created_at
                FROM comments c
                JOIN users u ON c.teacher_id = u.id
                WHERE c.graph_id = ?
                ORDER BY c.created_at DESC
            ''', (g[0],))
            comments = c.fetchall()

            result.append({
                'id': g[0],
                'name': g[1],
                'expression': g[2],
                'variable': g[3],
                'x_min': g[4],
                'x_max': g[5],
                'y_min': g[6],
                'y_max': g[7],
                'scale_type': g[8],
                'created_at': g[9],
                'comments': [{
                    'text': c[0],
                    'teacher': c[1],
                    'timestamp': c[2]
                } for c in comments]
            })

        conn.close()
        return result

    def get_student_graphs(self, student_username):
        """Get all graphs for a specific student"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            SELECT g.id, g.name, g.expression, g.variable,
                   g.x_min, g.x_max, g.y_min, g.y_max, g.scale_type,
                   g.created_at
            FROM graphs g
            JOIN users u ON g.user_id = u.id
            WHERE u.username = ?
            ORDER BY g.created_at DESC
        ''', (student_username,))
        graphs = c.fetchall()
        conn.close()
        return [{
            'id': g[0],
            'name': g[1],
            'expression': g[2],
            'variable': g[3],
            'x_min': g[4],
            'x_max': g[5],
            'y_min': g[6],
            'y_max': g[7],
            'scale_type': g[8],
            'created_at': g[9]
        } for g in graphs]