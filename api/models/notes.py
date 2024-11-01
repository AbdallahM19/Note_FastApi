"""notes.py"""

from typing import Union, Optional
from datetime import datetime
# from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
from api.database import NoteDb, get_session


def convert_class_note_to_object(note: NoteDb) -> dict:
    """Converts a Note_db object to a Note dict"""
    return {
        "id": note.id,
        "user_id": note.user_id,
        "title": note.title,
        "content": note.content,
        "time_created": note.time_created,
        "time_edition": note.time_edition,
    }


class Note():
    """Note Class"""
    def __init__(self):
        self.sess = get_session()

    # def get_notes_by_title(
    #     self, title: str, skip: int = None, limit:int = None
    # ):
    #     try:
    #         notes_data = self.sess.query(Note_db).filter(
    #             Note_db.title.like(f'%{title}%')
    #         ).offset(skip).limit(limit).all()

    #         if not notes_data:
    #             return "No notes found with the given {}".format(title)

    #         if len(notes_data) == 1:
    #             return self.convert_class_note_to_object(notes_data[0])
    #         else:
    #             return [
    #                 self.convert_class_note_to_object(note)
    #                 for note in notes_data
    #             ]
    #     except Exception as e:
    #         raise Exception("An error occurred while fetching notes by title: {}".format(e))
    #     finally:
    #         self.sess.close()

    # def get_notes_by_content(
    #     self, content: str, skip: int = None, limit:int = None
    # ):
    #     try:
    #         notes_data = self.sess.query(Note_db).filter(
    #             Note_db.content.like(f'%{content}%')
    #         ).offset(skip).limit(limit).all()

    #         if not notes_data:
    #             return "No notes found with the given {}".format(content)

    #         if len(notes_data) == 1:
    #             return self.convert_class_note_to_object(notes_data[0])
    #         else:
    #             return [
    #                 self.convert_class_note_to_object(note)
    #                 for note in notes_data
    #             ]
    #     except Exception as e:
    #         raise Exception("An error occurred while fetching notes by title: {}".format(e))
    #     finally:
    #         self.sess.close()

    def get_note_by_id(self, note_id: int):
        """Fetches a note by its id."""
        try:
            note = self.sess.query(NoteDb).filter(NoteDb.id == note_id).first()
            if note:
                return convert_class_note_to_object(note)
            return f"Note with id {note_id} not found"
        except Exception as e:
            raise SQLAlchemyError(
                f"An error occurred while fetching note by id: {e}"
            ) from e
        finally:
            self.sess.close()

    def get_all_notes(self, skip: Optional[int] = None, limit: Optional[int] = None):
        """Fetches all notes from the database."""
        try:
            notes = self.sess.query(NoteDb)

            if skip is not None and limit is not None:
                notes = notes.offset(skip).limit(limit)
            elif skip is None and limit:
                notes = notes.offset(0).limit(limit)
            elif skip and limit is None:
                notes = notes.offset(skip).limit(10)

            notes = notes.all()

            if not notes:
                return "No notes found"

            if isinstance(notes, list) and len(notes) == 1:
                return convert_class_note_to_object(notes[0])
            return [
                convert_class_note_to_object(note)
                for note in notes
            ]
        except Exception as e:
            raise SQLAlchemyError(
                f"An error occurred while fetching note by id: {e}"
            ) from e
        finally:
            self.sess.close()

    def search_notes(
        self, field: str, query: str,
        skip: Optional[int] = None, limit: Optional[int] = None
    ):
        """Search notes based on field and query."""
        try:
            notes = None
            q = query.lower()

            if field == "title":
                notes = self.sess.query(NoteDb).filter(
                    NoteDb.title.like(f'%{q}%')
                )
            elif field == "content":
                notes = self.sess.query(NoteDb).filter(
                    NoteDb.content.like(f'%{q}%')
                )

            if not notes:
                return "No notes found"

            if skip is not None and limit is not None:
                notes = notes.offset(skip).limit(limit).all()
            elif skip is not None:
                notes = notes.offset(skip).limit(10).all()
            elif limit is not None:
                notes = notes.limit(limit).all()
            else:
                notes = notes.all()

            if not notes:
                return f"No notes found '{query}' for the search query."

            if isinstance(notes, list) and len(notes) == 1:
                return convert_class_note_to_object(notes[0])
            return [
                convert_class_note_to_object(note)
                for note in notes
            ]
        except Exception as e:
            raise SQLAlchemyError(
                f"An error occurred while searching notes: {e}"
            ) from e
        finally:
            self.sess.close()

    # def get_notes(
    #     self,
    #     field: str,
    #     query: Union[str, None] = None,
    #     note_id: Union[int, None] = None,
    #     skip: Union[int, None] = 0,
    #     limit: Union[int, None] = None
    # ) -> Union[dict, list, None]:
    #     """Fetches notes based on the given field and query."""
    #     try:
    #         notes_data = None

    #         if field == 'id' and note_id:
    #             notes_data = self.sess.query(NoteDb).filter(
    #                 NoteDb.id == query
    #             ).first()
    #         elif field == "list":
    #             notes_data = self.sess.query(NoteDb)
    #         elif field == "title":
    #             notes_data = self.sess.query(NoteDb).filter(
    #                 NoteDb.title.like(f'%{query}%')
    #             )
    #         elif field == "content":
    #             notes_data = self.sess.query(NoteDb).filter(
    #                 NoteDb.content.like(f'%{query}%')
    #             )

    #         if skip and limit:
    #             notes_data = notes_data.offset(skip).limit(limit).all()
    #         elif skip:
    #             notes_data = notes_data.offset(skip).all()

    #         if not notes_data:
    #             print(f"No {field}s found with the given query: {query}")
    #             return None

    #         if len(notes_data) == 1:
    #             return self.convert_class_note_to_object(notes_data[0])

    #         return [
    #             self.convert_class_note_to_object(note)
    #             for note in notes_data
    #         ]
    #     except Exception as e:
    #         raise SQLAlchemyError(
    #             f"An error occurred while fetching notes by {field}: {e}"
    #         ) from e
    #     finally:
    #         self.sess.close()

    def create_a_new_note(
        self, user_id: int, content: str, title: Union[str, None] = None,
    ) -> dict:
        """Creates a new note with the given content and title."""
        try:
            new_note = NoteDb(
                user_id=user_id,
                content=content,
                title=title,
            )
            self.sess.add(new_note)
            self.sess.commit()
            return convert_class_note_to_object(new_note)
        except Exception as e:
            raise SQLAlchemyError(f"An error occurred while creating a new note: {e}") from e
        finally:
            self.sess.close()

    def update_note_data(
        self,
        note_id: int,
        content: str,
        title: Union[str, None] = None
    ) -> dict:
        """Updates the note data in the database."""
        try:
            old_note = self.sess.query(NoteDb).filter(
                NoteDb.id == note_id
            ).first()

            if old_note is None:
                raise ValueError(f"No note found with id {note_id}")

            old_note.content = content
            old_note.title = title
            old_note.time_edition = datetime.now()

            self.sess.commit()
            return convert_class_note_to_object(old_note)
        except Exception as e:
            raise SQLAlchemyError(f"An error occurred while updating note data: {e}") from e
        finally:
            self.sess.close()

    def delete_note_by_id(self, note_id: int):
        """Deletes a note by its ID."""
        try:
            self.sess.query(NoteDb).filter(
                NoteDb.id == note_id
            ).delete()
            self.sess.commit()
        except Exception as e:
            self.sess.rollback()
            raise SQLAlchemyError(f"An error occurred while deleting note by ID: {e}") from e
        finally:
            self.sess.close()


    # def get_note_by_id(self, note_id):
    #     """Get note by id"""
    #     try:
    #         note = self.sess.query(NoteDb).filter(
    #             NoteDb.id == note_id
    #         ).first()
    #         return self.convert_class_note_to_object(note)
    #     except Exception as e:
    #         raise SQLAlchemyError(
    #             f"An error occurred while fetching note by id: {e}"
    #         ) from e
    #     finally:
    #         self.sess.close()

    # def create_note(self, ):
    #     pass
