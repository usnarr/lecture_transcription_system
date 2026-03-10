import pytest
import psycopg
from unittest.mock import AsyncMock, MagicMock, patch
from src.common.db.repository import LectureDBRepository


@pytest.fixture
def mock_connection():
    """Fixture for mocked database connection"""
    conn = AsyncMock(spec=psycopg.AsyncConnection)
    return conn


@pytest.fixture
def lecture_repository(mock_connection):
    """Fixture for LectureRepository with mocked connection"""
    return LectureDBRepository(mock_connection)


@pytest.mark.asyncio
async def test_get_system_message(lecture_repository, mock_connection):
    """Test get_system_message method"""
    mock_cursor = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value=("System prompt text",))
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    result = await lecture_repository.get_system_message("math")
    
    assert result == "System prompt text"
    mock_cursor.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_prompt_message(lecture_repository, mock_connection):
    """Test get_prompt_message method"""
    mock_cursor = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value=("User prompt text",))
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    result = await lecture_repository.get_prompt_message("programming")
    
    assert result == "User prompt text"
    mock_cursor.execute.assert_called_once()


@pytest.mark.asyncio
async def test_save_summary(lecture_repository, mock_connection):
    """Test save_summary method"""
    mock_cursor = AsyncMock()
    mock_cursor.description = [("id",), ("summary_text",), ("last_processing_timestamp",)]
    mock_cursor.fetchone = AsyncMock(return_value=(1, "Test summary", None))
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    result = await lecture_repository.save_summary("Test summary")
    
    assert result["id"] == 1
    assert result["summary_text"] == "Test summary"
    mock_connection.commit.assert_called_once()


@pytest.mark.asyncio
async def test_save_transcription(lecture_repository, mock_connection):
    """Test save_transcription method"""
    mock_cursor = AsyncMock()
    mock_cursor.description = [("id",), ("transcription_text",)]
    mock_cursor.fetchone = AsyncMock(return_value=(1, "Test transcription"))
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    result = await lecture_repository.save_transcription("Test transcription")
    
    assert result["id"] == 1
    assert result["transcription_text"] == "Test transcription"
    mock_connection.commit.assert_called_once()


@pytest.mark.asyncio
async def test_add_task(lecture_repository, mock_connection):
    """Test add_task method"""
    mock_cursor = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value=(5,))
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    with patch.object(lecture_repository, 'update_lecture_task', new_callable=AsyncMock) as mock_update:
        result = await lecture_repository.add_task("celery-task-123", 1)
        
        assert result == 5
        mock_update.assert_called_once_with(1, 5)
        mock_connection.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_lecture_task(lecture_repository, mock_connection):
    """Test update_lecture_task method"""
    mock_cursor = AsyncMock()
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    await lecture_repository.update_lecture_task(1, 5)
    
    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_lectures_by_ids(lecture_repository, mock_connection):
    """Test get_lectures_by_ids method"""
    mock_cursor = AsyncMock()
    mock_cursor.description = [
        ("lecture_id",), ("lecture_recording_path",), ("lecture_type",), 
        ("is_processed",), ("task_id",)
    ]
    mock_cursor.fetchall = AsyncMock(return_value=[
        (1, "/path/to/lecture1.mp4", "math", False, None),
        (2, "/path/to/lecture2.mp4", "programming", True, 5)
    ])
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    result = await lecture_repository.get_lectures_by_ids([1, 2])
    
    assert len(result) == 2
    assert result[0]["lecture_id"] == 1
    assert result[0]["is_processed"] is False
    assert result[1]["lecture_id"] == 2
    assert result[1]["is_processed"] is True


@pytest.mark.asyncio
async def test_set_lecture_processed(lecture_repository, mock_connection):
    """Test set_lecture_processed method"""
    mock_cursor = AsyncMock()
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    await lecture_repository.set_lecture_processed(1)
    
    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_task_by_id(lecture_repository, mock_connection):
    """Test get_task_by_id method"""
    mock_cursor = AsyncMock()
    mock_cursor.description = [
        ("id",), ("task_status_id",), ("transcription_id",), 
        ("summary_id",), ("celery_task_id",), ("last_processing_timestamp",)
    ]
    mock_cursor.fetchone = AsyncMock(return_value=(1, 1, 10, 20, "celery-123", None))
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    result = await lecture_repository.get_task_by_id(1)
    
    assert result["id"] == 1
    assert result["celery_task_id"] == "celery-123"


@pytest.mark.asyncio
async def test_get_transcription_by_id(lecture_repository, mock_connection):
    """Test get_transcription_by_id method"""
    mock_cursor = AsyncMock()
    mock_cursor.description = [("id",), ("transcription_text",)]
    mock_cursor.fetchone = AsyncMock(return_value=(10, "Transcription content"))
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    result = await lecture_repository.get_transcription_by_id(10)
    
    assert result["id"] == 10
    assert result["transcription_text"] == "Transcription content"


@pytest.mark.asyncio
async def test_update_summary(lecture_repository, mock_connection):
    """Test update_summary method"""
    mock_cursor = AsyncMock()
    mock_cursor.description = [("id",), ("summary_text",), ("last_processing_timestamp",)]
    mock_cursor.fetchone = AsyncMock(return_value=(20, "Updated summary", None))
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    result = await lecture_repository.update_summary(20, "Updated summary")
    
    assert result["id"] == 20
    assert result["summary_text"] == "Updated summary"
    mock_connection.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_task(lecture_repository, mock_connection):
    """Test update_task method"""
    mock_cursor = AsyncMock()
    mock_cursor.description = [
        ("id",), ("task_status_id",), ("transcription_id",), 
        ("summary_id",), ("celery_task_id",), ("last_processing_timestamp",)
    ]
    mock_cursor.fetchone = AsyncMock(return_value=(1, 3, 10, 20, "celery-123", None))
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    result = await lecture_repository.update_task("celery-123", status=3, transcription_id=10, summary_id=20)
    
    assert result["id"] == 1
    assert result["task_status_id"] == 3
    assert result["transcription_id"] == 10
    assert result["summary_id"] == 20
    mock_connection.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_lecture_type_by_task_id(lecture_repository, mock_connection):
    """Test get_lecture_type_by_task_id method"""
    mock_cursor = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value=("math",))
    mock_connection.cursor.return_value.__aenter__.return_value = mock_cursor
    
    result = await lecture_repository.get_lecture_type_by_task_id("celery-123")
    
    assert result == "math"
    mock_cursor.execute.assert_called_once()