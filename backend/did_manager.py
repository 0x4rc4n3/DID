# backend/did_manager.py
import uuid
import datetime
from pqc_utils import PQCrypto
from blockchain import Blockchain
from db import Database

class DIDManager:
    def __init__(self):
        self.pqc = PQCrypto()
        self.blockchain = Blockchain()
        self.db = Database()
        self.load_blockchain_from_db()
    
    def load_blockchain_from_db(self):
        """Load existing blockchain from database"""
        stored_blocks = self.db.get_blockchain()
        if len(stored_blocks) > 1:  # More than genesis block
            self.blockchain.chain = []
            for block_data in stored_blocks:
                from blockchain import Block
                block = Block(
                    block_data['index'],
                    block_data['data'],
                    block_data['previous_hash']
                )
                block.timestamp = block_data['timestamp']
                block.hash = block_data['hash']
                self.blockchain.chain.append(block)
    
    def create_did(self, user_info):
        """Create new DID with PQC key pair"""
        # Generate unique DID
        did_id = str(uuid.uuid4())
        did = f"did:pqc:{did_id}"
        
        # Check if DID already exists
        if self.db.did_exists(did):
            raise ValueError("DID already exists")
        
        # Generate PQC key pair
        keys = self.pqc.generate_key_pair()
        
        # Create DID document
        did_document = {
            "id": did,
            "created": datetime.datetime.now().isoformat(),
            "updated": datetime.datetime.now().isoformat(),
            "publicKey": [{
                "id": f"{did}#keys-1",
                "type": "MLDSAVerificationKey2024",
                "controller": did,
                "publicKeyBase64": keys['public_key']
            }],
            "authentication": [f"{did}#keys-1"],
            "service": [],
            "userInfo": user_info
        }
        
        # Save DID document to database
        self.db.save_did_document(did, did_document)
        
        # Add to blockchain
        block_data = {
            "type": "DID_CREATION",
            "did": did,
            "public_key": keys['public_key'],
            "user_info": user_info
        }
        
        new_block = self.blockchain.add_block(block_data)
        self.db.save_block(new_block.to_dict())
        
        return {
            "did": did,
            "document": did_document,
            "private_key": keys['private_key'],
            "public_key": keys['public_key']
        }
    
    def get_did_document(self, did):
        """Retrieve DID document"""
        return self.db.get_did_document(did)
    
    def authenticate_challenge(self, did, challenge, signature):
        """Authenticate user by verifying signed challenge"""
        did_doc = self.get_did_document(did)
        if not did_doc:
            return False
        
        public_key = did_doc['publicKey'][0]['publicKeyBase64']
        return self.pqc.verify_signature(challenge, signature, public_key)
    
    def sign_challenge(self, challenge, private_key):
        """Sign challenge with private key"""
        return self.pqc.sign_message(challenge, private_key)
    
    def get_blockchain_info(self):
        """Get blockchain information"""
        return {
            "chain_length": len(self.blockchain.chain),
            "is_valid": self.blockchain.is_chain_valid(),
            "latest_block": self.blockchain.get_latest_block().to_dict(),
            "full_chain": self.blockchain.get_chain()
        }