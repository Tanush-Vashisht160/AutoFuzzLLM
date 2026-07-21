import sqlite3


class DatabaseManager:

    def __init__(self):

        self.connection = sqlite3.connect(
            "autofuzz.db",
            check_same_thread=False
        )

        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS campaigns (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            created_at TEXT,

            provider TEXT,

            seed_prompt TEXT

        )

        """)

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS results (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            campaign_id INTEGER,

            mutated_prompt TEXT,

            response TEXT,

            risk TEXT

        )

        """)

        self.connection.commit()

    def create_campaign(
        self,
        created_at,
        provider,
        seed_prompt
    ):

        self.cursor.execute(

            """
            INSERT INTO campaigns
            (
                created_at,
                provider,
                seed_prompt
            )
            VALUES (?, ?, ?)
            """,

            (
                created_at,
                provider,
                seed_prompt
            )
        )

        self.connection.commit()

        return self.cursor.lastrowid

    def save_result(
        self,
        campaign_id,
        prompt,
        response,
        risk
    ):

        self.cursor.execute(

            """
            INSERT INTO results
            (
                campaign_id,
                mutated_prompt,
                response,
                risk
            )

            VALUES (?, ?, ?, ?)
            """,

            (
                campaign_id,
                prompt,
                response,
                risk
            )
        )

        self.connection.commit()
