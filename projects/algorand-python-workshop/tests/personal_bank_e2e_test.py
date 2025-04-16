import pytest
from algokit_utils import (
    AlgoAmount,
    AlgorandClient,
    CommonAppCallParams,
    PaymentParams,
    SendParams,
    SigningAccount,
)

from smart_contracts.artifacts.personal_bank.personal_bank_client import (
    DepositArgs,
    PersonalBankClient,
    PersonalBankFactory,
)


@pytest.fixture(scope="session")
def deployer(algorand_client: AlgorandClient) -> SigningAccount:
    account = algorand_client.account.from_environment("DEPLOYER")
    algorand_client.account.ensure_funded_from_environment(
        account_to_fund=account.address, min_spending_balance=AlgoAmount.from_algo(10)
    )
    return account


@pytest.fixture(scope="session")
def depositor(algorand_client: AlgorandClient) -> SigningAccount:
    account = algorand_client.account.from_environment("DEPOSITOR")
    algorand_client.account.ensure_funded_from_environment(
        account_to_fund=account.address, min_spending_balance=AlgoAmount.from_algo(10)
    )
    return account


@pytest.fixture(scope="session")
def personal_bank_client(
    algorand_client: AlgorandClient, deployer: SigningAccount
) -> PersonalBankClient:
    factory = algorand_client.client.get_typed_app_factory(
        PersonalBankFactory, default_sender=deployer.address
    )

    client, _ = factory.send.create.bare()

    dispenser = algorand_client.account.localnet_dispenser()
    algorand_client.account.ensure_funded(
        account_to_fund=client.app_address,
        min_spending_balance=AlgoAmount.from_algo(1),
        dispenser_account=dispenser,
    )
    return client


def test_deposit(
    algorand_client: AlgorandClient,
    depositor: SigningAccount,
    personal_bank_client: PersonalBankClient,
) -> None:
    pay_txn = algorand_client.create_transaction.payment(
        PaymentParams(
            sender=depositor.address,
            receiver=personal_bank_client.app_address,
            amount=AlgoAmount(algo=1),
        )
    )
    result = personal_bank_client.send.deposit(
        args=(DepositArgs(pay_txn=pay_txn)),
        params=CommonAppCallParams(
            sender=depositor.address, extra_fee=AlgoAmount(micro_algo=1000)
        ),
    )
    assert result.abi_return == 1000000


def test_withdraw(
    depositor: SigningAccount, personal_bank_client: PersonalBankClient
) -> None:
    print("test_withdraw")
    result = personal_bank_client.send.withdraw(
        params=CommonAppCallParams(
            sender=depositor.address,
            max_fee=AlgoAmount(micro_algo=3000),
        ),
        send_params=SendParams(cover_app_call_inner_transaction_fees=True),
    )
    print("result", result)
    assert result.abi_return == 1000000
