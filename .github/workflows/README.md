# GitHub Actions Workflows

This directory contains automated workflows for the Morra Cinese AI project.

## Available Workflows

### build-executables.yml

**Purpose**: Automatically builds Windows and Linux executables when a new version tag is pushed.

**Trigger**: 
- Push a version tag (e.g., `v1.0`, `v1.1`)
- Manual dispatch from GitHub Actions UI

**What it does**:
1. Builds Windows executable on Windows runner
2. Builds Linux executable on Linux runner  
3. Creates checksums for verification
4. Uploads artifacts (7 day retention)
5. Automatically creates/updates GitHub Release with executables

**How to use**:

```bash
# Create and push a version tag
git tag v1.0
git push origin v1.0

# This will automatically:
# 1. Trigger the workflow
# 2. Build both executables
# 3. Create a GitHub Release
# 4. Attach executables to the release
```

**Manual trigger**:
1. Go to Actions tab in GitHub
2. Select "Build Portable Executables"
3. Click "Run workflow"
4. Choose branch and run

## Setup Requirements

No setup required! The workflow:
- Uses standard GitHub Actions runners
- Installs all dependencies automatically
- Handles both Windows and Linux builds

## Artifacts

After each run, artifacts are available for 7 days:
- `MorraCinese-Windows` - Windows executable
- `MorraCinese-Linux` - Linux executable + tar.gz

## Release Process

For a complete release:

1. Update version in code
2. Update CHANGELOG.md
3. Commit changes
4. Create and push tag:
   ```bash
   git tag -a v1.0 -m "Release version 1.0"
   git push origin v1.0
   ```
5. Workflow automatically:
   - Builds executables
   - Creates GitHub Release
   - Attaches files
6. Edit release notes on GitHub
7. Publish release

## Notes

- Build time: ~10-15 minutes total
- Windows build: ~5-8 minutes
- Linux build: ~4-7 minutes
- Checksums generation: <1 minute
- Free for public repositories
- Requires no secrets/configuration

## Troubleshooting

**Build fails on Windows**:
- Check requirements.txt compatibility
- Verify PyInstaller spec file

**Build fails on Linux**:
- Check system dependencies in workflow
- Verify SDL2 libraries available

**Release not created**:
- Ensure tag format is correct (v*)
- Check repository permissions
- Verify GITHUB_TOKEN has access

## Customization

Edit `build-executables.yml` to:
- Change trigger conditions
- Modify build commands
- Add additional platforms
- Include more files in release
- Change artifact retention

See BUILD_GUIDE.md for more details on the build process.
