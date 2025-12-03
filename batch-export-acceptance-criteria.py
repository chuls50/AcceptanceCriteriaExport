import requests
from requests.auth import HTTPBasicAuth
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration - loaded from .env file
ORGANIZATION = os.getenv("AZURE_DEVOPS_ORGANIZATION")
PROJECT = os.getenv("AZURE_DEVOPS_PROJECT")
PAT = os.getenv("AZURE_DEVOPS_PAT")
PRODUCT_PREFIX = os.getenv("PRODUCT_PREFIX", "eNr")  # Default to "eNr" if not set

# Output directory for exported files
OUTPUT_DIR = "userstories"

def sanitize_filename(text):
    """Convert text to lowercase and replace spaces/special chars with underscores"""
    # Remove special characters and replace spaces with underscores
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s]+', '_', text)
    return text.lower().strip('_')

def extract_title_suffix(title):
    """Extract the part after the colon in the title
    Example: 'eNcounter Refresh: Loading Screen' -> 'loading_screen'
    """
    if ':' in title:
        # Get everything after the colon and strip whitespace
        suffix = title.split(':', 1)[1].strip()
    else:
        # If no colon, use the whole title
        suffix = title
    
    return sanitize_filename(suffix)

def get_work_item(work_item_id):
    """Fetch work item details from Azure DevOps API"""
    url = f"https://dev.azure.com/{ORGANIZATION}/{PROJECT}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth('', PAT)
    )
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        print("Error: Authentication failed. Check your PAT.")
        return None
    elif response.status_code == 404:
        print(f"Error: Work item {work_item_id} not found.")
        return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def extract_acceptance_criteria(work_item):
    """Extract acceptance criteria from work item fields"""
    fields = work_item.get('fields', {})
    
    # Get the dedicated Acceptance Criteria field
    acceptance_criteria = fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')
    
    if not acceptance_criteria:
        return ""
    
    # Convert HTML line breaks to newlines before removing tags
    acceptance_criteria = acceptance_criteria.replace('<br>', '\n')
    acceptance_criteria = acceptance_criteria.replace('<br/>', '\n')
    acceptance_criteria = acceptance_criteria.replace('<br />', '\n')
    acceptance_criteria = acceptance_criteria.replace('</p>', '\n')
    acceptance_criteria = acceptance_criteria.replace('</div>', '\n')
    
    # Remove remaining HTML tags
    acceptance_criteria = re.sub(r'<[^>]+>', '', acceptance_criteria)
    
    # Decode HTML entities
    acceptance_criteria = acceptance_criteria.replace('&nbsp;', ' ')
    acceptance_criteria = acceptance_criteria.replace('&lt;', '<')
    acceptance_criteria = acceptance_criteria.replace('&gt;', '>')
    acceptance_criteria = acceptance_criteria.replace('&amp;', '&')
    acceptance_criteria = acceptance_criteria.replace('&quot;', '"')
    
    # Clean up initial whitespace and excessive blank lines
    acceptance_criteria = re.sub(r'\n\s*\n', '\n', acceptance_criteria)
    acceptance_criteria = acceptance_criteria.strip()
    
    # Ensure Given, When, Then each start on their own line
    acceptance_criteria = re.sub(r'(\s+)(Given )', r'\n\2', acceptance_criteria)
    acceptance_criteria = re.sub(r'(\s+)(When )', r'\n\2', acceptance_criteria)
    acceptance_criteria = re.sub(r'(\s+)(Then )', r'\n\2', acceptance_criteria)
    
    # Add single blank line before each Scenario (except the first)
    lines = acceptance_criteria.split('\n')
    formatted_lines = []
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('Scenario ') and i > 0:
            formatted_lines.append('')  # Add one blank line
        if line:  # Only add non-empty lines
            formatted_lines.append(line)
    
    acceptance_criteria = '\n'.join(formatted_lines)
    
    return acceptance_criteria

def generate_filename(work_item_id, work_item_title, product_prefix):
    """Generate filename following the specified convention
    Example: eNr_118556_loading_screen.us.txt
    """
    # Extract the part after the colon
    title_suffix = extract_title_suffix(work_item_title)
    filename = f"{product_prefix}_{work_item_id}_{title_suffix}.us.txt"
    return filename

def export_single_story(work_item_id):
    """Export a single user story to a file with default filename
    
    Args:
        work_item_id: The ID of the work item to export
    
    Returns:
        dict with 'success' (bool), 'filename' (str), and 'error' (str) keys
    """
    work_item = get_work_item(work_item_id)
    
    if not work_item:
        return {'success': False, 'filename': None, 'error': 'Failed to fetch work item'}
    
    # Extract fields
    fields = work_item.get('fields', {})
    work_item_title = fields.get('System.Title', 'untitled')
    work_item_type = fields.get('System.WorkItemType', 'Unknown')
    
    # Extract acceptance criteria
    acceptance_criteria = extract_acceptance_criteria(work_item)
    
    # Generate filename
    filename = generate_filename(work_item_id, work_item_title, PRODUCT_PREFIX)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Save to file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"User Story ID: {work_item_id}\n")
            f.write(f"Title: {work_item_title}\n")
            f.write(f"Type: {work_item_type}\n")
            f.write("=" * 50 + "\n\n")
            f.write("ACCEPTANCE CRITERIA:\n\n")
            f.write(acceptance_criteria if acceptance_criteria else "(No acceptance criteria found)")
        
        return {
            'success': True, 
            'filename': filename, 
            'title': work_item_title,
            'has_criteria': bool(acceptance_criteria)
        }
        
    except Exception as e:
        return {'success': False, 'filename': filename, 'error': str(e)}

def batch_export(work_item_ids):
    """Export multiple user stories using default filenames
    
    Args:
        work_item_ids: List of work item IDs to export
    """
    print(f"\n{'='*70}")
    print(f"BATCH EXPORT MODE - Processing {len(work_item_ids)} user stories")
    print(f"{'='*70}")
    
    results = {
        'successful': [],
        'failed': [],
        'no_criteria': []
    }
    
    for i, work_item_id in enumerate(work_item_ids, 1):
        print(f"\n[{i}/{len(work_item_ids)}] Processing ID: {work_item_id}...")
        
        result = export_single_story(work_item_id)
        
        if result['success']:
            print(f"  ✓ Exported: {result['filename']}")
            if result.get('title'):
                print(f"    {result['title'][:60]}{'...' if len(result['title']) > 60 else ''}")
            
            if not result.get('has_criteria'):
                print(f"    ⚠️  No acceptance criteria found")
                results['no_criteria'].append(work_item_id)
            
            results['successful'].append({
                'id': work_item_id,
                'filename': result['filename']
            })
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
            results['failed'].append({
                'id': work_item_id,
                'error': result.get('error', 'Unknown error')
            })
    
    # Summary
    print(f"\n{'='*70}")
    print(f"BATCH EXPORT COMPLETE")
    print(f"{'='*70}")
    print(f"✓ Successfully exported: {len(results['successful'])}")
    
    if results['no_criteria']:
        print(f"⚠️  Missing acceptance criteria: {len(results['no_criteria'])}")
        print(f"   IDs: {', '.join(results['no_criteria'])}")
    
    if results['failed']:
        print(f"❌ Failed: {len(results['failed'])}")
        for item in results['failed']:
            print(f"   ID {item['id']}: {item['error']}")
    
    print(f"\nAll files saved to: {OUTPUT_DIR}/")
    
    return results

def main():
    print("Azure DevOps Batch Acceptance Criteria Exporter")
    print("=" * 70)
    
    # Validate environment variables
    if not all([ORGANIZATION, PROJECT, PAT]):
        print("\n❌ ERROR: Missing required environment variables!")
        print("Please ensure your .env file contains:")
        print("  - AZURE_DEVOPS_ORGANIZATION")
        print("  - AZURE_DEVOPS_PROJECT")
        print("  - AZURE_DEVOPS_PAT")
        print("\nSee .env.example for reference.")
        return
    
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"\n✓ Created output directory: {OUTPUT_DIR}/")
    
    print("\nEnter user story IDs in one of these formats:")
    print("  • Comma-separated: 118556, 118558, 118559")
    print("  • Space-separated: 118556 118558 118559")
    print("  • Range: 118556-118560 (exports IDs 118556 through 118560)")
    print("  • Mixed: 118556, 118558-118560, 118562")
    
    ids_input = input("\nEnter user story IDs: ").strip()
    
    if not ids_input:
        print("❌ No input provided.")
        return
    
    # Parse input
    work_item_ids = []
    parts = ids_input.replace(',', ' ').split()
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Handle range (e.g., 118556-118560)
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                work_item_ids.extend([str(i) for i in range(start, end + 1)])
            except ValueError:
                print(f"  ⚠️  Skipping invalid range: {part}")
        elif part.isdigit():
            work_item_ids.append(part)
        else:
            print(f"  ⚠️  Skipping invalid ID: {part}")
    
    if not work_item_ids:
        print("\n❌ No valid user story IDs provided.")
        return
    
    # Remove duplicates while preserving order
    seen = set()
    work_item_ids = [x for x in work_item_ids if not (x in seen or seen.add(x))]
    
    print(f"\n✓ Found {len(work_item_ids)} user story ID(s) to process")
    print(f"  IDs: {', '.join(work_item_ids[:10])}{'...' if len(work_item_ids) > 10 else ''}")
    
    confirm = input("\nProceed with batch export? (y/n): ").strip().lower()
    
    if confirm == 'y':
        batch_export(work_item_ids)
    else:
        print("Batch export cancelled.")

if __name__ == "__main__":
    main()
