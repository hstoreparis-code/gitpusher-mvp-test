from typing import Dict
from datetime import datetime, timezone
import uuid

class CreditsService:
    def __init__(self, db):
        self.db = db
        self.PACKS = {
            "pack_10": {"credits": 10, "price": 5, "currency": "EUR"},
            "pack_50": {"credits": 50, "price": 20, "currency": "EUR"},
            "pack_100": {"credits": 100, "price": 35, "currency": "EUR"},
        }
    
    async def get_user_credits(self, user_id: str) -> int:
        """Get user's current credit balance."""
        user = await self.db.users.find_one({"_id": user_id})
        return user.get("credits", 0) if user else 0
    
    async def add_credits(self, user_id: str, amount: int, transaction_type: str = "purchase") -> Dict:
        """Add credits to user account."""
        now = datetime.now(timezone.utc).isoformat()
        
        # Update user credits
        result = await self.db.users.find_one_and_update(
            {"_id": user_id},
            {"$inc": {"credits": amount}},
            return_document=True
        )
        
        # Log transaction
        transaction = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "amount": amount,
            "type": transaction_type,
            "credits": result.get("credits", 0),
            "created_at": now
        }
        await self.db.billing_transactions.insert_one(transaction)
        
        return transaction
    
    async def consume_credits(self, user_id: str, amount: int = 1) -> bool:
        """Consume credits for an operation. Returns True if successful."""
        user = await self.db.users.find_one({"_id": user_id})
        current_credits = user.get("credits", 0) if user else 0
        
        if current_credits < amount:
            return False
        
        # Deduct credits
        await self.add_credits(user_id, -amount, transaction_type="consumption")
        return True
    
    async def get_transactions(self, user_id: str, limit: int = 50) -> list:
        """Get user's billing transactions."""
        transactions = await self.db.billing_transactions.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        return transactions
    
    async def create_checkout_session(self, user_id: str, pack_id: str) -> Dict:
        """Create a mock Stripe checkout session."""
        if pack_id not in self.PACKS:
            raise ValueError(f"Invalid pack_id: {pack_id}")
        
        pack = self.PACKS[pack_id]
        session_id = f"cs_mock_{uuid.uuid4().hex[:16]}"
        
        # In real implementation, this would call Stripe API
        # For MVP, we'll just return a mock URL
        checkout_url = f"https://checkout.stripe.com/mock/{session_id}"
        
        # Store pending transaction
        await self.db.pending_checkouts.insert_one({
            "_id": session_id,
            "user_id": user_id,
            "pack_id": pack_id,
            "credits": pack["credits"],
            "amount": pack["price"],
            "currency": pack["currency"],
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "checkoutUrl": checkout_url,
            "sessionId": session_id
        }
    
    async def complete_checkout(self, session_id: str) -> bool:
        """Complete a checkout session (called by webhook or mock)."""
        session = await self.db.pending_checkouts.find_one({"_id": session_id})
        if not session or session.get("status") != "pending":
            return False
        
        # Add credits to user
        await self.add_credits(
            session["user_id"],
            session["credits"],
            transaction_type="purchase"
        )
        
        # Mark session as completed
        await self.db.pending_checkouts.update_one(
            {"_id": session_id},
            {"$set": {"status": "completed"}}
        )
        
        return True
