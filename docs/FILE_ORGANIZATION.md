# DataWeaver.AI File Organization

## Overview

This document outlines the file organization structure for DataWeaver.AI, ensuring all documentation is properly organized in the `docs/` folder while keeping essential files in the root directory.

## 📁 Root Directory Structure

### **Essential Files (Root Level)**
```
DataWeaver.AI/
├── README.md                    # Main project documentation
├── LICENSE                      # MIT License
├── CHANGELOG.md                 # Version history and changes
├── start.py                     # Unified startup script
├── .gitignore                   # Git ignore rules
├── backend/                     # Backend application
├── frontend/                    # Frontend application
├── scripts/                     # Utility scripts
├── test_data/                   # Test data files
├── venv/                        # Python virtual environment
└── logs/                        # Application logs
```

### **Legacy Files (Removed)**
```
DataWeaver.AI/
├── start.sh                     # ✅ Removed - replaced by start.py
├── start.bat                    # ✅ Removed - replaced by start.py
├── setup.sh                     # ✅ Removed - replaced by start.py
├── check_ports.sh               # ✅ Removed - functionality in start.py
├── CLEANUP_SUMMARY.md           # ✅ Removed - moved to docs/
├── COMPETITIVE_ANALYSIS.md      # ✅ Removed - legacy document
├── IMPLEMENTATION_SUMMARY.md    # ✅ Removed - legacy document
├── LICENSING_STRATEGY.md        # ✅ Removed - legacy document
└── PORT_MANAGEMENT.md           # ✅ Removed - legacy document
```

## 📚 Documentation Structure (`docs/` folder)

### **Release Documentation**
```
docs/
├── RELEASE_NOTES.md             # Release notes for v1.0.0
├── RELEASE_CLEANUP_PLAN.md      # Cleanup planning document
├── RELEASE_CLEANUP_SUMMARY.md   # Cleanup completion summary
└── env.example                  # Environment configuration template
```

### **User Documentation**
```
docs/
├── USER_GUIDE.md                # Comprehensive user guide
├── SETUP.md                     # Installation and setup guide
├── DEPLOYMENT.md                # Production deployment guide
├── API.md                       # API reference documentation
└── SECURITY_CHECKLIST.md        # Security configuration guide
```

### **Technical Documentation**
```
docs/
├── ARCHITECTURE.md              # System architecture overview
├── DATA_CONTROL_FLOW.md         # Data flow documentation
├── DATA_FLOW_DIAGRAM.md         # Visual data flow diagrams
├── END_TO_END_WORKFLOW_SUMMARY.md # Workflow summary
└── SUMMARY.md                   # Technical summary
```

### **API Documentation**
```
docs/
├── openapi.yaml                 # OpenAPI specification
├── openapi.json                 # OpenAPI specification (JSON)
└── OPENAPI_SUMMARY.md           # API documentation summary
```

### **Feature Documentation**
```
docs/
├── DATA_QA_FEATURE.md           # Data Q&A feature documentation
├── DATAWEAVER_CORE_GOALS.md     # Core project goals
├── MERGED_DATA_DISPLAY_DEBUG.md # Debug documentation
├── MERGE_REMERGE_FIX.md         # Merge feature fixes
├── AI_CHAT_SIDEBAR_TOGGLE.md    # AI chat sidebar feature
└── SIDEBAR_TOGGLE.md            # Sidebar toggle functionality
```

## 🔧 Configuration Files

### **Environment Configuration**
- **Location**: `docs/env.example`
- **Purpose**: Template for environment variables
- **Usage**: Copy to root directory as `.env` and configure

### **Startup Configuration**
- **Location**: `start.py` (root directory)
- **Purpose**: Unified startup script for all platforms
- **Features**: 
  - Cross-platform compatibility
  - Automatic dependency installation
  - Database setup
  - Port management
  - Process management

## 📋 File Organization Rules

### **Root Directory**
- **README.md**: Main project documentation (stays in root)
- **LICENSE**: Project license (stays in root)
- **CHANGELOG.md**: Version history and changes (stays in root)
- **start.py**: Unified startup script (stays in root)
- **.gitignore**: Git ignore rules (stays in root)
- **Application code**: `backend/`, `frontend/` directories
- **Utility files**: `scripts/`, `test_data/`, `venv/`, `logs/`

### **Documentation Directory (`docs/`)**
- **All documentation files**: Move to `docs/` folder
- **Configuration templates**: `env.example` in `docs/`
- **API specifications**: OpenAPI files in `docs/`
- **Technical guides**: Architecture, setup, deployment docs
- **Release documentation**: Release notes, cleanup docs (CHANGELOG.md stays in root)

### **Legacy Files**
- **Startup scripts**: `start.sh`, `start.bat`, `setup.sh` (✅ Removed)
- **Port management**: `check_ports.sh`, `PORT_MANAGEMENT.md` (✅ Removed)
- **Legacy summaries**: Various summary documents (✅ Removed)

## 🔄 File References

### **Updated References**
All documentation files have been updated to reference the new file locations:

- **README.md**: References `docs/env.example`
- **Setup guides**: Reference `docs/env.example`
- **Deployment guides**: Reference `docs/env.example`
- **Release documentation**: References updated file paths

### **Cross-References**
- **Backend README**: References `../docs/env.example`
- **Documentation files**: Reference other docs with `docs/` prefix
- **Configuration files**: Reference `docs/env.example`

## 🚀 Benefits of New Organization

### **Cleaner Root Directory**
- **Reduced clutter**: Only essential files in root
- **Better navigation**: Clear separation of concerns
- **Professional appearance**: Organized project structure

### **Centralized Documentation**
- **Single location**: All docs in `docs/` folder
- **Easy maintenance**: Centralized documentation management
- **Better discoverability**: Clear documentation structure

### **Improved Configuration Management**
- **Template location**: `docs/env.example` as configuration template
- **Clear usage**: Copy from docs to root for actual configuration
- **Version control**: Template tracked, actual config ignored

## 📝 Maintenance Guidelines

### **Adding New Documentation**
1. **Create in `docs/`**: All new documentation goes in `docs/` folder
2. **Update references**: Update any cross-references to new files
3. **Update this guide**: Keep this file organization guide current

### **Configuration Changes**
1. **Update template**: Modify `docs/env.example` for new settings
2. **Update documentation**: Update setup and deployment guides
3. **Test references**: Ensure all references point to correct locations

### **Legacy File Cleanup**
1. **Remove unused scripts**: Delete legacy startup scripts
2. **Archive old docs**: Move or remove legacy documentation
3. **Update references**: Remove references to deleted files

## 🎯 Next Steps

### **Immediate Actions**
- [x] Move all documentation to `docs/` folder
- [x] Update all file references
- [x] Create this organization guide
- [x] Remove legacy startup scripts
- [x] Remove legacy documentation files
- [x] Update .gitignore for new structure

### **Future Improvements**
- [ ] Create documentation index in `docs/README.md`
- [ ] Add documentation search functionality
- [ ] Implement automated documentation validation
- [ ] Create documentation templates for new features

---

This file organization ensures a clean, maintainable, and professional project structure that follows best practices for open-source projects.
