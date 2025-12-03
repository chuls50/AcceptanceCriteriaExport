# Azure DevOps Acceptance Criteria Exporter

A Python script to export acceptance criteria from Azure DevOps User Stories to formatted text files.

## Features

- ✅ Exports acceptance criteria from Azure DevOps work items
- ✅ Generates standardized filenames (e.g., `eNr_118556_loading_screen.us.txt`)
- ✅ Secure credential management using environment variables
- ✅ Isolated virtual environment for dependencies
- ✅ Saves all exports to organized `userstories/` folder

## Prerequisites

- **Python 3.8+** installed on your system
- **Git** installed (for version control)
- **Azure DevOps account** with access to the project
- **Personal Access Token (PAT)** with Work Items read permissions

## Setup Instructions

### Step 1: Clone or Navigate to Project

```powershell
cd "c:\Users\CHuls\OneDrive - GlobalMed Holdings, LLC\Desktop\projects\AcceptanceCriteriaExport"
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

Expected output:

```
Successfully installed requests-2.31.0 python-dotenv-1.0.0
```

### Step 4: Create Your Personal Access Token (PAT)

1. **Open Azure DevOps**: https://dev.azure.com/globalmeddev
2. Click your **profile icon** (top right) → **Personal access tokens**
3. Click **+ New Token**
4. Configure:
   - **Name**: `Acceptance Criteria Export Script`
   - **Organization**: `globalmeddev`
   - **Expiration**: 90 days (or custom)
   - **Scopes**: Click "Show all scopes" → Check **Work Items (Read)**
5. Click **Create**
6. **⚠️ IMPORTANT**: Copy the token immediately - you won't see it again!

### Step 5: Configure Environment Variables

1. **Copy the example file**:

   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit `.env` file** and add your credentials:

   ```env
   AZURE_DEVOPS_ORGANIZATION=globalmeddev
   AZURE_DEVOPS_PROJECT=GlobalMed
   AZURE_DEVOPS_PAT=your-actual-token-here
   PRODUCT_PREFIX=eNr
   ```

3. **Save the file** (Ctrl+S)

> **🔒 Security Note**: The `.env` file contains your PAT and is excluded from Git via `.gitignore`. Never commit this file!

## Usage

### Daily Workflow

1. **Activate virtual environment** (if not already active):

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Run the script**:

   ```powershell
   python export-acceptance-criteria.py
   ```

3. **Enter User Story ID** when prompted:

   ```
   Enter User Story ID: 118556
   ```

4. **Press Enter** to accept the default filename, or type a custom one

5. **Done!** The file is saved in `userstories/eNr_118556_loading_screen.us.txt`

### Example Session

```
Azure DevOps Acceptance Criteria Exporter
==================================================

Enter User Story ID: 118556

Fetching work item 118556...
Work Item Type: User Story
Title: eNcounter Refresh: Loading Screen

Default filename: eNr_118556_loading_screen.us.txt
Press Enter to use default, or type a custom filename:

✓ Successfully exported to: userstories/eNr_118556_loading_screen.us.txt
  File size: 532 bytes
```

## Project Structure

```
AcceptanceCriteriaExport/
├── .venv/                      # Virtual environment (not in Git)
├── userstories/                # Exported .us.txt files (not in Git)
├── .env                        # Your credentials (not in Git)
├── .env.example                # Template for .env
├── .gitignore                  # Git ignore rules
├── export-acceptance-criteria.py  # Main script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Troubleshooting

### ❌ "Missing required environment variables"

**Solution**: Check your `.env` file exists and contains all required variables:

```powershell
cat .env
```

### ❌ "Authentication failed"

**Solutions**:

- Verify your PAT is copied correctly (no extra spaces)
- Check the PAT hasn't expired
- Ensure the PAT has Work Items (Read) permissions
- Create a new PAT if needed

### ❌ "python is not recognized"

**Solution**: Python not in PATH

- Reinstall Python and check "Add Python to PATH"
- Or use: `py` instead of `python`

### ❌ "cannot be loaded because running scripts is disabled"

**Solution**: Update PowerShell execution policy

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ "No module named 'requests'" or "'dotenv'"

**Solution**: Activate virtual environment and install dependencies

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ❌ "Work item not found"

**Solutions**:

- Verify the User Story ID exists in Azure DevOps
- Check `ORGANIZATION` and `PROJECT` in `.env` are correct
- Ensure you have access to the work item

## Filename Convention

Generated filenames follow this pattern:

```
{PRODUCT_PREFIX}_{WORK_ITEM_ID}_{title_suffix}.us.txt
```

**Examples**:

- `eNcounter Refresh: Loading Screen` → `eNr_118556_loading_screen.us.txt`
- `eNcounter: Patient Dashboard` → `eNr_123456_patient_dashboard.us.txt`

## Git Workflow

### Initial Commit

```powershell
git add .
git commit -m "Initial project setup with environment variables"
git branch -M main
git push -u origin main
```

### Regular Updates

```powershell
git add export-acceptance-criteria.py README.md
git commit -m "Update script functionality"
git push
```

## Security Best Practices

- ✅ **Never commit `.env`** - it's in `.gitignore`
- ✅ **Use environment variables** for all secrets
- ✅ **Rotate your PAT** regularly (every 90 days)
- ✅ **Use minimal permissions** (only Work Items Read)
- ✅ **Don't share your PAT** with anyone

## Dependencies

- **requests**: HTTP library for Azure DevOps API calls
- **python-dotenv**: Loads environment variables from `.env` file

## License

Internal tool for GlobalMed use.

## Support

For issues or questions, contact the development team.

---

**Last Updated**: December 3, 2025
