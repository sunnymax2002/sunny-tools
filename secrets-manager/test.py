from core import FamilySecretsManager, DecryptedSecretPayload

if __name__ == "__main__":
    manager = FamilySecretsManager("./family_vault")

    # ----------------------------------------------------
    # SCENARIO: Setup structured items for multiple family members
    # ----------------------------------------------------
    
    # Dad setup
    dad_netflix = DecryptedSecretPayload(
        url_or_app="netflix.com",
        category="Entertainment",
        payload={"email": "dad@family.com", "password": "DadPassword55!"},
        hint_value="555-0199"  # Dad's phone number
    )
    manager.save_secret("Dad", "Netflix", "SuperSecretDadKey", dad_netflix, "Dad's Phone Number")

    # Alice setup (Same service, different user account & different secret hint)
    alice_netflix = DecryptedSecretPayload(
        url_or_app="netflix.com/profile",
        category="Entertainment",
        payload={"email": "alice_cool@gmail.com", "password": "AliceSecret99#"},
        hint_value="Green"  # Alice's favorite color
    )
    manager.save_secret("Alice", "Netflix", "AliceMasterPass", alice_netflix, "Your favorite color")

    # ----------------------------------------------------
    # TEST 1: Request Dynamic Menu for Alice
    # ----------------------------------------------------
    print("\n--- FETCHING DYNAMIC MENU FOR ALICE ---")
    alice_menu = manager.get_dynamic_menu("Alice")
    print(f"Alice's Menu: {alice_menu}")

    # ----------------------------------------------------
    # TEST 2: Decrypting Credentials Successfully
    # ----------------------------------------------------
    print("\n--- ATTEMPTING DECRYPTION FOR DAD'S NETFLIX ---")
    # Providing exact Master Key and exact phone Hint
    secret_data = manager.decrypt_secret(
        user="Dad", 
        service_name="Netflix", 
        master_key="SuperSecretDadKey", 
        hint_value="555-0199"
    )
    print(f"[Result] Decrypted Credentials safely extracted: {secret_data}")

    # ----------------------------------------------------
    # TEST 3: Attempting Decryption with an invalid Hint
    # ----------------------------------------------------
    print("\n--- ATTEMPTING DECRYPTION WITH BAD HINT ---")
    failed_data = manager.decrypt_secret(
        user="Dad", 
        service_name="Netflix", 
        master_key="SuperSecretDadKey", 
        hint_value="WrongHint123"
    )