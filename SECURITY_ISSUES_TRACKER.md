# 🔒 Security Issues Tracker

**Last Updated:** February 5, 2026  
**Total Issues:** 26  
**Status:** 🔴 In Progress

---

## ✅ Quick Status Overview

| Phase | Status | Issues | Completed | Progress |
|-------|--------|--------|-----------|----------|
| Phase 1: Critical Security | 🔴 Not Started | 8 | 0 | 0% |
| Phase 2: High Priority | 🔴 Not Started | 8 | 0 | 0% |
| Phase 3: Production Hardening | 🔴 Not Started | 8 | 0 | 0% |
| Phase 4: Testing & QA | 🔴 Not Started | 8 | 0 | 0% |

---

## 🚨 Phase 1: Critical Security Fixes (P0)

**Deadline:** Week 1  
**Estimated Effort:** 2-3 days

- [ ] **Issue #1** - Fix path traversal in `tools/file_manager_mcp/run.py:49, 90, 156`
  - Severity: CRITICAL
  - CVSS: 9.1
  - Files: `tools/file_manager_mcp/run.py`
  - Line: 49, 90, 156-165

- [ ] **Issue #2** - Change MCP services to bind to 127.0.0.1
  - Severity: CRITICAL
  - CVSS: 8.8
  - Files: `tools/file_manager_mcp/run.py:199`, `tools/markdownify_mcp/run.py:43`

- [ ] **Issue #3** - Add non-root user to Dockerfile
  - Severity: HIGH
  - CVSS: 7.5
  - Files: `Dockerfile`

- [ ] **Issue #4** - Create .dockerignore file
  - Severity: HIGH
  - CVSS: 7.5
  - Files: Create new file at root

- [ ] **Issue #5** - Add missing dependencies (fastapi, uvicorn, markdownify)
  - Severity: HIGH
  - Files: `requirements.txt`

- [ ] **Issue #6** - Add input validation and sanitization
  - Severity: HIGH
  - CVSS: 7.3
  - Files: `app.py:269-283`, `tools/file_manager_mcp/run.py:26`

- [ ] **Issue #7** - Implement ZIP bomb protection
  - Severity: HIGH
  - CVSS: 6.5
  - Files: `tools/file_manager_mcp/run.py:71-73`

- [ ] **Issue #8** - Add user_settings.json to .gitignore
  - Severity: MEDIUM
  - Files: `.gitignore`

---

## ⚠️ Phase 2: High Priority Reliability (P1)

**Deadline:** Week 2  
**Estimated Effort:** 3-4 days

- [ ] **Issue #9** - Fix thread safety in GenerationStateManager
  - Severity: HIGH
  - Files: `src/generation_state.py:28-134`

- [ ] **Issue #10** - Remove global state mutation in app.py
  - Severity: MEDIUM
  - Files: `app.py:266-267, 392-407`

- [ ] **Issue #11** - Add request timeouts (120s for API calls)
  - Severity: MEDIUM
  - Files: `src/ai_models.py:68-99`

- [ ] **Issue #12** - Implement rate limiting (2 concurrent generations)
  - Severity: MEDIUM
  - Files: `app.py:315-374`

- [ ] **Issue #13** - Make URLs/ports configurable via environment
  - Severity: MEDIUM
  - Files: `app.py:296, 667, 686`

- [ ] **Issue #14** - Add health checks to Dockerfile
  - Severity: MEDIUM
  - Files: `Dockerfile`

- [ ] **Issue #15** - Implement proper error recovery in workflow
  - Severity: HIGH
  - Files: `src/workflow.py:90-255`

- [ ] **Issue #16** - Add comprehensive logging
  - Severity: MEDIUM
  - Files: All MCP tool files, workflow

---

## 🔧 Phase 3: Production Hardening (P2)

**Deadline:** Week 3  
**Estimated Effort:** 4-5 days

- [ ] **Issue #17** - Implement multi-stage Docker build
  - Files: `Dockerfile`

- [ ] **Issue #18** - Add dependency injection for agents
  - Files: `src/workflow.py:112-215`

- [ ] **Issue #19** - Pin all dependency versions
  - Files: `requirements.txt`

- [ ] **Issue #20** - Add Prometheus metrics
  - Files: `app.py`, create new metrics module

- [ ] **Issue #21** - Implement keyring for API key storage
  - Files: `src/settings.py`

- [ ] **Issue #22** - Create production deployment guide
  - Files: Create `DEPLOYMENT.md`

- [ ] **Issue #23** - Add Docker Compose file
  - Files: Create `docker-compose.yml`

- [ ] **Issue #24** - Set up CI/CD with security scanning
  - Files: Create `.github/workflows/security.yml`

---

## 🧪 Phase 4: Testing & Documentation (P3)

**Deadline:** Week 4  
**Estimated Effort:** 5-7 days

- [ ] **Issue #25** - Add pytest test suite
  - Files: Create `tests/` directory

- [ ] **Issue #26** - Add integration tests for workflow
  - Files: `tests/test_workflow.py`

- [ ] **Issue #27** - Load testing (100 concurrent users)
  - Files: Create `tests/load_test.py`

- [ ] **Issue #28** - Security audit (penetration testing)
  - External: Hire security consultant or use automated tools

- [ ] **Issue #29** - Accessibility audit (WCAG 2.1 AA)
  - Files: UI components in `app.py`, `src/editor_page.py`

- [ ] **Issue #30** - Create security documentation
  - Files: Add section to `README.md`

- [ ] **Issue #31** - Update README with deployment instructions
  - Files: `README.md`

- [ ] **Issue #32** - Create incident response runbook
  - Files: Create `RUNBOOK.md`

---

## 🎯 Quick Wins (Do First!)

These can be done in ~40 minutes:

1. ✅ **Create .dockerignore** (5 min)
   ```bash
   # Run this:
   touch .dockerignore
   # Then copy content from SECURITY_REVIEW_FINDINGS.md
   ```

2. ✅ **Add user_settings.json to .gitignore** (1 min)
   ```bash
   echo "user_settings.json" >> .gitignore
   ```

3. ✅ **Pin dependencies in requirements.txt** (10 min)
   ```bash
   pip freeze > requirements-lock.txt
   # Then manually update requirements.txt with versions
   ```

4. ✅ **Change MCP host to 127.0.0.1** (2 min)
   - Edit `tools/file_manager_mcp/run.py:199`
   - Edit `tools/markdownify_mcp/run.py:43`
   - Change `host="0.0.0.0"` to `host="127.0.0.1"`

5. ✅ **Add missing dependencies** (5 min)
   ```bash
   # Add to requirements.txt:
   fastapi>=0.104.0
   uvicorn[standard]>=0.24.0
   markdownify>=0.11.6
   ```

6. ✅ **Add input length validation** (15 min)
   - Edit `app.py` around line 269
   - Add max length check (5000 chars)

---

## 📊 Progress Tracking

### Overall Progress: 0/32 (0%)

### By Severity:
- **Critical:** 0/2 (0%)
- **High:** 0/9 (0%)
- **Medium:** 0/13 (0%)
- **Low:** 0/8 (0%)

### By Category:
- **Security:** 0/11 (0%)
- **Architecture:** 0/6 (0%)
- **Deployment:** 0/5 (0%)
- **UI/UX:** 0/4 (0%)
- **Testing:** 0/6 (0%)

---

## 📝 Notes & Context

### Review Methodology:
- 4 specialized critic agents ran in parallel
- Each agent focused on specific domain (Architecture, UI, Tools/MCP, Deployment)
- Review duration: ~15 minutes
- Files analyzed: 25+ source files

### Risk Assessment:
- **Before Fixes:** HIGH RISK (confidentiality, integrity, availability)
- **After Phase 1:** MEDIUM RISK
- **After Phase 2:** LOW RISK
- **After All Phases:** PRODUCTION READY ✅

### Deployment Readiness:
- **Current Score:** 6/10
- **Target Score:** 9/10
- **Blockers:** Phase 1 and Phase 2 must be complete

---

## 🔗 Related Files

- **Full Review:** `SECURITY_REVIEW_FINDINGS.md`
- **Repository Guidelines:** `AGENTS.md`
- **Current .gitignore:** `.gitignore`
- **Docker Config:** `Dockerfile`
- **Dependencies:** `requirements.txt`

---

## ✏️ How to Use This Tracker

1. **Start with Quick Wins** - Get easy wins first
2. **Work Through Phases Sequentially** - Don't skip Phase 1
3. **Check Off Items** - Change `[ ]` to `[x]` when complete
4. **Update Progress** - Recalculate percentages after each issue
5. **Reference Main Doc** - See `SECURITY_REVIEW_FINDINGS.md` for fix details

---

**Remember:** DO NOT deploy to production until Phase 1 and Phase 2 are complete!
