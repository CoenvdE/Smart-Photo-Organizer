"""
Utility functions for Google Drive operations
"""

def select_folder(drive_connector):
    """
    Interactive folder selection from user's Google Drive
    
    Args:
        drive_connector: DriveConnector instance
        
    Returns:
        str: Selected folder ID or None if cancelled
    """
    folders = drive_connector.list_folders()
    
    if not folders:
        print("No folders found in your Google Drive.")
        return None
    
    print("\nAvailable folders:")
    print("-" * 40)
    for i, folder in enumerate(folders, 1):
        print(f"{i}. {folder['name']}")
    print("-" * 40)
    
    try:
        choice = int(input("Select a folder number (or 0 to cancel): "))
        
        if choice == 0:
            return None
        
        if 1 <= choice <= len(folders):
            selected_folder = folders[choice - 1]
            print(f"Selected folder: {selected_folder['name']}")
            return selected_folder['id']
        else:
            print("Invalid choice.")
            return None
            
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None

def create_output_folder(drive_connector, folder_name):
    """
    Create output folder for processed images
    
    Args:
        drive_connector: DriveConnector instance
        folder_name (str): Name for the output folder
        
    Returns:
        str: Created folder ID
    """
    # Check if folder exists
    folders = drive_connector.list_folders()
    for folder in folders:
        if folder['name'] == folder_name:
            print(f"Folder '{folder_name}' already exists. Using existing folder.")
            return folder['id']
    
    # Create new folder
    print(f"Creating output folder '{folder_name}'...")
    folder_id = drive_connector.create_folder(folder_name)
    print(f"Folder created successfully.")
    
    return folder_id 