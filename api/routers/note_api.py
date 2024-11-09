"""note_api.py"""

from typing import Union, Optional, Annotated
from fastapi import APIRouter, Path, Depends
from api.app import note_model, user_model
from api.models.notes import NoteData
from api.utils.session import SessionManager, get_session_manager

router = APIRouter(
    prefix='/api',
)


@router.get("/notes/{field}")
async def get_notes_by_field(
    field: Optional[str],
    query: Optional[str] = None,
    note_id: Optional[int] = None,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
) -> Union[list, dict]:
    """Get notes by field"""
    # if field not in ['title', 'content', 'list', 'id']:
    #     raise ValueError(
    #         f"Invalid field: {field}. Must be 'title', 'content', 'list' or 'id'."
    #     )
    try:
        notes_data = None

        match field:
            case 'id' if note_id:
                notes_data = note_model.get_note_by_id(note_id)
            case 'list':
                notes_data = note_model.get_all_notes(skip=skip, limit=limit)
            case 'title' if query:
                notes_data = note_model.search_notes(
                    field="title", query=query, skip=skip, limit=limit
                )
            case 'content' if query:
                notes_data = note_model.search_notes(
                    field="content", query=query, skip=skip, limit=limit
                )
            case 'title' | 'content' if query is None:
                notes_data = f"Invalid query for field: {field}."
            case _:
                notes_data = f"Invalid field: {field}. Must be 'title', 'content', 'list' or 'id'."

        if isinstance(notes_data, str):
            return {"message": notes_data}

        return notes_data
    except Exception as e:
        raise ValueError(
            f"Invalid field: {field}. Must be 'title', 'content', 'list' or 'id'."
        ) from e

    # return note_model.get_notes(
    #     field=field, query=query, note_id=note_id, skip=skip, limit=limit
    # )


@router.post("/notes/create")
async def create_note(
    item: NoteData, session: SessionManager = Depends(get_session_manager)
) -> dict:
    """Create a new note."""
    if item.user_id == 0 or not item.user_id:
        item.user_id = user_model.get_user_by_session_id(session.get_session_id()).id

    new_note = note_model.create_a_new_note(item)

    return {
        "message": "Note created successfully",
        "note": new_note,
    }


@router.put("/notes/{note_id}/update")
async def update_note(
    note_id: Annotated[
        int, Path(
            title="The ID of the note to be updated",
            description="The ID of the note to be updated",
            gt=0
        )
    ],
    content: str,
    title: Optional[str] = None
) -> dict:
    """Update a note."""
    updated_note = note_model.update_note_data(
        note_id=note_id, content=content, title=title
    )
    return updated_note


@router.delete("/notes/{note_id}/delete")
async def delete_note_data_permanently(
    note_id: Annotated[
        int, Path(
            title="The ID of the note to be deleted",
            description="The ID of the note to be deleted",
            gt=0
        )
    ]
) -> dict:
    """Delete note data permanently."""
    note_model.delete_note_by_id(note_id)
    return {"message": f"Note with id {note_id} has been deleted permanently."}



# @router.get("/notes")
# async def get_all_or_limit_notes(
#     skip: Union[int, None] = None,
#     limit: Union[int, None] = None,
#     title: Union[str, None] = None,
# ):
#     if title:
#         return note_model.get_notes_by_title(title, skip, limit)
#     return note_model.get_notes(skip, limit)
