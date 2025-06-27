# 📝 Project Notes

## 🚧 TODOs

### Expansion
- [x] Newham parks Inclusion
- [ ] Southwark Parks inclusion
- [ ] Tower hamlets inclusion
- 

### Feature
- [ ] Taking 30 minutes logic into account due to Southwark park

### Code
- [ ] Implement logging
- [ ] Git feature branch, how does it work?

---

## 📌 Important Notes
### Known Issues

### Logging Notes
✅ **logger.debug() – For development & low-level internal info**
When to use:
- Inspecting variables
- Tracing loops or data transformations
- Verifying function inputs/outputs during debugging

✅ **logger.info() – For expected events and important steps**
When to use:
- Key steps in your workflow
- Confirmation that things are working as intended
- App startup/shutdown messages

**✅ logger.warning() – For recoverable issues that need attention**
When to use:
- An external API gives incomplete data
- A booking site is reachable, but missing expected fields
- A venue exists in your config but doesn’t return any sessions

**✅ logger.error() – For serious issues or exception**
When to use:
- API call failed
- JSON couldn't be parsed
- Date format is invalid and it halts logic


**✅ logger.critical() – For app-breaking problems**
When to use:
- Missing Configuration file
- Core data structure isn’t initialized
- Unrecoverable system error (e.g., can’t authenticate, file system unavailable)



---

## 🔍 References

---

_Last updated: June 26, 2025_