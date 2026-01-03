"""
Azure Translator Text Application
This script provides an interactive translation service using Azure AI Translator.
It allows users to translate text from any detected language to a target language of their choice.
"""

# Import required libraries
from dotenv import load_dotenv  # For loading environment variables from .env file
import os  # For accessing environment variables

# Import Azure AI Translation SDK namespaces
from azure.core.credentials import AzureKeyCredential  # For authenticating with Azure services
from azure.ai.translation.text import *  # Import all translation client components
from azure.ai.translation.text.models import InputTextItem  # Model for structuring input text


def main():
    """
    Main function that orchestrates the translation workflow:
    1. Loads configuration from environment variables
    2. Initializes the Azure Translator client
    3. Prompts user to select a target language
    4. Continuously translates user input until 'quit' is entered
    """
    try:
        # ===== STEP 1: Load Configuration Settings =====
        # Load environment variables from .env file in the project directory
        load_dotenv()
        
        # Retrieve Azure Translator service credentials from environment variables
        translatorRegion = os.getenv('TRANSLATOR_REGION')  # Azure region (e.g., 'eastus', 'westeurope')
        translatorKey = os.getenv('TRANSLATOR_KEY')  # Azure Translator API key for authentication

        # ===== STEP 2: Initialize Azure Translator Client =====
        # Create authentication credential using the API key
        credential = AzureKeyCredential(translatorKey)
        
        # Initialize the Text Translation client with credentials and region
        # This client will be used for all translation operations
        client = TextTranslationClient(credential=credential, region=translatorRegion)


        # ===== STEP 3: Get Supported Languages and Select Target Language =====
        # Retrieve the list of all languages supported by Azure Translator
        # The 'translation' scope returns only languages available for text translation
        languagesResponse = client.get_supported_languages(scope="translation")
        
        # Display the total number of supported languages to the user
        print("{} languages supported.".format(len(languagesResponse.translation)))
        print("(See https://learn.microsoft.com/azure/ai-services/translator/language-support#translation)")
        print("Enter a target language code for translation (for example, 'en'):")
        
        # Initialize variables for target language selection
        targetLanguage = "xx"  # Placeholder value (will be replaced by user input)
        supportedLanguage = False  # Flag to track whether a valid language was selected
        
        # Loop until the user enters a valid language code
        while supportedLanguage == False:
            targetLanguage = input()  # Get user input for target language code
            
            # Check if the entered language code exists in the supported languages dictionary
            if targetLanguage in languagesResponse.translation.keys():
                supportedLanguage = True  # Valid language found, exit loop
            else:
                # Invalid language code, prompt user to try again
                print("{} is not a supported language.".format(targetLanguage)) 


        # ===== STEP 4: Interactive Translation Loop =====
        # Initialize input variable for user text
        inputText = ""
        
        # Continue translating until the user types 'quit'
        while inputText.lower() != "quit":
            # Prompt user to enter text for translation
            inputText = input("Enter text to translate (or 'quit' to exit): ")
            
            # Only process if the user didn't type 'quit'
            if inputText != "quit":
                # Wrap the input text in an InputTextItem object as required by the API
                # This allows sending multiple text items in batch if needed
                input_text_elements = [InputTextItem(text=inputText)]
                
                # Call the Azure Translator API to translate the text
                # Parameters:
                #   - body: List of text items to translate
                #   - to_language: List of target language codes (can translate to multiple languages at once)
                translationResponse = client.translate(body=input_text_elements, to_language=[targetLanguage])
                
                # Extract the first translation result (we only sent one text item)
                # Handle case where response might be empty
                translation = translationResponse[0] if translationResponse else None
                
                # Process and display the translation result
                if translation:
                    # Get the detected source language (Azure auto-detects the input language)
                    sourceLanguage = translation.detected_language
                    
                    # Iterate through all translations (in case multiple target languages were specified)
                    for translated_text in translation.translations:
                        # Display the original text, source language, target language, and translated result
                        print(f"'{inputText}' was translated from {sourceLanguage.language} to {translated_text.to} as '{translated_text.text}'.")




    except Exception as ex:
        # Catch and display any errors that occur during execution
        # This includes API errors, network issues, or invalid configurations
        print(ex)


# Entry point of the script
# This ensures main() only runs when the script is executed directly (not when imported as a module)
if __name__ == "__main__":
    main()