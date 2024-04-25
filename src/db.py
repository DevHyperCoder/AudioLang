import sqlite3
from datetime import datetime
from fsrs import Card, State
from .utils import get_audio_files_in_dir

con = sqlite3.connect("")


def configure_db(base_path: str, db_path: str):
    con = sqlite3.connect(db_path)

    create_tables(con)
    make_sure_audio_exists(con, get_audio_files_in_dir(base_path))

    return con


def create_tables(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute(
        """
CREATE TABLE IF NOT EXISTS cards (
    id VARCHAR PRIMARY KEY,
    due INTEGER NON NULL,
    stability INTEGER NON NULL,
    difficulty INTEGER NON NULL,
    elapsed_days INTEGER NON NULL,
    scheduled_days INTEGER NON NULL,
    reps INTEGER NON NULL,
    lapses INTEGER NON NULL,
    state INTEGER NON NULL,
    last_review INTEGER
);
"""
    )
    con.commit()

    print("Table `cards` created")


def get_dict_for_card(card: Card):
    last_review = None
    if hasattr(card, "last_review"):
        last_review = card.last_review

    return {
        "due": card.due,
        "stability": card.stability,
        "difficulty": card.difficulty,
        "elapsed_days": card.elapsed_days,
        "scheduled_days": card.scheduled_days,
        "reps": card.reps,
        "lapses": card.lapses,
        "state": card.state,
        "last_review": last_review,
    }


def make_sure_audio_exists(con: sqlite3.Connection, audio_files: list[str]):
    """
    Creates cards for audio files that do not exist
    """
    data = [{"id": p, **get_dict_for_card(Card())} for p in audio_files]

    cur = con.cursor()
    cur.executemany(
        """
INSERT OR IGNORE INTO cards VALUES
(:id, 
 :due,
 :stability,
 :difficulty,
 :elapsed_days,
 :scheduled_days,
 :reps,
 :lapses,
 :state,
 :last_review
 )""",
        data,
    )

    con.commit()
    print("Table `cards` populated")


class WordCard:
    def __init__(self, id: str, card: Card):
        self.word_path = id
        self.id = id
        self.card = card
        self.fname = self.word_path.split(".")[0]

    @staticmethod
    def from_row(row: sqlite3.Row):
        last_review = None
        if row["last_review"]:
            last_review = datetime.fromisoformat(row["last_review"])

        card = Card()
        card.due = datetime.fromisoformat(row["due"])
        card.stability = int(row["stability"])
        card.difficulty = int(row["difficulty"])
        card.elapsed_days = int(row["elapsed_days"])
        card.scheduled_days = int(row["scheduled_days"])
        card.reps = int(row["reps"])
        card.lapses = int(row["lapses"])
        card.state = State(int(row["state"]))
        card.last_review = last_review  # type: ignore
        return WordCard(row["id"], card)


def cards_due_before_now(con: sqlite3.Connection):
    cur = con.cursor()
    cur.row_factory = sqlite3.Row  # type:ignore
    now = datetime.utcnow()
    cur.execute("SELECT * FROM cards WHERE due <= ?", (now,))

    return [WordCard.from_row(row) for row in cur.fetchall()]


def update_card(con: sqlite3.Connection, id: str, card: Card):
    data = {"id": id, **get_dict_for_card(card)}
    cur = con.cursor()
    cur.execute(
        """
UPDATE cards
 SET
due = :due,
stability = :stability,
difficulty = :difficulty,
elapsed_days = :elapsed_days,
scheduled_days = :scheduled_days,
reps = :reps,
lapses = :lapses,
state = :state,
last_review = :last_review
WHERE id = :id
                """,
        data,
    )
    con.commit()
