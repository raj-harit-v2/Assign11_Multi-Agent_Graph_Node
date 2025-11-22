# Connect Local Repository to Raj_Projects_25 on GitHub

## Current Status

- ✅ Branch `Assign10_Multi-Agent` created locally
- ❌ No remote repository configured
- ❌ Branch not visible in GitHub Desktop (needs remote connection)

## Method 1: Connect via GitHub Desktop (Recommended)

### Step 1: Open GitHub Desktop

1. Open GitHub Desktop from Start Menu
2. If repository is not open:
   - Click **File → Add Local Repository**
   - Browse to: `C:\A1_School_ai_25\001_My_proj_AI\Assign10_Multi-Agent`
   - Click **Add**

### Step 2: Publish Repository to GitHub

1. In GitHub Desktop, click **File → Publish Repository**
2. Or click **"Publish repository"** button (if shown)
3. In the dialog:
   - **Name**: `Assign10_Multi-Agent` (or your preferred name)
   - **Description**: "Session 10 - Multi-Agent Systems and Distributed AI Coordination"
   - **Keep this code private**: Check if you want it private
   - **Organization**: Select "Raj_Projects_25" (if it's an organization)
   - Or select your account if "Raj_Projects_25" is your username

### Step 3: Alternative - Add Existing Remote

If "Raj_Projects_25" repository already exists on GitHub:

1. In GitHub Desktop, click **Repository → Repository Settings**
2. Click **Remote** tab
3. Click **Add Remote**
4. Enter:
   - **Name**: `origin`
   - **URL**: `https://github.com/YOUR_USERNAME/Raj_Projects_25.git`
     - Replace `YOUR_USERNAME` with your GitHub username
   - Or: `git@github.com:YOUR_USERNAME/Raj_Projects_25.git` (SSH)

### Step 4: Push Branch

1. After connecting remote, you'll see **"Publish branch"** button
2. Click it to push `Assign10_Multi-Agent` branch
3. Or use **Branch → Push** from menu

## Method 2: Connect via PowerShell (Command Line)

### Step 1: Add Remote Repository

```powershell
# Navigate to repository
cd C:\A1_School_ai_25\001_My_proj_AI\Assign10_Multi-Agent

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/Raj_Projects_25.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/Raj_Projects_25.git

# Verify remote was added
git remote -v
```

### Step 2: Push Branch to Remote

```powershell
# Push the branch to remote (creates it on GitHub)
git push -u origin Assign10_Multi-Agent

# This will:
# - Create the branch on GitHub
# - Set up tracking between local and remote branch
# - Make it visible in GitHub Desktop
```

### Step 3: Verify in GitHub Desktop

1. Refresh GitHub Desktop (File → Refresh or Ctrl+R)
2. You should now see:
   - Remote: `origin`
   - Branch: `Assign10_Multi-Agent` with remote tracking
   - "Push" or "Pull" options available

## Method 3: Create New Repository on GitHub First

If "Raj_Projects_25" doesn't exist yet:

### Step 1: Create Repository on GitHub

1. Go to https://github.com
2. Click **"+" → New repository**
3. Repository name: `Raj_Projects_25`
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license
6. Click **Create repository**

### Step 2: Connect Local Repository

Use Method 1 or Method 2 above to connect.

## Troubleshooting

### "Repository not found" Error

- Check repository name: `Raj_Projects_25`
- Verify you have access (if it's a private repo)
- Check your GitHub username is correct in the URL

### "Permission denied" Error

- You may need to authenticate
- In GitHub Desktop: File → Options → Accounts
- Add your GitHub account if not already added
- Or use Personal Access Token

### Branch Still Not Visible

1. **Refresh GitHub Desktop**: File → Refresh (Ctrl+R)
2. **Check branch dropdown**: Should show `Assign10_Multi-Agent`
3. **Verify remote**: Repository → Repository Settings → Remote
4. **Pull from remote**: Branch → Pull (to sync)

### Find Your GitHub Username

1. Go to https://github.com
2. Click your profile picture (top right)
3. Your username is in the URL or profile

## Quick Command Reference

```powershell
# Check current remotes
git remote -v

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/Raj_Projects_25.git

# Remove remote (if wrong)
git remote remove origin

# Push branch
git push -u origin Assign10_Multi-Agent

# Check branch status
git branch -vv

# Fetch from remote
git fetch origin

# See all branches (local and remote)
git branch -a
```

## After Connecting

Once connected, you'll see in GitHub Desktop:

- ✅ Remote: `origin` → `https://github.com/.../Raj_Projects_25.git`
- ✅ Branch: `Assign10_Multi-Agent` with remote tracking
- ✅ "Push" button available
- ✅ Branch appears in branch dropdown

## Next Steps After Connection

1. **Commit your changes**:
   - Review files in "Changes" tab
   - Add commit message
   - Commit to `Assign10_Multi-Agent`

2. **Push to GitHub**:
   - Click "Push origin" or "Publish branch"
   - Branch will appear on GitHub

3. **Create Pull Request** (if needed):
   - GitHub Desktop will show "Create Pull Request" button
   - Or go to GitHub website → Pull Requests → New PR

