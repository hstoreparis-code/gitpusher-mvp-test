"""
Unit tests for the Credits Service.

Tests credit operations to ensure atomicity and consistency.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from services.credits_service import CreditsService


@pytest.fixture
def mock_db():
    """Mock MongoDB database"""
    db = MagicMock()
    db.users = MagicMock()
    db.billing_transactions = MagicMock()
    db.pending_checkouts = MagicMock()
    
    db.users.find_one = AsyncMock()
    db.users.find_one_and_update = AsyncMock()
    db.billing_transactions.insert_one = AsyncMock()
    db.billing_transactions.find = MagicMock()
    db.pending_checkouts.insert_one = AsyncMock()
    db.pending_checkouts.find_one = AsyncMock()
    db.pending_checkouts.update_one = AsyncMock()
    
    return db


@pytest.fixture
def credits_service(mock_db):
    """Create CreditsService instance with mock DB"""
    return CreditsService(mock_db)


@pytest.mark.asyncio
async def test_get_user_credits(credits_service, mock_db):
    """Test getting user's credit balance"""
    user_id = "user_123"
    mock_db.users.find_one = AsyncMock(return_value={
        "_id": user_id,
        "credits": 15
    })
    
    credits = await credits_service.get_user_credits(user_id)
    
    assert credits == 15
    mock_db.users.find_one.assert_called_once_with({"_id": user_id})


@pytest.mark.asyncio
async def test_get_user_credits_default_zero(credits_service, mock_db):
    """Test getting credits returns 0 for user not found"""
    mock_db.users.find_one = AsyncMock(return_value=None)
    
    credits = await credits_service.get_user_credits("nonexistent_user")
    
    assert credits == 0


@pytest.mark.asyncio
async def test_add_credits(credits_service, mock_db):
    """Test adding credits to user account"""
    user_id = "user_123"
    mock_db.users.find_one_and_update = AsyncMock(return_value={
        "_id": user_id,
        "credits": 25  # After adding 10 to existing 15
    })
    
    transaction = await credits_service.add_credits(
        user_id=user_id,
        amount=10,
        transaction_type="purchase"
    )
    
    # Verify user credits were incremented
    mock_db.users.find_one_and_update.assert_called_once()
    update_call = mock_db.users.find_one_and_update.call_args
    assert update_call[0][0] == {"_id": user_id}
    assert update_call[0][1] == {"$inc": {"credits": 10}}
    
    # Verify transaction was logged
    assert transaction["user_id"] == user_id
    assert transaction["amount"] == 10
    assert transaction["type"] == "purchase"
    assert transaction["credits"] == 25
    
    mock_db.billing_transactions.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_consume_credits_success(credits_service, mock_db):
    """Test consuming credits successfully"""
    user_id = "user_123"
    mock_db.users.find_one = AsyncMock(return_value={
        "_id": user_id,
        "credits": 10
    })
    mock_db.users.find_one_and_update = AsyncMock(return_value={
        "_id": user_id,
        "credits": 9  # After consuming 1
    })
    
    result = await credits_service.consume_credits(user_id, 1)
    
    assert result is True
    
    # Verify credits were decremented (via add_credits with negative amount)
    mock_db.users.find_one_and_update.assert_called_once()
    update_call = mock_db.users.find_one_and_update.call_args
    assert update_call[0][1] == {"$inc": {"credits": -1}}


@pytest.mark.asyncio
async def test_consume_credits_insufficient(credits_service, mock_db):
    """Test consuming credits fails with insufficient balance"""
    user_id = "user_123"
    mock_db.users.find_one = AsyncMock(return_value={
        "_id": user_id,
        "credits": 0
    })
    
    result = await credits_service.consume_credits(user_id, 1)
    
    assert result is False
    
    # Verify no update was made
    mock_db.users.find_one_and_update.assert_not_called()


@pytest.mark.asyncio
async def test_consume_credits_multiple(credits_service, mock_db):
    """Test consuming multiple credits at once"""
    user_id = "user_123"
    mock_db.users.find_one = AsyncMock(return_value={
        "_id": user_id,
        "credits": 10
    })
    mock_db.users.find_one_and_update = AsyncMock(return_value={
        "_id": user_id,
        "credits": 5  # After consuming 5
    })
    
    result = await credits_service.consume_credits(user_id, 5)
    
    assert result is True
    
    update_call = mock_db.users.find_one_and_update.call_args
    assert update_call[0][1] == {"$inc": {"credits": -5}}


@pytest.mark.asyncio
async def test_get_transactions(credits_service, mock_db):
    """Test getting user's transaction history"""
    user_id = "user_123"
    expected_transactions = [
        {"user_id": user_id, "amount": 10, "type": "purchase"},
        {"user_id": user_id, "amount": -1, "type": "consumption"}
    ]
    
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=expected_transactions)
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_db.billing_transactions.find = MagicMock(return_value=mock_cursor)
    
    transactions = await credits_service.get_transactions(user_id, limit=50)
    
    assert transactions == expected_transactions
    mock_db.billing_transactions.find.assert_called_once_with(
        {"user_id": user_id},
        {"_id": 0}
    )


@pytest.mark.asyncio
async def test_create_checkout_session(credits_service, mock_db):
    """Test creating a checkout session"""
    user_id = "user_123"
    pack_id = "pack_10"
    
    result = await credits_service.create_checkout_session(user_id, pack_id)
    
    assert "checkoutUrl" in result
    assert "sessionId" in result
    assert result["checkoutUrl"].startswith("https://checkout.stripe.com/mock/")
    
    # Verify pending checkout was created
    mock_db.pending_checkouts.insert_one.assert_called_once()
    insert_call = mock_db.pending_checkouts.insert_one.call_args
    checkout = insert_call[0][0]
    assert checkout["user_id"] == user_id
    assert checkout["pack_id"] == pack_id
    assert checkout["credits"] == 10
    assert checkout["amount"] == 5
    assert checkout["status"] == "pending"


@pytest.mark.asyncio
async def test_create_checkout_session_invalid_pack(credits_service, mock_db):
    """Test creating checkout session with invalid pack ID"""
    with pytest.raises(ValueError, match="Invalid pack_id"):
        await credits_service.create_checkout_session("user_123", "invalid_pack")


@pytest.mark.asyncio
async def test_complete_checkout_success(credits_service, mock_db):
    """Test completing a checkout session"""
    session_id = "cs_test_123"
    user_id = "user_123"
    
    mock_db.pending_checkouts.find_one = AsyncMock(return_value={
        "_id": session_id,
        "user_id": user_id,
        "credits": 10,
        "status": "pending"
    })
    mock_db.users.find_one_and_update = AsyncMock(return_value={
        "_id": user_id,
        "credits": 20
    })
    mock_db.pending_checkouts.update_one = AsyncMock()
    
    result = await credits_service.complete_checkout(session_id)
    
    assert result is True
    
    # Verify credits were added
    mock_db.users.find_one_and_update.assert_called_once()
    
    # Verify transaction was logged
    mock_db.billing_transactions.insert_one.assert_called_once()
    
    # Verify session was marked as completed
    mock_db.pending_checkouts.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_complete_checkout_already_completed(credits_service, mock_db):
    """Test completing an already completed checkout"""
    session_id = "cs_test_123"
    
    mock_db.pending_checkouts.find_one = AsyncMock(return_value={
        "_id": session_id,
        "status": "completed"  # Already completed
    })
    
    result = await credits_service.complete_checkout(session_id)
    
    assert result is False
    
    # Verify no credits were added
    mock_db.users.find_one_and_update.assert_not_called()


@pytest.mark.asyncio
async def test_complete_checkout_not_found(credits_service, mock_db):
    """Test completing a non-existent checkout"""
    mock_db.pending_checkouts.find_one = AsyncMock(return_value=None)
    
    result = await credits_service.complete_checkout("nonexistent_session")
    
    assert result is False
