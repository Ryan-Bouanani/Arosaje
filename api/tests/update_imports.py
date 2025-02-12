import os
import re

def update_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remplacer les imports
    replacements = {
        'ext_functions:verify_photo_list': 'validators.photo_validators:verify_photo_list',
        'misc:validate_photo_response': 'validators.photo_validators:validate_photo_response',
        'misc:validate_care_response': 'validators.care_validators:validate_care_response',
        'misc:validate_message_response': 'validators.message_validators:validate_message_response',
        'misc:validate_messages_list_response': 'validators.message_validators:validate_messages_list_response',
        'misc:validate_unread_count_response': 'validators.message_validators:validate_unread_count_response',
        'misc:validate_conversation_response': 'validators.conversation_validators:validate_conversation_response',
        'misc:validate_advice_response': 'validators.advice_validators:validate_advice_response'
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    with open(file_path, 'w') as f:
        f.write(content)

def main():
    workflow_dir = 'api/tests/workflows'
    for file in os.listdir(workflow_dir):
        if file.endswith('.tavern.yaml'):
            file_path = os.path.join(workflow_dir, file)
            update_file(file_path)
            print(f"Updated {file}")

if __name__ == '__main__':
    main() 