import boto3
import uuid
import re

from ewallet.repository.base_repository import BaseRepository
from ewallet.model.wallet import Wallet

class DynamoDbWalletRepository(BaseRepository):
    """
    Concrete class for that implements the Repository interface.
    This class is responsible to handle Wallet objects
    interacting with the DynamoDB database.
    """

    def __init__(self, dynamodb_client: boto3.client, wallet_table_name: str):
        self.dynamodb_client = dynamodb_client
        self.wallet_table_name = wallet_table_name
    
    def _validate_wallet_name(self, name: str) -> None:
        """Validates wallet name input."""
        if not name or not isinstance(name, str):
            raise ValueError("Wallet name must be a non-empty string")
        if len(name.strip()) == 0:
            raise ValueError("Wallet name cannot be empty or whitespace only")
        if len(name) > 100:
            raise ValueError("Wallet name cannot exceed 100 characters")
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
            raise ValueError("Wallet name contains invalid characters")
    
    def _validate_wallet_id(self, wallet_id: str) -> None:
        """Validates wallet ID input."""
        if not wallet_id or not isinstance(wallet_id, str):
            raise ValueError("Wallet ID must be a non-empty string")
        if len(wallet_id.strip()) == 0:
            raise ValueError("Wallet ID cannot be empty or whitespace only")
        # UUID format validation
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, wallet_id.lower()):
            raise ValueError("Wallet ID must be a valid UUID format")

    def list_wallets(self) -> list[Wallet]:
        """
        Lists all wallets from the DynamoDB database.

        :return: A list of all wallets.
        :rtype: list[Wallet]
        """
        response = self.dynamodb_client.scan(
            TableName=self.wallet_table_name
        )

        items = response.get('Items')

        if items is None:
            return []

        return [Wallet(item.get('name').get('S')) for item in items]

    def save(self, wallet: Wallet) -> str:
        """
        Saves a wallet to the DynamoDB database.

        :param wallet: The wallet to save.
        :return: The id of the saved wallet.
        :rtype: str
        """
        if wallet is None:
            raise ValueError("Wallet cannot be None")
        
        self._validate_wallet_name(wallet.name)
        
        wallet.id = str(uuid.uuid4())

        self.dynamodb_client.put_item(
            TableName=self.wallet_table_name,
            Item={
                'id': {'S': wallet.id},
                'name': {'S': wallet.name.strip()}
            }
        )

        return wallet.id
    
    def find(self, id: str) -> Wallet:
        """
        Finds a wallet by id.

        :param str id: The id of the wallet to find.
        :return: The wallet found.
        :rtype: Wallet
        """
        self._validate_wallet_id(id)
        
        response = self.dynamodb_client.get_item(
            TableName=self.wallet_table_name,
            Key={
                'id': {'S': id.strip()}
            }
        )

        item = response.get('Item')

        if item is None:
            return None
        
        wallet = Wallet(item.get('name').get('S'))
        wallet.id = item.get('id').get('S')

        return wallet
    